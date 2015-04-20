# coding=utf8
from io import open
from subprocess import call
import logging
import re
import uuid

from bs4 import BeautifulSoup
import cssutils
from nameparser import HumanName

from clld.util import slug, jsondump
from clld.db.meta import DBSession
from clld.db.models.common import Contributor, Language, Source


NAME = '[A-Z][a-zê]'.decode('utf8')
YEAR = re.compile('(\.|(?P<ed>\(ed(s?)\.\)(,?)))\s*(?P<year>((\[[0-9]+(,\s*[0-9]+)*\]\s+)?([0-9]{4}(–|/))?[0-9]{4}[a-z\+]?)|(n\.d))\.'.decode('utf8'))

SURVEY_SECTIONS = [
    'Historical background',
    'Sociohistorical background',
    'Verb phrase',
    'Verb phrase and related categories',
    'Noun phrase',
    'The noun phrase',
    'Sentences',
    'Simple sentences',
    'Sociolinguistic situation',
    'Sociolinguistic background',
    'Introduction',
    'Phonology',
    'Complex sentences',
    'Complex sentences and their introducers',
    'Other features',
    'The lexicon',
    'The quotative particle',
    'Lexicon',
    'Genders',
    'Morphology',
    'Interrogative constructions',
    'Focus constructions',
    'Interrogative and focus constructions',
    'Interrogative sentences and focus constructions',
    'References',
    'Glossed Text',
    'Glossed text',
    'Glossed texts',
    'Acknowledgements',
    'Acknowledgement',
    'References and further reading',
    'Sources of examples',
    'Verb complex',
    'Adverbs',
    'Vowels',
    'Consonants',
    'Suprasegmentals',
    'Pronouns',
    'The relative pronoun ki',
    'Nouns',
    'Adjectives',
    'Preverbs, adverbs, and prepositions',
]

REFERENCE_CATEGORIES = [
    'Text',
    'Texts',
    'Grammatical description',
    'Grammatical descriptions',
    'Text/corpus',
    'Texts/corpora',
    'Texts/Corpora',
    'Grammar',
    'Grammars',
    'Dictionary',
    'Dictionaries',
    'Other',
    'Linguistic atlas',
    'Teaching manuals',
    'Further references',
    'Further reading',
    'History',
    'Special topics',
    'Grammars and dictionaries',
    'Articles and books',
    'Books and articles',
    'Dictionaries and handbooks',
    'Grammars and surveys',
    'Specific topics in grammar',
    'Berbice Dutch origins',
    'Other references cited',
    'Topics in Grammar',
    'Grammars and sketches',
]


def convert_chapter(fname, outdir):
    call('unoconv -f html -o %s "%s"' % (outdir, fname), shell=True)
    out = outdir.joinpath(fname.basename().splitext()[0] + '.html')
    lines = []
    with open(out, encoding='utf8') as fp:
        for line in fp:
            if '<sdfield' not in line:
                lines.append(line)
    with open(out, 'w', encoding='utf8') as fp:
        fp.write('\n'.join(lines))
    call('tidy -q -m -c -utf8 -asxhtml %s' % out, shell=True)


def normalize_whitespace(s, nbsp=False, repl=' '):
    if nbsp:
        s = re.sub(u'[\s\xa0]+', repl, s, re.M)
    else:
        s = re.sub('\s+', repl, s, re.M)
    return s.strip().replace('\n', ' ')


def text(e, nbsp=False):
    if not hasattr(e, 'strings'):
        res = unicode(e)
    else:
        res = ''.join([s for s in e.strings])
    return normalize_whitespace(res, nbsp=nbsp)


def is_empty(e, nbsp=True):
    return not text(e, nbsp=nbsp).strip()


def _tags(collection):
    return [t for t in collection if hasattr(t, 'name')]


def descendants(e):
    return _tags(e.descendants)


def children(e):
    return _tags(e.children)


def next_siblings(e):
    return _tags(e.next_siblings)


