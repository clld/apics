# -*- coding: utf-8 -*-
from clld.db.meta import DBSession
from clld.db.models.common import Parameter
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import map_marker_img
from clld.lib import bibtex

from apics.models import Feature


# see http://en.wikipedia.org/wiki/BibTeX
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


def value_table(ctx, req):
    rows = []
    langs = {}

    for de in ctx.domain:
        exclusive = 0
        shared = 0

        for v in [_v for _v in de.values if not _v.valueset.language.language_pk]:
            if len(v.valueset.values) > 1:
                shared += 1
            else:
                exclusive += 1
            langs[v.valueset.language_pk] = 1

        cells = [
            HTML.td(map_marker_img(req, de)),
            HTML.td(literal(de.name)),
            HTML.td(str(exclusive), class_='right'),
        ]
        if ctx.multivalued:
            cells.append(HTML.td(str(shared), class_='right'))
            cells.append(HTML.td(str(exclusive + shared), class_='right'))

        rows.append(HTML.tr(*cells))
    rows.append(HTML.tr(
        HTML.td('Representation:', colspan=str(len(cells) - 1), class_='right'),
        HTML.td('%s' % len(langs), class_='right')))

    parts = []
    if ctx.multivalued:
        parts.append(HTML.thead(
            HTML.tr(*[HTML.th(s) for s in [' ', ' ', 'excl.', 'shrd.', 'all']])))
    parts.append(HTML.tbody(*rows))

    return HTML.table(*parts, class_='table table-condensed')


def segments(language):
    existing = dict(
        (v.parameter.id, v.values[0].domainelement.name)
        for v in language.valuesets if v.parameter.feature_type == 'segment' and v.values)

    class_map = {
        'Exists (as a major allophone)': 'major',
        'Does not exist': 'inexistent',
        'Exists only as a minor allophone': 'minor',
        'Exists only in loanwords': 'loan',
    }

    class_ = lambda id_: 'segment ' + class_map.get(
        existing.get(id_, 'Does not exist'), 'inexistent')

    return dict(
        (sm.jsondata['number'], (
            '%s - %s' % (sm.name, existing.get(sm.id, 'Does not exist')),
            sm.jsondata['symbol'],
            class_(sm.id),
            sm,
            existing.get(sm.id, 'Does not exist') != 'Does not exist'))
        for sm in DBSession.query(Parameter).filter(Feature.feature_type == 'segment'))


def ipa_custom(segments):
    rows = []
    for i, data in segments.items():
        title, symbol, class_, param, exists = data
        if exists and param and (not param.jsondata['core_list'] or i in [15, 74, 77, 84]):
            rows.append(HTML.tr(
                HTML.td(literal(symbol), title=title, class_=class_),
                HTML.th(title.split('-')[1].strip(), style="padding-left: 10px; text-align: left;"),
            ))
    return HTML.table(HTML.tbody(*rows))


