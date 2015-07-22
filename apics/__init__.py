from functools import partial

from sqlalchemy.orm import joinedload, joinedload_all
from pyramid.config import Configurator

from clld.interfaces import (
    ICtxFactoryQuery, IValueSet, IValue, IDomainElement, ILanguage, IMapMarker,
    IFrequencyMarker, ILinkAttrs,
)
from clld.web.app import CtxFactoryQuery, menu_item
from clld.db.models import common
from clld.web.icon import MapMarker
from clld.web.adapters.download import CsvDump, N3Dump, Download, Sqlite

from apics.models import ApicsContribution, Wals
from apics.interfaces import IWals

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
    def __call__(self, model, req):
        if model == Wals:
            return Wals(
                req.db.query(common.Parameter).filter(
                    common.Parameter.id == req.matchdict['id']).one())
        return CtxFactoryQuery.__call__(self, model, req)

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
    if IValue.providedBy(ctx):
        return req.static_url(
            'apics:static/icons/%s' % ctx.jsondata['frequency_icon'])


class ApicsMapMarker(MapMarker):
    def __call__(self, ctx, req):
        icon = None
        if IValueSet.providedBy(ctx):
            if req.matched_route.name == 'valueset' and not ctx.parameter.multivalued:
                return ''
            icon = ctx.jsondata['icon']

        if IValue.providedBy(ctx):
            icon = ctx.domainelement.jsondata['icon']

        if IDomainElement.providedBy(ctx):
            icon = ctx.jsondata['icon']

        if icon:
            return req.static_url('apics:static/icons/%s' % icon)

        return super(ApicsMapMarker, self).__call__(ctx, req)


def link_attrs(req, obj, **kw):
    if ILanguage.providedBy(obj):
        # we are about to link to a language details page: redirect to contribution page!
        id_ = obj.language.id if obj.language else obj.id
        kw['href'] = req.route_url('contribution', id=id_, **kw.pop('url_kw', {}))

    if IValueSet.providedBy(obj) and obj.parameter_pk == 1:
        # we are about to link to a valueset of the "hidden" feature 0: redirect to
        # contribution page!
        kw['href'] = req.route_url(
            'contribution', id=obj.language.id, **kw.pop('url_kw', {}))

    return kw


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['sitemaps'] = 'contribution parameter source sentence valueset'.split()
    settings['route_patterns'] = {'walss': '/wals', 'wals': '/wals/{id:[^/\.]+}'}
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.registry.registerUtility(ApicsCtxFactoryQuery(), ICtxFactoryQuery)
    config.registry.registerUtility(ApicsMapMarker(), IMapMarker)
    config.registry.registerUtility(frequency_marker, IFrequencyMarker)
    config.registry.registerUtility(link_attrs, ILinkAttrs)
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('contributions', partial(menu_item, 'contributions')),
        ('parameters', partial(menu_item, 'parameters')),
        ('apics_wals', lambda ctx, rq: (rq.route_url('walss'), u'WALS\u2013APiCS')),
        ('sentences', partial(menu_item, 'sentences')),
        ('sources', partial(menu_item, 'sources')),
        ('contributors', partial(menu_item, 'contributors')),
    )

    config.register_download(CsvDump(
        common.Language, 'apics', description="Languages as CSV"))
    config.register_download(N3Dump(
        common.Language, 'apics', description="Languages as RDF"))
    config.register_download(Download(
        common.Source, 'apics', ext='bib', description="Sources as BibTeX"))
    config.register_download(Sqlite(
        common.Dataset, 'apics', description="APiCS database as sqlite3"))

    config.register_resource('wals', Wals, IWals, with_index=True)

    config.add_route('chapters', '/admin/chapters')
    config.add_route('chapter', '/admin/chapters/{id}')
    config.add_route('surveys', '/admin/surveys')
    config.add_route('survey', '/admin/surveys/{id}')
    return config.make_wsgi_app()
