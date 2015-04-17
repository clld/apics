# coding=utf8
from io import open
import re
from subprocess import call
import logging
from collections import defaultdict
import uuid

from bs4 import BeautifulSoup, Tag
from path import path
import cssutils
from sqlalchemy import create_engine
from nameparser import HumanName

from clld.util import slug, jsondump, jsonload


db = create_engine('postgresql://robert@/apics')
LANGUAGES = {r[0]: r[1] for r in db.execute("select id, name from language")}
YEAR = re.compile('(\.|(?P<ed>\(ed(s?)\.\)(,?)))\s*(?P<year>((\[[0-9]+(,\s*[0-9]+)*\]\s+)?([0-9]{4}(–|/))?[0-9]{4}[a-z\+]?)|(n\.d))\.'.decode('utf8'))


def convert(fname, outdir):
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


#
# common parsing:
# - css extraction and normalization
# - removal of lang and xml:lang attributes
#
def normalize_whitespace(s, nbsp=False):
    if nbsp:
        s = re.sub(u'[\s\xa0]+', ' ', s, re.M)
    else:
        s = re.sub('\s+', ' ', s, re.M)
    return s.strip().replace('\n', ' ')


def text(e, nbsp=False):
    if not hasattr(e, 'strings'):
        res = unicode(e)
    else:
        res = ''.join([s for s in e.strings])
    return normalize_whitespace(res, nbsp=nbsp)


def children(e):
    return [t for t in e.contents if t.name]


class Parser(object):
    def __init__(self, fname):
        self.fname = fname
        self.id = self.get_id(fname)
        self.authors = [r[0] for r in db.execute("select id from contributor")]

    def __call__(self, outdir):
        """
        runs a parser workflow consisting of
        - preprocess
        - refactor
        - postprocess
        writes the results, an html and a css file to disk.
        """
        cssutils_logger = logging.getLogger('CSSUTILS')
        cssutils_logger.setLevel(logging.ERROR)
        print(self.fname.namebase.encode('utf8'))

        with open(self.fname, encoding='utf8') as fp:
            c = fp.read()
        soup = BeautifulSoup(self.preprocess(c))
        head = soup.find('head')
        css = cssutils.parseString("""
""")
        for style in head.find_all('style'):
            for rule in self.cssrules(style):
                css.add(rule)
        md = dict(outline=[], refs=[], authors=[])
        soup = self.refactor(soup, md)

        # enhance section headings:
        for section in soup.find_all('h3'):
            t = re.sub('\s+', ' ', section.get_text(' ', strip=True).strip())
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

        body = self.link_refs(unicode(soup.find('body')), md['refs'])
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

    def link_refs(self, html, refs):
        def repl(match):
            return '<a class="ref-link" style="cursor: pointer;" data-content="%s">%s</a>' \
                   % (slug(match.group('key').replace('&amp;', '&')), match.group('key'))

        for ref in refs:
            if ref['key']:
                html = re.sub('(?P<key>' + ref['key'].replace(' ', '\s+\(?').replace('&', '&amp;') + ')', repl, html, re.M)

        return html

    def preprocess(self, html):
        return html

    def postprocess(self, html):
        return html

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


class Paragraph(object):
    number_pattern = re.compile('\([0-9]+\)')
    number_language_ref_pattern = re.compile(
        '\((?P<no>[0-9]+)\)\s+(?P<lang>[^\(]+)(\((?P<ref>[^0-9]+[0-9]{4}([a-z])?(:\s*[0-9]+)?)\))?$')
    value_pattern = re.compile('[0-9]\.\s+[^\t]+\t[0-9]+$')
    header_pattern = re.compile('Chapter\s+[0-9]+$')

    def __init__(self, lines, refs=False):
        #if refs:
        #    print '\n'.join(l[1] for l in lines)
        self.lines = lines
        self.is_example = ('\t' in self.lines[0][1] and self.lines[0][2] == 'p') \
                          or self.number_language_ref_pattern.match(self.lines[0][1])
        if self.value_pattern.match(self.lines[0][1]):
            # entry in list of values for non-multiple valued feature
            self.is_example = False

        self.is_refs = refs
        self.is_header = self.header_pattern.match(self.lines[0][1])


