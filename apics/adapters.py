from clld import interfaces
from clld.web.adapters import GeoJsonParameter
from clld.web.adapters.md import BibTex, TxtCitation
from clld.web.adapters.base import Representation
from clld.lib import bibtex
from clldutils.dsv import UnicodeWriter
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet, Language, Parameter, Value, DomainElement

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
            title=getattr(ctx, 'citation_name', ctx.__unicode__()),
            url=req.resource_url(ctx),
            address=req.dataset.publisher_place,
            publisher=req.dataset.publisher_name,
            year=str(req.dataset.published.year),
            author=ctx.format_authors(),
            booktitle=req.dataset.description,
            editor=' and '.join(c.contributor.name for c in list(req.dataset.editors)))


class FeatureReferenceManager(FeatureBibTex):
    """Resource metadata in RIS format.
    """
    name = 'RIS'
    __label__ = 'RIS'
    unapi = 'ris'
    extension = 'md.ris'
    mimetype = "application/x-research-info-systems"

    def render(self, ctx, req):
        return self.rec(ctx, req).format('ris')


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


class SurveyReferenceManager(SurveyBibTex):
    """Resource metadata in RIS format.
    """
    name = 'RIS'
    __label__ = 'RIS'
    unapi = 'ris'
    extension = 'md.ris'
    mimetype = "application/x-research-info-systems"

    def render(self, ctx, req):
        return self.rec(ctx, req).format('ris')


class SurveyTxtCitation(TxtCitation):
    def render(self, ctx, req):
        self.template = 'survey/md_txt.mako'
        return Representation.render(self, ctx, req)


class Cldf(Representation):
    extension = str('cldf.csv')
    mimetype = str('text/csv')  # FIXME: declare header?

    def render(self, ctx, req):
        fid = req.route_url('parameter', id='xxx').replace('xxx', '{0}')
        lid = req.route_url('language', id='xxx').replace('xxx', '{0}')
        with UnicodeWriter() as writer:
            writer.writerow(['Language_ID', 'Feature_ID', 'Value'])
            for _lid, _fid, v in DBSession.query(
                    Language.id, Parameter.id, DomainElement.name) \
                    .filter(Language.pk == ValueSet.language_pk) \
                    .filter(Parameter.pk == ValueSet.parameter_pk) \
                    .filter(Value.valueset_pk == ValueSet.pk) \
                    .filter(Value.domainelement_pk == DomainElement.pk) \
                    .order_by(Parameter.pk, Language.id):
                writer.writerow([lid.format(_lid), fid.format(_fid), v])
            return writer.read()


def includeme(config):
    config.register_adapter(Cldf, interfaces.IDataset)
    config.register_adapter(GeoJsonFeature, interfaces.IParameter)
    config.register_adapter(FeatureMetadata, interfaces.IParameter)
    for cls in [FeatureBibTex, FeatureTxtCitation, FeatureReferenceManager]:
        for if_ in [interfaces.IRepresentation, interfaces.IMetadata]:
            config.register_adapter(cls, interfaces.IParameter, if_)
    config.register_adapter(SurveyMetadata, ISurvey)
    for cls in [SurveyBibTex, SurveyTxtCitation, SurveyReferenceManager]:
        for if_ in [interfaces.IRepresentation, interfaces.IMetadata]:
            config.register_adapter(cls, ISurvey, if_)