class Parser(object):
    def __init__(self, fname):
        self.fname = fname
        self.authors = [c.id for c in DBSession.query(Contributor)]
        self.languages = {l.id: l.name for l in DBSession.query(Language)}
        self.id = self.get_id(fname)
        self.refs = {slug(s.name): s for s in DBSession.query(Source) if s.name}

    def __call__(self, outdir):
        """
        runs a parser workflow consisting of
        - preprocess
        - refactor
        - postprocess
        writes the results, an html, a css and a json file to disk.
        """
        cssutils_logger = logging.getLogger('CSSUTILS')
        cssutils_logger.setLevel(logging.ERROR)
        print(self.fname.namebase.encode('utf8'))

        with open(self.fname, encoding='utf8') as fp:
            c = fp.read()
        soup = BeautifulSoup(self.preprocess(c))

        # extract css from the head section of the HTML doc:
        css = cssutils.parseString('\n')
        for style in soup.find('head').find_all('style'):
            for rule in self.cssrules(style):
                css.add(rule)

        md = dict(outline=[], refs=[], authors=[])
        soup = self.refactor(soup, md)

        # enhance section headings:
        for section in soup.find_all('h3'):
            t = text(section, nbsp=True)
            if t:
                t = t.split('[Note')[0]
                id_ = 'section-%s' % slug(t)
                md['outline'].append((t, id_))
                section.attrs['id'] = id_
                for s, attrs in [
                    (u'\u21eb', {'href': '#top', 'title': 'go to top of the page', 'style': 'vertical-align: bottom'}),
                    ('¶', {'class': 'headerlink', 'href': '#' + id_, 'title': 'Permalink to this section'}),
                ]:
                    section.append(soup.new_string('\n'))
                    a = soup.new_tag("a", **attrs)
                    a.string = s
                    section.append(a)

        #
        # TODO: link "§<no>" to sections!
        #

        body = self.insert_links(unicode(soup.find('body')), md)

        # write output files:
        with open(outdir.joinpath('%s.html' % self.id), 'w', encoding='utf8') as fp:
            fp.write(self.wrap(self.postprocess(body)))

        with open(outdir.joinpath('%s.css' % self.id), 'wb') as fp:
            fp.write(self.csstext(css))

        md['authors'] = list(self.yield_valid_authors(md['authors']))
        jsondump(md, outdir.joinpath('%s.json' % self.id), indent=4)

    def yield_valid_authors(self, authors):
        for name in authors:
            n = HumanName(name)
            res = dict(name=name, id=slug(n.last + n.first + n.middle))
            if name == 'Margot C. van den Berg':
                res['id'] = 'vandenbergmargotc'
            if name == 'Khin Khin Aye':
                res['id'] = 'khinkhinayenone'
            if name == 'Melanie Halpap':
                res['id'] = 'revismelanie'
            if res['id'] not in self.authors:
                raise ValueError(name)
            yield res

    def get_ref(self, e, category=None):
        t = text(e, nbsp=True)
        ref = self.refs.get(slug(t))
        if ref:
            return dict(
                key=ref.name,
                id=slug(t),
                text='%s. %s.' % (ref.name, ref.description),
                html=u'<a href="/sources/{0.id}">{0.name}</a>. {0.description}.'.format(ref),
                category=category)
        match = YEAR.search(t)
        if match:
            authors = t[:match.start()].split('(')[0].strip()
            authors = [HumanName(n.strip()).last for n in authors.split('&')]
            key = '%s %s' % (' & '.join(authors), match.group('year').strip())
        else:
            key = None
        return dict(
            key=key,
            id=slug(key) if key else uuid.uuid4().hex,
            text=t,
            html=unicode(e),
            category=category)

    def insert_links(self, html, md):
        def repl(match):
            return '<a class="ref-link" style="cursor: pointer;" data-content="%s">%s</a>' \
                   % (slug(match.group('key').replace('&amp;', '&')), match.group('key'))

        ids = {}
        for ref in md['refs']:
            if ref['key']:
                ids[ref['id']] = 1
                html = re.sub('(?P<key>' + ref['key'].replace(' ', '\s+\(?').replace('&', '&amp;') + ')', repl, html, flags=re.M)

        def repl2(match):
            s = match.string[match.start():match.end()]
            id_ = slug(match.group('key').replace('&amp;', '&'))
            ref = self.refs.get(id_)
            if not ref or id_ in ids:
                return s
            return '%s<a href="/sources/%s">%s</a>%s' \
                   % (match.group('before'), ref.id, match.group('key'), match.group('after'))

        html = re.sub('(?P<before>\(|>)(?P<key>' + NAME + '\s+(&\s+' + NAME + '\s+)*[0-9]{4})(?P<after><|\)|:)', repl2, html, flags=re.M)

        section_lookup = {}
        for t, id_ in md['outline']:
            m = re.match('(?P<no>[0-9]+(\.[0-9]+)?)\.\s+', t)
            if m:
                section_lookup[m.group('no')] = id_

        def repl3(match):
            return '<a class="section-link" href="#%s">§%s</a>'.decode('utf8') \
                   % (section_lookup[match.group('no')], match.group('no'))

        for no in section_lookup:
            html = re.sub('§(</span><span>)(?P<no>'.decode('utf8') + no.replace('.', '\\.') + ')', repl3, html, flags=re.M)

        lookup = {v: k for k, v in self.languages.items()}

        def langs(match):
            name = normalize_whitespace(match.group('name'))
            return '<a href="/contributions/%s">%s</a>' % (lookup[name], name)
        for name in lookup:
            html = re.sub('(?P<name>' + name.replace(' ', '\s+') + ')', langs, html, flags=re.M)
        return html

    def preprocess(self, html):
        return html

    def postprocess(self, html):
        new = []
        pos = 0
        _number = 0
        soup = BeautifulSoup()

        def popover(number, note):
            # we use BeautifulSoup to fix broken markup, e.g. incomplete span tags.
            note = BeautifulSoup(normalize_whitespace(note)).find('body')
            note = unicode(note).replace('body>', 'div>')
            a = soup.new_tag(
                'a',
                **{
                    'style': 'text-decoration: underline; cursor: pointer;',
                    'class': 'popover-note',
                    'data-original-title': 'Note %s' % number,
                    'data-content': note,
                    })
            sup = soup.new_tag('sup')
            sup.string = number
            a.append(sup)
            return unicode(a)

        for match in re.finditer('\[Note\s+(?P<number>[0-9]+):\s*', html, flags=re.M):
            new.append(html[pos:match.start()])
            level = 0
            for i, c in enumerate(html[match.end():]):
                if c == '[':
                    level += 1
                if c == ']':
                    if level == 0:
                        closing_bracket = match.end() + i
                        break
                    level -= 1
            else:
                raise ValueError(match.group('number'))
            _number += 1
            if int(match.group('number')) != _number:
                print '--- missing note %s' % _number
            _number = int(match.group('number'))

            new.append(popover(match.group('number'), html[match.end():closing_bracket]))
            pos = closing_bracket + 1

        new.append(html[pos:])
        return ''.join(new)

    def wrap(self, html):
        html = re.sub(' (xml:)?lang="[a-z]{2}\-[A-Z]{2}"', '', html).replace('</body>', '')
        return """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" type="text/css" href="%s.css">
        <script src="http://code.jquery.com/jquery.js"></script>
        <link href="http://maxcdn.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap-combined.min.css" rel="stylesheet">
        <script src="http://maxcdn.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"></script>
    </head>
    %s
        <script>
            $(document).ready(function(){
                $('.popover-note').popover({html: true});
            });
        </script>
    </body>
</html>
    """ % (self.id, html)

    def get_id(self, fname):
        return fname.namebase

    def refactor(self, soup, md):
        return soup

    def cssrules(self, style):
        res = text(style)
        for s in ['/*<![CDATA[*/', '<!--', '/*]]>*/', '-->']:
            res = res.replace(s, '')
        res = re.sub('/\*[^\*]+\*/', '', res)
        res = re.sub('mso\-[^\:]+\:[^;]+;', '', res)
        for rule in [r.strip() + '}' for r in res.strip().split('}') if r]:
            selector = rule.split('{')[0]
            if not rule.startswith('@page') \
                    and ':' not in selector \
                    and not re.search('\.[0-9]+', selector):
                yield rule

    def csstext(self, css):
        lines = []
        for line in css.cssText.split('\n'):
            if ':' in line:
                selector, rule = line.strip().split(':', 1)
                if selector in [
                    'font-family',
                    'line-height',
                    'font-size',
                    'so-language',
                    'margin-left',
                    'margin-right',
                    'direction',
                    'color',
                ]:
                    continue
                if 'mso-' in rule:
                    continue
            lines.append(line)
        css = cssutils.parseString('\n'.join(lines))
        return css.cssText