class Atlas(Parser):
    BR = '----------'

    def get_id(self, fname):
        return fname.name.split('.')[0]

    def preprocess(self, html):
        for t, d in [
            ('<h3 ', '<p '),
            ('</h3>', '</p>'),
            ('<h1 ', '<p '),
            ('</h1>', '</p>'),
            # Special special case for 42:
            ('(2005e)).</span></p>',
             '(2005e)).</span></p>\n<p><br></p>\n<p>References</p>'),
            ('<br />', self.BR),
            ('<br>', self.BR),
        ]:
             html = html.replace(t, d)
        return html

    def postprocess(self, html):
        return html.replace(self.BR, '<br />')

    def refactor(self, soup, md):
        d = BeautifulSoup('<body></body>')
        body = d.find('body')
        for p in self._chunks(soup):
            if not isinstance(p, list):
                p = [p]
            for pp in p:
                if pp.is_header:
                    continue
                elif pp.is_refs:
                    md['refs'] = [self.get_ref(line[0]) for line in pp.lines]
                else:
                    if pp.is_example:
                        body.append(Tag(name='hr'))
                    for e, line, t in pp.lines:
                        body.append(e)
                    if pp.is_example:
                        body.append(Tag(name='hr'))
        return d

    def _paragraphs(self, soup):
        lines = []
        refs = False
        for e in soup.find_all(['p', 'table', 'ol', 'ul']):
            if e.name == 'table':
                print '--- the table ---'
            if e.parent.name in ['li', 'td']:
                continue

            t = text(e)
            if not t:
                continue
            #print t
            br = t == self.BR
            if t in ['References', 'Reference']:
                refs = True
                t = ''
            elif not lines and re.match('[0-9]+\.\s+[A-Za-z]+(\s+[A-Za-z]+)*$', t):
                e.name = 'h3'
            elif t.endswith('and the APiCS Consortium'):
                continue

            if br and not refs:
                if lines:
                    yield Paragraph(lines)
                    lines = []
            if t and t != self.BR:
                lines.append((e, t, e.name))

        if lines:
            yield Paragraph(lines, refs=refs)

    def _chunks(self, soup):
        example_group = []
        for p in self._paragraphs(soup):
            if p.is_example:
                example_group.append(p)
            else:
                if example_group:
                    yield example_group
                    example_group = []
                yield p


