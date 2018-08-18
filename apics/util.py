# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from base64 import b64encode

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import and_, null
from clldutils.path import Path, read_text
from clldutils import jsonlib
from bs4 import BeautifulSoup as bs
from clld.db.meta import DBSession
from clld.db.models.common import (
    Parameter,
    ValueSet,
    Contributor,
    Contribution,
)
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import map_marker_img, get_adapter, external_link
from clld.interfaces import IRepresentation, IIcon
from clld import RESOURCES
from clldmpg import cdstar

import apics
from apics.models import Feature, Lect
from apics.maps import WalsMap, ApicsWalsMap


assert cdstar


def text_path(what, *comps):
    return Path(apics.__file__).parent.joinpath('static', what, *comps)


def get_text(what, id_, fmt):
    p = text_path(what, '{0}.{1}'.format(id_, fmt))
    if not p.exists():
        raise ValueError(p)
    if fmt == 'json':
        return jsonlib.load(p)
    text = read_text(p)
    if fmt == 'css':
        return text
    body = bs(text).find('body')
    body.name = 'div'
    body.attrs.clear()
    return '{0}'.format(body).replace('.popover(', '.clickover(')


def replace_icons(text):
    return re.sub(
        '/static/icons/(?P<fname>[^.]+)\.png',
        lambda m: apics.ApicsMapMarker.pie_from_filename(m.group('fname')),
        text)


def get_data_uri(p, mimetype='image/png'):
    return 'data:{0};base64,{1}'.format(mimetype, b64encode(p.open('rb').read()))


def survey_detail_html(context=None, request=None, **kw):
    md = get_text('Surveys', context.id, 'json')
    html = get_text('Surveys', context.id, 'html')
    maps = []
    for fname in sorted(text_path('Surveys').glob('%s-*.png' % context.id), key=lambda p: p.stem):
        data_uri = get_data_uri(fname)
        if 'figure' in fname.stem:
            html = html.replace('{%s}' % fname.name, '%s' % data_uri)
        else:
            maps.append(data_uri)

    return {
        'maps': maps,
        'md': md,
        'html': html,
        'css': get_text('Surveys', context.id, 'css'),
    }


def wals_detail_html(context=None, request=None, **kw):
    wals_data = Path(apics.__file__).parent.joinpath(
        'static', 'wals', '%sA.json' % context.parameter.wals_id)
    if not wals_data.exists():
        raise HTTPNotFound()

    wals_data = jsonlib.load(wals_data)
    value_map = {}

    for layer in wals_data['layers']:
        for feature in layer['features']:
            feature['properties']['icon'] = request.registry.getUtility(
                IIcon, name=feature['properties']['icon']).url(request)
            feature['properties']['popup'] = external_link(
                'http://wals.info/languoid/lect/wals_code_'
                + feature['properties']['language']['id'],
                label=feature['properties']['language']['name'])
        value_map[layer['properties']['number']] = {
            'icon': layer['features'][0]['properties']['icon'],
            'name': layer['properties']['name'],
            'number': layer['properties']['number'],
        }

    return {
        'wals_data': wals_data,
        'wals_map': WalsMap(
            context.parameter, request, data=wals_data, value_map=value_map),
        'apics_map': ApicsWalsMap(
            context.parameter, request, data=wals_data, value_map=value_map)}


def language_snippet_html(context=None, request=None, **kw):
    vs = None
    if 'parameter' in request.params:
        try:
            vs = DBSession.query(ValueSet)\
                .filter(ValueSet.parameter_pk == int(request.params['parameter']))\
                .filter(ValueSet.language_pk == context.pk)\
                .first()
        except ValueError:
            pass
    return {'valueset': vs}


def parameter_chapter_html(context=None, request=None, **kw):
    if context.feature_type != 'primary':
        raise HTTPNotFound()
    try:
        _html = get_text('Atlas', request.matchdict['id'], 'html')
        return {
            'md': get_text('Atlas', request.matchdict['id'], 'json'),
            'html': lambda vt: _html.replace('<p>value-table</p>', HTML.div(vt)),
            'css': get_text('Atlas', request.matchdict['id'], 'css'),
        }
    except ValueError:
        return {'md': {}, 'html': lambda s: '', 'css': ''}


