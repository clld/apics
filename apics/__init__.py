from functools import partial

from sqlalchemy.orm import joinedload, joinedload_all
from pyramid.config import Configurator

from clld.interfaces import (
    ICtxFactoryQuery, IValueSet, IValue, IDomainElement, ILanguage, IMapMarker,
    ILinkAttrs, IParameter,
)
from clld.web.app import CtxFactoryQuery, menu_item
from clld.db.models import common
from clld.web.icon import MapMarker
from clldutils import svg
from clld.web.adapters.download import CsvDump, N3Dump, Download
from clld.web.adapters.base import Representation

from apics.models import ApicsContribution, Wals, Survey
from apics.interfaces import IWals, ISurvey

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
        if model == common.Contributor:
            query = query.options(
                joinedload_all(
                    common.Contributor.survey_assocs,
                    models.SurveyContributor.survey)
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


class ApicsMapMarker(MapMarker):
    @staticmethod
    def pie(*slices):
        return svg.data_url(svg.pie(
            [float(p[0]) for p in slices],
            ['#' + p[1] for p in slices],
            stroke_circle=True))

    @staticmethod
    def pie_from_filename(fname):
        if fname.startswith('pie-'):
            spec = fname.replace('pie-', '').replace('.png', '').split('-')
        elif fname.startswith('freq-'):
            freq = int(fname.replace('freq-', '').replace('.png', ''))
            spec = [freq, '000000', 100 - freq, 'ffffff']
        return ApicsMapMarker.pie(*[spec[i:i+2] for i in range(0, len(spec), 2)])

    def __call__(self, ctx, req):
        if IValueSet.providedBy(ctx):
            if req.matched_route.name == 'valueset' and not ctx.parameter.multivalued:
                return self.pie((100, ctx.values[0].domainelement.jsondata['color']))
            return self.pie_from_filename(ctx.jsondata['icon'])

        if IValue.providedBy(ctx):
            freq = ctx.frequency or 100
            slices = [(freq, ctx.domainelement.jsondata['color'])]
            if freq < 100:
                slices.append((100 - freq, 'ffffff'))
            return self.pie(*slices)

        if IDomainElement.providedBy(ctx):
            return self.pie((100, ctx.jsondata['color']))

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
    settings['route_patterns'] = {'walss': '/wals', 'wals': '/wals/{id:[^/\.]+}'}
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.registry.registerUtility(ApicsCtxFactoryQuery(), ICtxFactoryQuery)
    config.registry.registerUtility(ApicsMapMarker(), IMapMarker)
    config.registry.registerUtility(link_attrs, ILinkAttrs)
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('contributions', partial(menu_item, 'contributions')),
        ('parameters', partial(menu_item, 'parameters')),
        ('apics_wals', lambda ctx, rq: (rq.route_url('walss'), u'WALS\u2013APiCS')),
        ('surveys', partial(menu_item, 'surveys')),
        ('sentences', partial(menu_item, 'sentences')),
        ('sources', partial(menu_item, 'sources')),
        ('contributors', partial(menu_item, 'contributors')),
    )
    config.register_adapter(
        {
            "base": Representation,
            "mimetype": 'application/vnd.clld.chapter+html',
            "send_mimetype": "text/html",
            "extension": 'chapter.html',
            "template": 'parameter/chapter_html.mako',
        },
        IParameter,
        name="application/vnd.clld.chapter+html")

    config.register_download(CsvDump(
        common.Language, 'apics', description="Languages as CSV"))
    config.register_download(N3Dump(
        common.Language, 'apics', description="Languages as RDF"))
    config.register_download(Download(
        common.Source, 'apics', ext='bib', description="Sources as BibTeX"))

    config.register_resource('wals', Wals, IWals, with_index=True)
    config.register_resource('survey', Survey, ISurvey, with_index=True)

    config.register_adapters([(
            ISurvey,
            Representation,
            'application/vnd.clld.md+xml',
            'md.html',
            'md_html.mako',
            {'rel': 'describedby'})])

    return config.make_wsgi_app()
