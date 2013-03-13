from clld.web.util.htmllib import HTML
from clld.lib import bibtex


BIBTEX_MAP = {
    'Volume': 'volume',
    'School': 'school',
    'Additional_information': 'note',
    'Issue': 'issue',
    'Book_title': 'booktitle',
    'City': 'address',
    'Editors': 'editor',
    'Article_title': 'title',
    'URL': 'url',
    'Series_title': 'series',
    'Pages': 'pages',
    'Journal': 'journal',
    'Publisher': 'publisher',
}


def format_source(source, fmt=None):
    rec = source.datadict()
    if fmt == 'bibtex':
        return HTML.pre(bibtex.Record(
            rec.get('BibTeX_type', 'misc'),
            source.id,
            author=source.authors,
            year=source.year,
            **dict((BIBTEX_MAP[k], v) for k, v in rec.items() if k in BIBTEX_MAP)
        ))
    return rec.get('Full_reference', '%s. %s' % (source.name, source.description))