def dataset_detail_html(context=None, request=None, **kw):
    return {
        'stats': context.get_stats(
            [rsc for rsc in RESOURCES if rsc.name
             in 'language contributor parameter sentence'.split()],
            language=Lect.language_pk == null(),
            parameter=and_(Feature.feature_type == 'primary', Parameter.id != '0'),
            contributor=Contributor.contribution_assocs.any()),
        'example_contribution': Contribution.get('58'),
        'citation': get_adapter(IRepresentation, context, request, ext='md.txt')}


def value_table(ctx, req):
    rows = []
    langs = {}

    for i, de in enumerate(ctx.domain):
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

        if exclusive or shared:
            rows.append(HTML.tr(*cells))
    rows.append(HTML.tr(
        HTML.td('Representation:', colspan=str(len(cells) - 1), class_='right'),
        HTML.td('%s' % len(langs), class_='right')))

    parts = []
    if ctx.multivalued:
        parts.append(HTML.thead(
            HTML.tr(*[HTML.th(s, class_='right')
                      for s in [' ', ' ', 'excl', 'shrd', 'all']])))
    parts.append(HTML.tbody(*rows))

    return HTML.table(*parts, class_='table table-condensed')


SEGMENT_VALUES = {
    1: (u'Exists (as a major allophone)', 'FC3535', 'segment major'),
    2: (u'Exists only as a minor allophone', 'FFB6C1', 'segment minor'),
    3: (u'Exists only in loanwords', 'F7F713', 'segment loan'),
    4: (u'Does not exist', 'FFFFFF', 'segment inexistent'),
}


def segments(language):
    """
    :return: dict mapping segment numbers to tuples (label, symbol, parameter, exists)
    """
    valuesets = {
        v.parameter.id: v
        for v in language.valuesets if v.parameter.feature_type == 'segment' and v.values}

    domainelements = {pid: v.values[0].domainelement for pid, v in valuesets.items()}

    return {
        sm.jsondata['number']: (
            '%s - %s' % (sm.name, domainelements[sm.id].name
                         if sm.id in domainelements else 'Does not exist'),
            sm.jsondata['symbol'],
            SEGMENT_VALUES[domainelements[sm.id].number][2]
            if sm.id in domainelements else 'segment inexistent',
            sm,
            sm.id in domainelements and domainelements[sm.id].number != 4,
            valuesets.get(sm.id))
        for sm in DBSession.query(Parameter).filter(Feature.feature_type == 'segment')}


def parameter_link(req, sym, p):
    return HTML.a(sym, href=req.resource_url(p), style="color: black;") if p else sym


def legend(req):
    return HTML.table(*[
        HTML.tr(
            HTML.td(literal('&nbsp;'), class_=SEGMENT_VALUES[n][2]),
            HTML.td(SEGMENT_VALUES[n][0], style="padding-left: 10px;"))
        for n in sorted(SEGMENT_VALUES.keys())])


def ipa_custom(req, segments):
    rows = []
    for i, data in segments.items():
        title, symbol, class_, param, exists, vs = data
        if exists and param \
                and (not param.jsondata['core_list'] or i in [15, 74, 77, 84]):
            rows.append(HTML.tr(
                HTML.td(
                    parameter_link(req, literal(symbol), vs or param),
                    title=title, class_=class_),
                HTML.th(
                    title.split('-', 1)[1].strip(),
                    style="padding-left: 10px; text-align: left;"),
            ))
    return HTML.table(HTML.tbody(*rows)) if rows else ''


