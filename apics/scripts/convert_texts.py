# coding: utf8
from collections import defaultdict
import re
from uuid import uuid4
from itertools import combinations, groupby

from fuzzywuzzy import fuzz

from clld.scripts.util import parsed_args
from clld.util import jsondump, jsonload, slug

from apics.scripts.convert_util import (
    convert_chapter, Parser, text, SURVEY_SECTIONS, REFERENCE_CATEGORIES, is_empty,
    next_siblings, children, descendants, normalize_whitespace, YEAR, get_bibtex,
)


class Surveys(Parser):
    fname_pattern = re.compile('(?P<vol>I+)_(?P<no>[0-9]+)?_(?P<name>[^\._]+)')

    headings = SURVEY_SECTIONS
    heading_pattern = re.compile(
        '([0-9]+\.(?P<sub>[0-9]+\.?)?[\s\xa0]+)?(%s)$' % '|'.join(h.lower() for h in headings))
    _language_lookup = None

    @property
    def language_lookup(self):
        if not self._language_lookup:
            self._language_lookup = {slug(v): k for (k, v) in self.languages.items()}
        return self._language_lookup

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
        html = re.sub('line\-height:\s*200%', 'line-height:150%', html, flags=re.M)
        return re.sub('font\-size:\s*12\.0pt;?', '', html, flags=re.M)

    def refactor(self, soup, md):
        """
        - Must parse authors!
        - must parse notes:
        [Note 1: ...]

        - problem: In pichi, I.19, the doc file contains references objects, referencing
          examples which are only implicitely numbered!
        """
        # clean style attributes:
        for e in descendants(soup.find('body')):
            if e.name in ['p', 'h1', 'h2'] and is_empty(e):
                e.extract()
                continue

            if e.attrs.get('style'):
                style = []
                for rule in e.attrs['style'].split(';'):
                    rule = rule.strip()
                    # tab-stops:14.2pt  text-indent:36.0pt
                    if rule in ['tab-stops:14.2pt', 'text-indent:36.0pt']:
                        rule = 'margin-top:0.4em'
                    if normalize_whitespace(rule, repl='') in [
                        'font-family:Junicode',
                        'font-family:JunicodeRegular',
                    ]:
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
            if p.attrs.get('class') == ['Zitat']:
                p.wrap(soup.new_tag('blockquote'))
                continue

            if not p.parent.name == 'td':
                # need to detect headings by text, too!
                t = text(p)
                match = self.heading_pattern.match(t.lower())
                if match:
                    p.name = 'h2' if match.group('sub') else 'h1'

        # re-classify section headings:
        for i in range(1, 3):
            for p in soup.find_all('h%s' % i):
                p.name = 'h%s' % (i + 1,)

        for p in soup.find_all('a'):
            if p.attrs.get('name', '').startswith('OLE_LINK'):
                p.unwrap()

        top_level_elements = children(soup.find('div'))
        if '.' in self.id:
            try:
                assert [e.name for e in top_level_elements[:4]] == ['p', 'p', 'table', 'h3']
            except:
                print [e.name for e in top_level_elements[:4]]
                raise
            for i, e in enumerate(top_level_elements[:3]):
                if i == 0:
                    md['title'] = text(e)
                if i == 1:
                    md['authors'] = [s for s in re.split(',|&| and ', text(e))]
                e.extract()

        refs = None
        for h3 in soup.find_all('h3'):
            if text(h3).startswith('References'):
                refs = h3
                break

        if refs:
            ex = []
            category = None
            for e in next_siblings(refs):
                t = text(e, nbsp=True)
                if not t:
                    ex.append(e)
                    continue
                if e.name == 'p':
                    if t in REFERENCE_CATEGORIES:
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
                elif e.name in ['h3', 'h4']:
                    category = t
                    ex.append(e)
                else:
                    print(t)
                    raise ValueError(e.name)
            ex.append(refs)
            for e in ex:
                e.extract()

        for t in soup.find_all('table'):
            t.wrap(soup.new_tag('div', **{'class': 'table'}))

        return soup


def main(args):
    if args.cmd == 'convert':
        outdir = args.data_file('texts', args.what).joinpath('lo')
        if args.what == 'Atlas':
            for p in args.data_file('texts', args.what).joinpath('in').files():
                if p.ext in ['.doc', '.docx']:
                    convert_chapter(p, outdir)
        elif args.what == 'Surveys':
            pass
    if args.cmd == 'parse':
        outdir = args.data_file('texts', args.what).joinpath('processed')
        for p in args.data_file('texts', args.what).joinpath('lo').files():
            if args.in_name in p.namebase:
                globals()[args.what](p)(outdir)
    if args.cmd == 'refs':
        refs = []
        for p in args.data_file('texts', args.what).joinpath('processed').files('*.json'):
            if args.in_name in p.namebase:
                md = jsonload(p)
                refs.extend(md['refs'])
        db = get_bibtex(refs)
        unmatched = 0
        distinct = defaultdict(list)
        for i, rec in enumerate(db):
            if 'all' in rec:
                unmatched += 1
            distinct[(
                slug(rec.get('key', unicode(uuid4().hex))),
                slug(unicode(rec.get('title', uuid4().hex)), remove_whitespace=False)
            )] = 1
        print unmatched, 'of', i, 'distinct', len(distinct)

        c = 0
        for key, refs in groupby(sorted(distinct.keys()), key=lambda t: t[0]):
            refs = list(refs)
            if len(refs) > 1:
                for t1, t2 in combinations([t[1] for t in refs], 2):
                    if fuzz.partial_ratio(t1, t2) > 80:
                        print t1
                        print t2
                        print
                        c += 1
        print c
        return


if __name__ == '__main__':
    main(parsed_args(
        (("what",), dict()),
        (("cmd",), dict()),
        (("--in-name",), dict(default='')),
    ))
