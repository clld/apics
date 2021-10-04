from clld import interfaces
from clld.web.adapters import GeoJsonParameter
from clld.web.adapters.md import BibTex, TxtCitation
from clld.web.adapters.base import Representation
from clld.lib import bibtex

from apics.interfaces import ISurvey


class GeoJsonFeature(GeoJsonParameter):
    def feature_iterator(self, ctx, req):
        for vs in super(GeoJsonFeature, self).feature_iterator(ctx, req):
            if not vs.language.language_pk:
                yield vs

    def feature_properties(self, ctx, req, valueset):
        return {
            'values': list(valueset.values),
            'label': valueset.language.name}


class GeoJsonApicsWals(GeoJsonParameter):
    def featurecollection_properties(self, ctx, req):
        return self.obj

    def feature_properties(self, ctx, req, vs):
        res = GeoJsonParameter.feature_properties(self, ctx, req, vs)
        res.update(icon=self.obj['icon'])
        return res

    def feature_iterator(self, ctx, req):
        return [vs for vs in ctx.valuesets
                if vs.jsondata.get('wals_value_number') == self.obj['number']
                and not vs.language.language_pk]


class FeatureMetadata(Representation):
    template = 'md_html.mako'
    mimetype = 'application/vnd.clld.md+xml'
    extension = 'md.html'


class FeatureBibTex(BibTex):
    def rec(self, ctx, req):
        return bibtex.Record(
            'incollection',
            ctx.id,
            title=getattr(ctx, 'citation_name', str(ctx)),
            url=req.resource_url(ctx),
            address='Oxford',
            publisher='Oxford University Press',
            year='2013',
            author=ctx.format_authors(),
            booktitle='The atlas of pidgin and creole language structures',
            editor=' and '.join(c.contributor.name for c in list(req.dataset.editors)))


class FeatureTxtCitation(TxtCitation):
    def render(self, ctx, req):
        self.template = 'parameter/md_txt.mako'
        return Representation.render(self, ctx, req)


class SurveyMetadata(Representation):
    template = 'md_html.mako'
    mimetype = 'application/vnd.clld.md+xml'
    extension = 'md.html'


class SurveyBibTex(BibTex):
    def rec(self, ctx, req):
        return bibtex.Record(
            'incollection',
            ctx.id,
            title=ctx.name,
            url=req.resource_url(ctx),
            address='Oxford',
            publisher='Oxford University Press',
            year='2013',
            author=ctx.formatted_contributors(),
            booktitle='The survey of pidgin and creole languages. {0}'.format(
                ctx.description),
            editor=' and '.join(c.contributor.name for c in list(req.dataset.editors)))


class SurveyTxtCitation(TxtCitation):
    def render(self, ctx, req):
        self.template = 'survey/md_txt.mako'
        return Representation.render(self, ctx, req)


def includeme(config):
    config.register_adapter(GeoJsonFeature, interfaces.IParameter)
    config.register_adapter(FeatureMetadata, interfaces.IParameter)
    for cls in [FeatureBibTex, FeatureTxtCitation]:
        for if_ in [interfaces.IRepresentation, interfaces.IMetadata]:
            config.register_adapter(cls, interfaces.IParameter, if_)
    config.register_adapter(SurveyMetadata, ISurvey)
    for cls in [SurveyBibTex, SurveyTxtCitation]:
        for if_ in [interfaces.IRepresentation, interfaces.IMetadata]:
            config.register_adapter(cls, ISurvey, if_)
