from sqlalchemy import desc, null
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from sqlalchemy.orm import joinedload_all, joinedload, aliased

from clld.web import datatables
from clld.web.util.helpers import external_link, link, map_marker_img
from clld.web.util.htmllib import HTML, literal
from clld.web.datatables.base import (
    LinkToMapCol, Col, LinkCol, DetailsRowLinkCol, IntegerIdCol, DataTable,
)
from clld.web.datatables.value import ValueNameCol, RefsCol
from clld.web.datatables.contribution import CitationCol, ContributorsCol
from clld.web.datatables import contributor as contrib
from clld.web.datatables.sentence import Sentences, AudioCol
from clld.db.meta import DBSession
from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import (
    Value, Parameter, Language, ValueSet, ValueSetReference, DomainElement,
)
from clldutils.misc import dict_merged, nfilter

from apics.models import Feature, Lect, ApicsContribution, Survey


def description(request, anchor):
    return '<p>%s<a href="%s" target="_blank">%s</a> page.</p>' % (
        'For a description of this table refer to the ',
        request.route_url('help', _anchor=anchor),
        'Help')


class Examples(Sentences):
    def col_defs(self):
        cols = Sentences.col_defs(self)
        return cols[:-1] + [AudioCol(self, 'audio')] + cols[-1:]

    def get_options(self):
        return {'sDescription': description(self.req, 'sentences')}


#
# Features
#
class WalsCol(Col):
    __kw__ = dict(sTitle=u'WALS\u2013APiCS', input_size='mini')

    def format(self, item):
        if not item.wals_id:
            return ''
        return link(
            self.dt.req,
            item,
            href=self.dt.req.route_url('wals', id=item.id),
            label="WALS %sA" % item.wals_id)


class AreaCol(Col):
    def __init__(self, dt, name, **kw):
        kw['model_col'] = Feature.area
        # list areas by the order in which they appear:
        area_map = dict(
            [(f.area, int(f.id)) for f in
             DBSession.query(Feature).order_by(desc(cast(Parameter.id, Integer)))])
        area_map = {v: k for k, v in area_map.items()}
        kw['choices'] = [area_map[j] for j in sorted(area_map.keys()) if area_map[j]]
        super(AreaCol, self).__init__(dt, name, **kw)


class ChapterCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return link(
            self.dt.req, item,
            label='Chapter {0} by {1}'.format(item.id, item.formatted_contributors()),
            url_kw=dict(ext='chapter.html'))


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Parameter.id != '0')

    def col_defs(self):
        return [
            IntegerIdCol(self, 'id'),
            LinkCol(self, 'name', sTitle='Feature information'),
            ChapterCol(self, 'chapter', sTitle='Chapter'),
            Col(self,
                'feature_type',
                model_col=Feature.feature_type,
                sFilter='primary',
                choices=['primary', 'segment', 'sociolinguistic']),
            AreaCol(self, 'area'),
            WalsCol(self, 'WALS feature', model_col=Feature.wals_id),
            CitationCol(self, 'cite'),
        ]

    def get_options(self):
        return {'sDescription': description(self.req, 'parameters')}


#
# WALS Features
#
class WalsFeatureCol(LinkCol):
    def get_attrs(self, item):
        return {'href': self.dt.req.route_url('wals', id=item.id)}


class WalsWalsCol(Col):
    def format(self, item):
        return external_link(
            'http://wals.info/feature/%sA' % item.wals_id, label='%sA' % item.wals_id)


class WalsFeatures(datatables.Parameters):
    def db_model(self):
        return Parameter

    def base_query(self, query):
        return query.filter(Feature.wals_id != null())\
            .options(joinedload(Parameter.valuesets))

    def col_defs(self):
        return [
            IntegerIdCol(self, 'id', model_col=Parameter.id),
            WalsFeatureCol(self, 'name', sTitle='Feature name', model_col=Parameter.name),
            AreaCol(self, 'area'),
            Col(self, 'atotal',
                sTitle='APiCS total', model_col=Feature.representation),
            Col(self, 'wtotal',
                sTitle='WALS total', model_col=Feature.wals_representation),
            WalsWalsCol(
                self, 'wfeature',
                sTitle='WALS feature', input_size='mini', model_col=Feature.wals_id)]

    def get_options(self):
        return {'sDescription': description(self.req, 'wals_apics')}


