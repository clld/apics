from pyramid.config import Configurator
from sqlalchemy.orm import joinedload, joinedload_all

from clld import interfaces
from clld.web.app import CtxFactoryQuery
from clld.db.models import common

from apics.models import ApicsContribution, Lect
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


def map_marker(ctx, req):
    if interfaces.IValueSet.providedBy(ctx):
        fracs = [int(v.frequency) for v in ctx.values]
        colors = [v.domainelement.datadict()['color'] for v in ctx.values]
        id_ = '-'.join('%s-%s' % (f, c) for f, c in zip(fracs, colors))
        return req.static_url('apics:static/icons/pie-%s.png' % id_)

    if interfaces.IValue.providedBy(ctx):
        dd = ctx.domainelement.datadict()
        if 'color' in dd:
            return req.static_url('apics:static/icons/pie-100-%s.png' % dd['color'])

    if interfaces.IDomainElement.providedBy(ctx):
        dd = ctx.datadict()
        if 'color' in dd:
            return req.static_url('apics:static/icons/pie-100-%s.png' % dd['color'])


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
    config.registry.registerUtility(map_marker, interfaces.IMapMarker)
    config.registry.registerUtility(link_attrs, interfaces.ILinkAttrs)

    config.register_map('contribution', LanguageMap)
    config.register_map('contributions', LexifierMap)
    config.register_map('parameter', FeatureMap)
    config.register_datatable('parameters', Features)
    config.register_datatable('values', Values)
    config.register_datatable('values_alt', Values)
    config.register_datatable('contributions', ApicsContributions)

    #config.add_route('wals_proxy', '/wals-proxy')
    return config.make_wsgi_app()
