import re

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import and_, null
from clld.db.meta import DBSession
from clld.db.models.common import (
    Parameter,
    ValueSet,
    Contributor,
    Contribution,
    Config,
)
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import map_marker_img, get_adapter, external_link
from clld.interfaces import IRepresentation, IIcon
from clld import RESOURCES
from clldmpg import cdstar
from purl import URL

from apics.models import Feature, Lect
from apics.maps import WalsMap, ApicsWalsMap


assert cdstar


def format_external_link_in_label(url, label=None):
    label = label or URL(url).domain()
    return HTML.span(
        HTML.a(
            HTML.i('', class_="icon-share icon-white"),
            label,
            href=url,
            style="color: white"),
        class_="label label-info")


def survey_detail_html(context=None, request=None, **kw):
    cfg = DBSession.query(Config).filter(Config.key=='survey-{}'.format(context.id)).one()
    return {
        'maps': cfg.jsondata.get('maps', []),
        'md': cfg.jsondata['md'],
        'html': cfg.value,
        'css': cfg.jsondata.get('css'),
    }


def wals_detail_html(context=None, request=None, **kw):
    value_map = {}

    for layer in context.jsondata['layers']:
        for feature in layer['features']:
            feature['properties']['icon'] = request.registry.getUtility(
                IIcon, name=feature['properties']['icon']).url(request)
            feature['properties']['popup'] = external_link(
                'https://wals.info/languoid/lect/wals_code_'
                + feature['properties']['language']['id'],
                label=feature['properties']['language']['name'])
        value_map[layer['properties']['number']] = {
            'icon': layer['features'][0]['properties']['icon'],
            'name': layer['properties']['name'],
            'number': layer['properties']['number'],
        }
    return {
        'wals_data': context.jsondata,
        'wals_map': WalsMap(
            context.parameter, request, data=context.jsondata, value_map=value_map),
        'apics_map': ApicsWalsMap(
            context.parameter, request, data=context.jsondata, value_map=value_map)}


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
    cfg = DBSession.query(Config).filter(
        Config.key=='atlas-{}'.format(request.matchdict['id'])).one()
    return {
        'md': cfg.jsondata['md'],
        'html': lambda vt: cfg.value.replace('<p>value-table</p>', HTML.div(vt)),
        'css': cfg.jsondata.get('css'),
    }


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


def parameter_link(req, sym, p):
    return HTML.a(sym, href=req.resource_url(p), style="color: black;") if p else sym


def legend(req):
    return HTML.table(
        HTML.tr(
            HTML.td(HTML.span(literal('&nbsp;&nbsp;&nbsp;'), style="width: 1em; outline: solid 2px red")),
            HTML.td(literal('&nbsp;&nbsp;&nbsp;&nbsp;'), style="font-weight: bold; text-decoration: underline; text-decoration-style: solid"),
            HTML.td('Exists (as a major allophone)')),
        HTML.tr(
            HTML.td(HTML.span(literal('&nbsp;&nbsp;&nbsp;'), style="width: 1em; outline: dashed 2px red")),
            HTML.td(literal('&nbsp;&nbsp;&nbsp;&nbsp;'), style="font-weight: bold; text-decoration: underline; text-decoration-style: dashed"),
            HTML.td('Exists only as a minor allophone')),
        HTML.tr(
            HTML.td(HTML.span(literal('&nbsp;&nbsp;&nbsp;'), style="width: 1em; outline: dotted 2px red")),
            HTML.td(literal('&nbsp;&nbsp;&nbsp;&nbsp;'), style="font-weight: bold; text-decoration: underline; text-decoration-style: dotted"),
            HTML.td('Exists only in loanwords')),
        class_='table table-condensed table-nonfluid')


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


def contribution_detail_html(context=None, request=None, **kw):
    from pyclts.ipachart import VowelTrapezoid, PulmonicConsonants

    colorspec = {
        'major': ('black', 'solid 2px red'),
        'minor': ('black', 'dashed 2px red'),
        'loan': ('black', 'dotted 2px red'),
    }

    res = {}
    d = VowelTrapezoid()
    covered = d.fill_slots(context.inventory)
    res['vowels_html'], res['vowels_css'] = d.render(colorspec=colorspec)
    d = PulmonicConsonants()
    covered = covered.union(d.fill_slots(context.inventory))
    res['consonants_html'], res['consonants_css'] = d.render(colorspec=colorspec)
    res['uncovered'] = [p for i, p in enumerate(context.inventory) if i not in covered]
    return res
