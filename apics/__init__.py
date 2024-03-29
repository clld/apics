import functools
import collections

from sqlalchemy.orm import joinedload
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
                joinedload(common.Contribution.valuesets).joinedload(common.ValueSet.parameter),
                joinedload(common.Contribution.valuesets)
                .joinedload(common.ValueSet.values)
                .joinedload(common.Value.domainelement),
                joinedload(common.Contribution.valuesets)
                .joinedload(common.ValueSet.values)
                .joinedload(common.Value.sentence_assocs)
                .joinedload(common.ValueSentence.sentence),
                joinedload(ApicsContribution.language),
            )
        if model == common.Contributor:
            query = query.options(
                joinedload(common.Contributor.survey_assocs).joinedload(models.SurveyContributor.survey)
            )
        if model == common.Parameter:
            query = query.options(
                joinedload(common.Parameter.valuesets).joinedload(common.ValueSet.values),
                joinedload(common.Parameter.valuesets).joinedload(common.ValueSet.language),
            )
        return query


class ApicsMapMarker(MapMarker):
    @staticmethod
    def pie(*slices):
        return svg.data_url(svg.pie(
            [float(p[0]) for p in slices],
            ['#' + p[1] for p in slices],
            stroke_circle=True))

    def __call__(self, ctx, req):
        if IValueSet.providedBy(ctx):
            if req.matched_route.name == 'valueset' and not ctx.parameter.multivalued:
                return self.pie((100, ctx.values[0].domainelement.jsondata['color']))
            slices = collections.Counter()
            for v in ctx.values:
                slices[v.domainelement.jsondata['color']] += v.frequency or 1
            return self.pie(*[(v, k) for k, v in slices.most_common()])

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
        ('dataset', functools.partial(menu_item, 'dataset', label='Home')),
        ('contributions', functools.partial(menu_item, 'contributions')),
        ('parameters', functools.partial(menu_item, 'parameters')),
        ('apics_wals', lambda ctx, rq: (rq.route_url('walss'), u'WALS\u2013APiCS')),
        ('surveys', functools.partial(menu_item, 'surveys')),
        ('sentences', functools.partial(menu_item, 'sentences')),
        ('sources', functools.partial(menu_item, 'sources')),
        ('contributors', functools.partial(menu_item, 'contributors')),
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
