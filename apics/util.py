# -*- coding: utf-8 -*-
from clld.db.meta import DBSession
from clld.db.models.common import Parameter
from clld.web.util.htmllib import HTML
from clld.lib import bibtex


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


def ipa_consonants(language):
    row_specs = [
        (
            'Plosive / affricate',
            {
                1: 1,
                2: 5,
                7: 7,
                8: 9,
                9: 24,
                10: 80,
                11: 25,
                12: 27,
                13: 11,
                14: 12,
                15: 13,
                16: 14,
                17: 2,
                18: 17,
                19: 75,
                20: 76,
                21: 18,
                22: 19,
            }
        ),
        (
            'Aspirated plosive / affricate',
            {
                1: 4,
                7: 8,
                8: 6,
                9: 79,
                11: 26,
                17: 16,
            }
        ),
        (
            'Glottalized stop / affricate',
            {
                1: 20,
                2: 23,
                7: 21,
                9: 81,
                11: 28,
                17: 22,
                21: 78,
            }
        ),
        (
            'Nasal',
            {
                2: 42,
                8: 43,
                14: 44,
                16: 45,
                18 :46,
           }
        ),
        (
            'Trill, Tap or Flap',
            {
                7: 47,
                8: 48,
            }
        ),
        (
            'Fricative',
            {
                1: 29,
                2: 30,
                3: 31,
                4: 32,
                5: 82,
                6: 33,
                7: 34,
                8: 35,
                11: 36,
                12: 37,
                17: 38,
                18: 39,
                21: 40,
                22: 41,
            }
        ),
        (
            'Lateral / approximant',
            {
                7: 85,
                8: 49,
                14: 50,
                16: 51,
                20: 52,
            }
        ),
    ]

    existing = dict(
        (v.parameter.id, v.values[0].domainelement.name)
        for v in language.valuesets
        if v.parameter.feature_type == 'segment' and v.parameter.jsondata['consonant']
        and v.parameter.jsondata['core_list'] and v.values)

    class_map = {
        'Exists (as a major allophone)': 'major',
        'Does not exist': 'inexistent',
        'Exists only as a minor allophone': 'minor',
        'Exists only in loanwords': 'loan',
    }

    class_ = lambda id_: 'segment ' + class_map.get(
        existing.get(id_, 'Does not exist'), 'inexistent')

    segments = dict(
        (sm.id, (sm.name, sm.jsondata['symbol'], class_(sm.id)))
        for sm in DBSession.query(Parameter).filter(Parameter.id.contains('sm-'))
        if sm.jsondata['core_list'] and sm.jsondata['consonant'])

    rows = []
    for i, spec in enumerate(row_specs):
        m = i + 1
        name, segment_map = spec
        cells = [HTML.th(name)]
        for j in range(22):
            if j + 1 in segment_map:
                title, symbol, class_ = segments['sm-%s' % segment_map[j + 1]]
                cells.append(HTML.td(symbol, title=title, class_=class_))
            else:
                cells.append(HTML.td())
        rows.append(HTML.tr(*cells))

    return HTML.table(
        HTML.thead(
            HTML.tr(
                HTML.td(''),
                HTML.th('b', title='Bilabial', colspan="2"),
                HTML.th('ld', title='Labiodental', colspan="2"),
                HTML.th('d', title='Dental', colspan="2"),
                HTML.th('d/a', title='Dental/Alveolar', colspan="2"),
                HTML.th('d/a af', title='Dental/Alveolar affricate', colspan="2"),
                HTML.th('p-a', title='Palato-alveolar', colspan="2"),
                HTML.th('r', title='Retroflex', colspan="2"),
                HTML.th('p', title='Palatal', colspan="2"),
                HTML.th('v', title='Velar', colspan="2"),
                HTML.th('l-v', title='Labial-velar', colspan="2"),
                HTML.th('u', title='Uvular'),
                HTML.th('g', title='Glottal'),
            ),
        ),
        HTML.tbody(*rows),
    )



def ipa_vowels(language):
    existing_vowels = dict(
        (v.parameter.id, v.values[0].domainelement.name)
        for v in language.valuesets
        if v.parameter.feature_type == 'segment' and v.parameter.jsondata['vowel']
        and v.parameter.jsondata['core_list'] and v.values)

    class_map = {
        'Exists (as a major allophone)': 'major',
        'Does not exist': 'inexistent',
        'Exists only as a minor allophone': 'minor',
        'Exists only in loanwords': 'loan',
    }
    class_ = lambda id_: 'segment ' + class_map.get(
        existing_vowels.get(id_, 'Does not exist'), 'inexistent')

    vowels = dict(
        (sm.id, (sm.name, sm.jsondata['symbol'], class_(sm.id)))
        for sm in DBSession.query(Parameter).filter(Parameter.id.contains('sm-'))
        if sm.jsondata['core_list'] and sm.jsondata['vowel'])
    vowels['sm-0'] = ('separator', u'•', 'segment-separator')

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
              for name, symbol, class_ in [vowels['sm-%s' % i] for i in content]],
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