class ApicsValueNameCol(ValueNameCol):
    def get_attrs(self, item):
        label = item.__unicode__()
        label = HTML.span(map_marker_img(self.dt.req, item), literal('&nbsp;'), label)
        return {'label': label, 'title': item.__unicode__()}


class Values(datatables.Values):
    def __init__(self, req, model, **kw):
        self.ftype = kw.pop('ftype', req.params.get('ftype', None))
        if self.ftype:
            kw['eid'] = 'dt-values-' + self.ftype
        self.vs_lang = aliased(Language)
        self.vs_lect = aliased(Lect)
        super(Values, self).__init__(req, model, **kw)

    def get_options(self):
        opts = super(Values, self).get_options()
        if self.parameter:
            opts['aaSorting'] = [
                [0, 'asc'], [2 if self.parameter.multivalued else 1, 'desc']]
        if self.language:
            opts['aaSorting'] = [[0, 'asc'], [2, 'asc']]
        opts['sDescription'] = description(
            self.req, "language" if self.language else 'parameter')
        return opts

    def xhr_query(self):
        return dict_merged(super(Values, self).xhr_query(), ftype=self.ftype)

    def base_query(self, query):
        query = DBSession.query(self.model)\
            .join(ValueSet)\
            .options(joinedload_all(
                Value.valueset, ValueSet.references, ValueSetReference.source
            )).distinct()

        if not self.parameter:
            query = query.join(ValueSet.parameter).filter(Parameter.id != '0')
            if self.ftype:
                query = query.filter(Feature.feature_type == self.ftype)

        if self.language:
            return query\
                .options(joinedload(Value.domainelement))\
                .filter(ValueSet.language_pk.in_(
                    [l.pk for l in [self.language] + self.language.lects]))

        if self.parameter:
            query = query.join(ValueSet.contribution)\
                .join(self.vs_lang, ValueSet.language_pk == self.vs_lang.pk)\
                .join(self.vs_lect, ValueSet.language_pk == self.vs_lect.pk)\
                .join(DomainElement)\
                .options(joinedload(Value.domainelement))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        return query

    def col_defs(self):
        kw = {}
        if self.language:
            kw['bSearchable'] = False
            kw['bSortable'] = False
        name_col = ApicsValueNameCol(self, 'value', **kw)
        if self.parameter and self.parameter.domain:
            name_col.choices = [de.name for de in self.parameter.domain]

        class ValueLanguageCol(LinkCol):
            def search(self, qs):
                if self.dt.language:
                    return ValueSet.language_pk == int(qs)
                if self.dt.parameter:
                    return icontains(self.dt.vs_lang.name, qs)

            def order(self):
                if self.dt.parameter:
                    return cast(self.dt.vs_lang.id, Integer)
                if self.dt.language:
                    return ValueSet.language_pk

        lang_col = ValueLanguageCol(
            self,
            'language',
            model_col=Language.name,
            get_obj=lambda item: item.valueset.language,
            bSearchable=bool(self.parameter or self.language),
            bSortable=bool(self.parameter or self.language))
        if self.language:
            if self.language.lects:
                lang_col.choices = [
                    (l.pk, l.name) for l in [self.language] + self.language.lects]
                lang_col.js_args['sTitle'] = 'lect'
            else:
                lang_col = None

        get_param = lambda i: i.valueset.parameter
        if self.parameter:
            return nfilter([
                lang_col,
                name_col,
                Col(self,
                    'lexifier',
                    format=lambda i: i.valueset.language.lexifier,
                    model_col=self.vs_lect.lexifier,
                    choices=get_distinct_values(
                        Lect.lexifier,
                        key=lambda v: 'z' + v if v == 'Other' else v)),
                LinkToMapCol(
                    self, 'm', get_object=lambda i: None
                    if i.valueset.language.language_pk else i.valueset.language),
                DetailsRowLinkCol(self, 'more')
                if self.parameter.feature_type != 'sociolinguistic' else None,
                RefsCol(self, 'source')
                if self.parameter.feature_type != 'segment' else None,
            ])
        if self.language:
            return nfilter([
                IntegerIdCol(self, 'id', get_obj=get_param, model_col=Parameter.id),
                LinkCol(self, 'parameter', get_obj=get_param, model_col=Parameter.name),
                name_col,
                lang_col,
                DetailsRowLinkCol(self, 'more'),
                RefsCol(self, 'source'),
            ])
        return [
            LinkCol(self, 'parameter', get_obj=get_param, model_col=Parameter.name),
            name_col,
            lang_col,
            DetailsRowLinkCol(self, 'more'),
            RefsCol(self, 'source'),
        ]