def ipa_consonants(req, segments):
    #
    # a row_spec for a row in the segment chart is a pair (name, segment map), where
    # segment map maps column index to our internal segment number.
    #
    row_specs = [
        (
            'plosive/affricate',
            {1: 1, 2: 5, 7: 7, 8: 9, 9: 24, 10: 80, 11: 25, 12: 27, 13: 11, 14: 12,
             15: 13, 16: 14, 17: 2, 18: 17, 19: 75, 20: 76, 21: 18, 22: 19}
        ),
        ('aspirated plosive/affricate', {1: 4, 7: 8, 8: 6, 9: 79, 11: 26, 17: 16}),
        (
            'glottalized stop/affricate',
            {1: 20, 2: 23, 7: 21, 9: 81, 11: 28, 17: 22, 21: 78}
        ),
        ('nasal', {2: 42, 8: 43, 14: 44, 16: 45, 18: 46}),
        ('trill, tap or flap', {7: 47, 8: 48}),
        (
            'fricative',
            {
                1: 29, 2: 30, 3: 31, 4: 32, 5: 82, 6: 33,
                7: 34, 8: 35, 11: 36, 12: 37, 17: 38, 18: 39, 21: 40, 22: 41}
        ),
        ('lateral/approximant', {7: 85, 8: 49, 14: 50, 16: 51, 20: 52}),
    ]

    rows = []
    for i, spec in enumerate(row_specs):
        # build the chart row by row
        name, segment_map = spec
        cells = [HTML.th(name, class_="row-header")]
        for j in range(22):
            if j + 1 in segment_map:
                title, symbol, class_, p, exists, vs = segments[segment_map[j + 1]]
                cells.append(HTML.td(
                    parameter_link(req, symbol, vs or p), title=title, class_=class_))
            else:
                cells.append(HTML.td())
        rows.append(HTML.tr(*cells))

    return HTML.table(
        HTML.thead(
            HTML.tr(
                HTML.td(''),
                HTML.th(HTML.div('bilabial', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('labiodental', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('dental', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('dental/alveolar', class_="vertical"), colspan="2"),
                HTML.th(
                    HTML.div(
                        'dental/alveolar', HTML.br(), 'affricate', class_="vertical"),
                    colspan="2"),
                HTML.th(HTML.div('palato-alveolar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('retroflex', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('palatal', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('velar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('labial-velar', class_="vertical"), colspan="2"),
                HTML.th(HTML.div('uvular', class_="vertical")),
                HTML.th(HTML.div('glottal', class_="vertical")),
            ),
        ),
        HTML.tbody(*rows),
        style="margin-top: 5em;",
    )


def ipa_vowels(req, segments):
    segments[0] = ('separator', u'•', 'segment-separator', None, False, None)

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
            *[HTML.span(parameter_link(req, symbol, vs or p), class_=class_, title=name)
              for name, symbol, class_, p, exists, vs
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
                    HTML.span(
                        'front',
                        style="position:relative; left:-0.4em; font-weight: bold;"),
                    style="width:64px;"),
                HTML.td(
                    'near-front',
                    style="width:62px; font-weight: bold;"),
                HTML.td(
                    'central',
                    style="width:64px; font-weight: bold;"),
                HTML.td(
                    'near-back',
                    style="width:62px; font-weight: bold;"),
                HTML.td(
                    'back',
                    style="width:64px; font-weight: bold;"),
                style="text-align: center;",
            ),
            HTML.tr(
                HTML.td(
                    'high', style="height:32px; text-align:right; font-weight: bold;"),
                HTML.td(
                    diagram,
                    style="height:210px; padding-left: 30px;", colspan="5", rowspan="7"),
            ),
            HTML.tr(HTML.td('', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td(
                'higher-mid', style="height:32px; text-align:right; font-weight: bold;")),
            HTML.tr(HTML.td(
                'mid', style="height:32px; text-align:right; font-weight: bold;")),
            HTML.tr(HTML.td(
                'lower-mid', style="height:32px; text-align:right; font-weight: bold;")),
            HTML.tr(HTML.td('', style="height:32px; text-align:right;")),
            HTML.tr(HTML.td(
                'low', style="height:32px; text-align:right; font-weight: bold;")),
        ),
        style="line-height:1.4em; background:transparent; margin:0em auto 0em auto;",
        cellspacing="0")


def feature_description(req, ctx):
    desc = ctx.markup_description or ctx.description
    desc = re.sub(
        "\*\*(?P<id>[0-9]+\-[0-9]+)\*\*",
        lambda m: HTML.a(
            '[%s]' % m.group('id'), href=req.route_url('sentence', id=m.group('id'))),
        desc)

    desc = re.sub(
        "\*\*\<\/span\>(?P<id>[0-9]+\-[0-9]+)\*\*",
        lambda m: literal('</span>') + HTML.a(
            '[%s]' % m.group('id'), href=req.route_url('sentence', id=m.group('id'))),
        desc)

    return re.sub(
        '\<span style\=\"font-style\: italic;\"\>WALS\<\/span\>\s+feature\s+[0-9]+',
        lambda m: HTML.a(
            literal(desc[m.start():m.end()]), href=req.route_url('wals', id=ctx.id)),
        desc)