class Surveys(Parser):
    fname_pattern = re.compile('(?P<vol>I+)_(?P<no>[0-9]+)?_(?P<name>[^\._]+)')
    language_lookup = {slug(v): k for (k, v) in LANGUAGES.items()}

    headings = [
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
    heading_pattern = re.compile(
        '([0-9]+\.(?P<sub>[0-9]+\.?)?[\s\xa0]+)?(%s)$' % '|'.join(h.lower() for h in headings))

    def get_id(self, fname):
        match = self.fname_pattern.search(fname.name)
        assert match
        lid = self.language_lookup.get(slug(match.group('name')))
        if lid:
            return '%s.%s' % (lid, '%(vol)s-%(no)s' % match.groupdict())
        assert not match.group('no')
        return '%(vol)s-%(name)s' % match.groupdict()

    def preprocess(self, html):
        for s in ['<o:p>', '</o:p>', 'color:windowtext;']:
            html = html.replace(s, '')
        return html.replace('line-height:200%', 'line-height:150%')

    def postprocess(self, html):
        new = []
        pos = 0
        _number = 0
        soup = BeautifulSoup()

        def popover(number, note):
            note = BeautifulSoup(re.sub('\s+', ' ', note.strip(), re.M)).find('body')
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

        for match in re.finditer('\[Note\s+(?P<number>[0-9]+):\s*', html, re.M):
            new.append(html[pos:match.start()])
            level = 0
            closing_bracket = None
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

    def refactor(self, soup, md):
        """
        - Must parse authors!
        - must parse notes:
        [Note 1: ...]

        - problem: In pichi, I.19, the doc file contains references objects, referencing
          examples which are only implicitely numbered!
        """
        # clean style attributes:
        for e in soup.find('body').descendants:
            if not hasattr(e, 'attrs'):
                continue
            if e.attrs.get('style'):
                style = []
                for rule in e.attrs['style'].split(';'):
                    rule = rule.strip()
                    # tab-stops:14.2pt  text-indent:36.0pt
                    if rule in ['tab-stops:14.2pt', 'text-indent:36.0pt']:
                        rule = 'margin-top:0.4em'
                    if re.sub('\s+', '', rule, re.M) in ['font-family:Junicode']:
                        continue
                    if not rule.startswith('mso-'):
                        style.append(rule)
                if style:
                    e.attrs['style'] = ';'.join(style)
                else:
                    del e.attrs['style']
            if 'lang' in e.attrs:
                del e.attrs['lang']

        for p in soup.find_all('p'):
            # remove empty paragraphs:
            if not re.sub(u'[\s\xa0]', '', p.get_text(' ', strip=True), re.M):
                p.extract()
                continue

            if p.attrs.get('class') == ['Zitat']:
                p.wrap(soup.new_tag('blockquote'))
                continue

            if not p.parent.name == 'td':
                # need to detect headings by text, too!
                t = text(p)
                match = self.heading_pattern.match(t.lower())
                if match:
                    p.name = 'h4' if match.group('sub') else 'h3'

        for p in soup.find_all('h2'):
            if not re.sub(u'[\s\xa0]', '', p.get_text(' ', strip=True), re.M):
                p.extract()
            else:
                p.name = 'h4'
        for p in soup.find_all('h1'):
            if not re.sub(u'[\s\xa0]', '', p.get_text(' ', strip=True), re.M):
                p.extract()
            else:
                p.name = 'h3'

        for p in soup.find_all('a'):
            if p.attrs.get('name', '').startswith('OLE_LINK'):
                p.unwrap()

        top_level_elements = [e for e in soup.find('div').children if hasattr(e, 'name')]
        if '.' in self.id:
            if [e.name for e in top_level_elements[:4]] != ['p', 'p', 'table', 'h3']:
                raise ValueError
            for i, e in enumerate(top_level_elements[:3]):
                if i == 0:
                    md['title'] = text(e)
                if i == 1:
                    md['authors'] = [s for s in re.split(',|&| and ', text(e))]
                e.extract()
            #print(md.get('title'))
            #print(md.get('authors'))

        # TODO
        # - images/maps
        refs = None
        for h3 in soup.find_all('h3'):
            if text(h3).startswith('References'):
                refs = h3
                break

        if refs:
            ex = []
            category = None
            for e in refs.next_siblings:
                if hasattr(e, 'name'):
                    if not text(e):
                        ex.append(e)
                        continue
                    if e.name == 'p':
                        t = text(e, nbsp=True)
                        if not t:
                            pass
                        elif t in [
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
                        ]:
                            category = t
                        elif len(t.split()) < 3:
                            raise ValueError(t)
                        else:
                            if 'comment' in e.attrs.get('class', []):
                                if 'refs_comments' not in md:
                                    md['refs_comments'] = [t]
                                else:
                                    md['refs_comments'].append(t)
                            else:
                                if not YEAR.search(t):
                                    print t
                                md['refs'].append(self.get_ref(e, category=category))
                        ex.append(e)
                    elif e.name == 'h4':
                        category = text(e)
                        ex.append(e)
                    else:
                        raise ValueError(e.name)
            ex.append(refs)
            for e in ex:
                e.extract()

        #print(len(md['refs']) if md['refs'] else '#######')
        #print('--')

        for t in soup.find_all('table'):
            t.wrap(soup.new_tag('div', **{'class': 'table'}))

        return soup


def clean_dir(p):
    for f in p.files():
        f.remove()
    return p


def hash(authors, year, title):
    authors = [HumanName(n.strip()) for n in re.split('&|;', authors)]
    year = year.strip()
    if year[-1] in 'abc':
        year = year[:-1]
    return (authors[0].last, year, slug(title)[:15])


if __name__ == '__main__':
    import sys
    what, cmd = sys.argv[1:3]

    if cmd == 'convert':
        outdir = clean_dir(path(what).joinpath('lo'))
        if what == 'Atlas':
            for p in path(what).joinpath('in').files():
                if p.ext in ['.doc', '.docx']:
                    convert(p, outdir)
        elif what == 'Surveys':
            for p in path(what).joinpath('HTML').files():
                if p.ext in ['.htm']:
                    with open(
                            outdir.joinpath(p.namebase + '.html'),
                            'w',
                            encoding='utf8') as fp:
                        try:
                            c = open(p, 'rb').read()
                            enc = 'utf8'
                            if 'charset=macintosh' in c:
                                c = c.replace('charset=macintosh', 'charset=utf-8', 1)
                                enc = 'macroman'
                            elif 'charset=windows-1252' in c:
                                c = c.replace('charset=windows-1252', 'charset=utf-8', 1)
                                enc = 'windows-1252'
                            fp.write(c.decode(enc))
                        except:
                            print(p)
                            raise
    if cmd == 'parse':
        outdir = clean_dir(path(what).joinpath('processed'))
        for p in path(what).joinpath('lo').files():
            if (len(sys.argv) > 3 and sys.argv[3] in p.namebase) or len(sys.argv) <= 3:
                locals()[what](p)(outdir)
    if cmd == 'refs':
        refs = []
        for p in path(what).joinpath('processed').files('*.json'):
            md = jsonload(p)
            refs.extend([r[1] for r in md['refs']])
        refs = sorted(list(set(refs)))
        matched = defaultdict(list)
        unmatched = 0
        for ref in refs:
            match = YEAR.search(ref)
            if match:
                author = ref[:match.start()].strip() + (' (ed.)' if match.group('ed') else '')
                authors = [HumanName(n.strip()) for n in author.split('&')]
                year = match.group('year').strip()
                if year[-1] in 'abcdef':
                    year = year[:-1]
                title = ref[match.end():].strip().split('.')[0]
                matched[(authors[0].last, year, slug(title)[:15])].append(ref)
            else:
                unmatched += 1
                print '---', ref
        dbrefs = {}
        for row in db.execute("select author, year, title from source"):
            if row[0] and row[1] and row[2]:
                dbrefs[hash(*row)] = 1
        found = 0
        for t in sorted(matched.keys()):
            if t in dbrefs:
                found += 1
            else:
                print len(matched[t]), '%s\t%s\t%s' % t
        print len(matched)
        print found
        print unmatched