#
# Contributions
#
class ApicsContributions(datatables.Contributions):
    def base_query(self, query):
        return super(ApicsContributions, self).base_query(query).join(Language)\
            .options(joinedload_all(ApicsContribution.language, Lect.survey))

    def col_defs(self):
        return [
            IntegerIdCol(self, 'id'),
            LinkCol(self, 'name', sTitle='Language structure dataset'),
            ContributorsCol(self, 'contributors', bSearchable=False, bSortable=False, sTitle='Authors of dataset'),
            Col(self, 'lexifier',
                choices=get_distinct_values(
                    Lect.lexifier, key=lambda v: 'z' + v if v == 'Other' else v),
                get_obj=lambda item: item.language,
                model_col=Lect.lexifier),
            Col(self, 'region',
                choices=get_distinct_values(Lect.region),
                get_obj=lambda item: item.language,
                model_col=Lect.region),
            CitationCol(self, 'cite', bSearchable=False, bSortable=False),
            IntegerIdCol(
                self,
                'survey',
                get_object=lambda c: c.language.survey,
                bSearchable=False,
                bSortable=False,
                sTitle='Survey'),
        ]

    def get_options(self):
        return {'sDescription': description(self.req, 'languages')}


class DatasetsCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return HTML.ul(
            *[HTML.li(link(self.dt.req, l.contribution, label=l.id)) for l in item.languages],
            **dict(class_='inline'))


class Surveys(DataTable):
    def base_query(self, query):
        return super(Surveys, self).base_query(query).join(Language).options(joinedload(Survey.languages)).distinct()

    def col_defs(self):
        return [
            IntegerIdCol(self, 'id'),
            LinkCol(self, 'name', sTitle='Language survey'),
            ContributorsCol(self, 'contributors', bSearchable=False, bSortable=False, sTitle='Authors of survey'),
            Col(self, 'lexifier',
                choices=get_distinct_values(
                    Lect.lexifier, key=lambda v: 'z' + v if v == 'Other' else v),
                get_obj=lambda item: item.languages[0],
                model_col=Lect.lexifier),
            Col(self, 'region',
                choices=get_distinct_values(Lect.region),
                format=lambda item: item.languages[0].region,
                model_col=Lect.region),
            CitationCol(self, 'cite', bSearchable=False, bSortable=False),
            DatasetsCol(self, 'datasets'),
        ]


class SurveysCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return HTML.ul(
            *[HTML.li(link(
                self.dt.req, c.survey)) for c in item.survey_assocs])


class Authors(contrib.Contributors):
    def col_defs(self):
        return [
            contrib.NameCol(self, 'name'),
            contrib.ContributionsCol(self, 'Contributions', sTitle='Structure datasets'),
            SurveysCol(self, 'Surveys'),
            contrib.AddressCol(self, 'address'),
            contrib.UrlCol(self, 'Homepage'),
        ]


def includeme(config):
    config.register_datatable('sentences', Examples)
    config.register_datatable('parameters', Features)
    config.register_datatable('values', Values)
    config.register_datatable('values_alt', Values)
    config.register_datatable('contributions', ApicsContributions)
    config.register_datatable('contributors', Authors)
    config.register_datatable('walss', WalsFeatures)
    config.register_datatable('surveys', Surveys)