def ipa_consonants(segments):
    row_specs = [
        (
            'Plosive / affricate',
            {1: 1, 2: 5, 7: 7, 8: 9, 9: 24, 10: 80, 11: 25, 12: 27, 13: 11, 14: 12,
             15: 13, 16: 14, 17: 2, 18: 17, 19: 75, 20: 76, 21: 18, 22: 19}
        ),
        ('Aspirated plosive / affricate', {1: 4, 7: 8, 8: 6, 9: 79, 11: 26, 17: 16}),
        (
            'Glottalized stop / affricate',
            {1: 20, 2: 23, 7: 21, 9: 81, 11: 28, 17: 22, 21: 78}
        ),
        ('Nasal', {2: 42, 8: 43, 14: 44, 16: 45, 18 :46}),
        ('Trill, Tap or Flap', {7: 47, 8: 48}),
        (
            'Fricative',
            {
                1: 29, 2: 30, 3: 31, 4: 32, 5: 82, 6: 33,
                7: 34, 8: 35, 11: 36, 12: 37, 17: 38, 18: 39, 21: 40, 22: 41}
        ),
        ('Lateral / approximant', {7: 85, 8: 49, 14: 50, 16: 51, 20: 52}),
    ]

    rows = []
    for i, spec in enumerate(row_specs):
        m = i + 1
        name, segment_map = spec
        cells = [HTML.th(name, class_="row-header")]
        for j in range(22):
            if j + 1 in segment_map:
                title, symbol, class_, p, exists = segments[segment_map[j + 1]]
                cells.append(HTML.td(symbol, title=title, class_=class_))
            else:
                cells.append(HTML.td())
        rows.append(HTML.tr(*cells))

    return HTML.table(
        HTML.thead(
            HTML.tr(
                HTML.td(''),
                HTML.th(HTML.div('Bilabial', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Labiodental', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Dental', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Dental/Alveolar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Dental/Alveolar', HTML.br(), 'affricate', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Palato-alveolar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Retroflex', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Palatal', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Velar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Labial-velar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('Uvular', class_="vertical")),
                HTML.th(HTML.div('Glottal', class_="vertical")),
            ),
        ),
        HTML.tbody(*rows),
        style="margin-top: 5em;",
    )


def ipa_vowels(segments):
    segments[0] = ('separator', u'•', 'segment-separator', None, False)

    div_specs = [
        # high
        (4, -29, 125, [87, 54, 53, 0, 55, 88]),
        (4, 135, 60, [62, 0]),
        (4, 264, 110, [66, 0, 67, 68, 93]),
        # lowered high
        (35, 80, 60, [56, 0]),
        (35, 221, 60, [0, 69]),

        # higher mid
        (71, 12, 90, [89, 58, 57, 0]),
        (71, 283, 90, [0, 70, 71, 94]),

        # mid
        (98, 182, 60, [63]),

        # lower mid
        (135, 55, 90, [90, 60, 59, 0]),
        (135, 282, 90, [0, 72, 86, 95]),

        # raised low
        (166, 96, 60, [91, 61, 0]),

        # low
        (198, 100, 90, [92, 65, 64, 0]),
        (198, 247, 60, [96, 73, 0]),
    ]

    divs = [
        HTML.div(
            *[HTML.span(symbol, class_=class_, title=name)
              for name, symbol, class_, param, exists
              in [segments[i] for i in content]],
            style="top:%spx; left:%spx; width:%spx;" % (top, left, width),
            class_='segment-container')
        for top, left, width, content in div_specs]

    def wm_url(path):
        return '//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/'\
            'Blank_vowel_trapezoid.svg' + path

    diagram = HTML.div(
        HTML.img(
            height="224", width="320", alt="Blank vowel trapezoid.svg",
            src=wm_url("/320px-Blank_vowel_trapezoid.svg.png"),
            srcset=', '.join([
                wm_url('/480px-Blank_vowel_trapezoid.svg.png 1.5x'),
                wm_url('/640px-Blank_vowel_trapezoid.svg.png 2x')]),
        ),
        HTML.div(
            HTML.table(
                HTML.tbody(HTML.tr(HTML.td(*divs))),
                style="position:relative; width:320px; height:224px; text-align:center; "
                "background:transparent; font-size:131%;",
            ),
            style="background:transparent; position:absolute; top:0px; left:0px;",
        ),
        style="position:relative;",
    )

    return HTML.table(
        HTML.tbody(
            HTML.tr(
                HTML.td(' '),
                HTML.td(
                    HTML.span('Front', style="position:relative; left:-0.4em;"),
                    style="width:64px;"),
                HTML.td(
                    'Near-front',
                    style="width:62px;"),
                HTML.td(
                    'Central',
                    style="width:64px;"),
                HTML.td(
                    'Near-back',
                    style="width:62px;"),
                HTML.td(
                    'Back',
                    style="width:64px;"),
                style="text-align: center;",
            ),
            HTML.tr(
                HTML.td('High', style="height:32px; text-align:right;"),
                HTML.td(
                    diagram,
                    style="height:210px; padding-left: 30px;", colspan="5", rowspan="7"),
            ),
            HTML.tr(HTML.td('', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td('Higher-mid', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td('Mid', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td('Lower-mid', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td('', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td('Low', style="height:32px; text-align:right;")),
        ),
        style="line-height:1.4em; background:transparent; margin:0em auto 0em auto;",
        cellspacing="0")
