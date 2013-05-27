from functools import partial
from collections import OrderedDict

from pyramid.config import Configurator
from sqlalchemy.orm import joinedload, joinedload_all

from clld import interfaces
from clld.web.app import CtxFactoryQuery, menu_item
from clld.db.models import common
from clld.web.icon import MapMarker

from apics.models import ApicsContribution, Lect
from apics.adapters import GeoJsonFeature
from apics.maps import FeatureMap, LanguageMap, LexifierMap
from apics.datatables import Features, Values, ApicsContributions

#
# we list the i18n messages from clld core which we want to translate just to have them
# extracted by babel.
#
_ = lambda s: s

_('Parameter')
_('Parameters')
_('Contribution')
_('Contributions')
_('Contributor')
_('Contributors')
_('Sentence')
_('Sentences')
_('Value Set')
_('Address')


class ApicsCtxFactoryQuery(CtxFactoryQuery):
    def refined_query(self, query, model, req):
        if model == common.Contribution:
            query = query.options(
                joinedload_all(
                    common.Contribution.valuesets,
                    common.ValueSet.parameter,
                ),
                joinedload_all(
                    common.Contribution.valuesets,
                    common.ValueSet.values,
                    common.Value.domainelement),
                joinedload_all(
                    common.Contribution.valuesets,
                    common.ValueSet.values,
                    common.Value.sentence_assocs,
                    common.ValueSentence.sentence),
                joinedload(ApicsContribution.language),
            )
        if model == common.Parameter:
            query = query.options(
                joinedload_all(
                    common.Parameter.valuesets,
                    common.ValueSet.values,
                ),
                joinedload_all(
                    common.Parameter.valuesets,
                    common.ValueSet.language,
                ),
            )
        return query


def frequency_marker(ctx, req):
    if interfaces.IValue.providedBy(ctx):
        if req.matched_route.name in ['valueset', 'language_alt'] and ctx.frequency == 100:
            return ''
        return req.static_url(
            'apics:static/icons/%s' % ctx.jsondata['frequency_icon'])


class ApicsMapMarker(MapMarker):
    def __call__(self, ctx, req):
        icon = None
        if interfaces.IValueSet.providedBy(ctx):
            if req.matched_route.name == 'valueset' and not ctx.parameter.multivalued:
                return ''
            icon = ctx.jsondata['icon']

        if interfaces.IValue.providedBy(ctx):
            icon = ctx.domainelement.jsondata['icon']

        if interfaces.IDomainElement.providedBy(ctx):
            icon = ctx.jsondata['icon']

        if icon:
            return req.static_url('apics:static/icons/%s' % icon)

        return super(ApicsMapMarker, self).__call__(ctx, req)


def link_attrs(req, obj, **kw):
    if interfaces.ILanguage.providedBy(obj):
        # we are about to link to a language details page: redirect to contribution page!
        id_ = obj.language.id if obj.language else obj.id
        kw['href'] = req.route_url('contribution', id=id_, **kw.pop('url_kw', {}))
    return kw


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.register_app('apics')

    config.registry.registerUtility(ApicsCtxFactoryQuery(), interfaces.ICtxFactoryQuery)
    config.registry.registerUtility(ApicsMapMarker(), interfaces.IMapMarker)
    config.registry.registerUtility(frequency_marker, interfaces.IFrequencyMarker)
    config.registry.registerUtility(link_attrs, interfaces.ILinkAttrs)

    config.register_adapter(GeoJsonFeature, interfaces.IParameter)
    config.register_map('contribution', LanguageMap)
    config.register_map('contributions', LexifierMap)
    config.register_map('parameter', FeatureMap)
    config.register_datatable('parameters', Features)
    config.register_datatable('values', Values)
    config.register_datatable('values_alt', Values)
    config.register_datatable('contributions', ApicsContributions)

    config.add_route('wals_index', '/wals')
    config.add_route('wals', '/wals/{id}')

    menuitems = OrderedDict(home=partial(menu_item, 'home'))
    menuitems['contributions'] = partial(menu_item, 'contributions')
    menuitems['parameters'] = partial(menu_item, 'parameters')
    menuitems['apics_wals'] = lambda ctx, req: (req.route_url('wals_index'), 'WALS - APiCS')
    menuitems['contributors'] = partial(menu_item, 'contributors')
    menuitems['sentences'] = partial(menu_item, 'sentences')
    menuitems['sources'] = partial(menu_item, 'sources')
    config.registry.registerUtility(menuitems, interfaces.IMenuItems)
    return config.make_wsgi_app()
