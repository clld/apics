from sqlalchemy import desc
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from sqlalchemy.orm import joinedload_all, joinedload, aliased

from clld.web import datatables
from clld.web.util.helpers import external_link, format_frequency, link
from clld.web.datatables.base import (
    LinkToMapCol, Col, LinkCol, IdCol, filter_number, DetailsRowLinkCol,
)
from clld.web.datatables.value import (
    ValueNameCol, ParameterCol, ValueLanguageCol, RefsCol,
)
from clld.web.datatables.contribution import CitationCol, ContributorsCol
from clld.web.datatables.sentence import Sentences
from clld.db.meta import DBSession
from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import (
    Value, Parameter, Language, ValueSet, ValueSetReference, DomainElement,
)

from apics.models import Feature, Lect


def description(request, anchor):
    return '<p>For a description of this table refer to the <a href="%s" target="_blank">%s</a> page.</p>' % (
        request.route_url('help', _anchor=anchor), 'Help')


class Examples(Sentences):
    def get_options(self):
        return {'sDescription': description(self.req, 'sentences')}


#
# Features
#
class OrderNumberCol(IdCol):
    __kw__ = {'input_size': 'mini', 'sClass': 'right', 'sTitle': 'No.'}

    def search(self, qs):
        return filter_number(cast(self.dt.model.id, Integer), qs, type_=int)

    def order(self):
        return cast(self.dt.model.id, Integer)


class WalsCol(Col):
    __kw__ = dict(sTitle=u'WALS\u2013APiCS', input_size='mini')

    def format(self, item):
        if not item.wals_id:
            return ''
        return link(self.dt.req, item, href=self.dt.req.route_url('wals', id=item.id), label="WALS %sA" % item.wals_id)


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


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Parameter.id != '0')

    def col_defs(self):
        return [
            OrderNumberCol(self, 'id'),
            LinkCol(self, 'name', sTitle='Feature name'),
            Col(
                self,
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
    def base_query(self, query):
        return query.filter(Feature.wals_id != None)\
            .options(joinedload(Parameter.valuesets))

    def col_defs(self):
        return [
            OrderNumberCol(self, 'id'),
            WalsFeatureCol(self, 'name', sTitle='Feature name'),
            AreaCol(self, 'area'),
            Col(self, 'atotal', sTitle='APiCS total', sClass="right", model_col=Feature.representation),
            Col(self, 'wtotal', sTitle='WALS total', sClass="right", model_col=Feature.wals_representation),
            WalsWalsCol(self, 'wfeature', sTitle='WALS feature', input_size='mini', model_col=Feature.wals_id)]

    def get_options(self):
        return {
            'sAjaxSource': self.req.route_url('wals_index'),
            'sDescription': description(self.req, 'wals_apics')}


#
# Values
#
class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        if item.valueset.language.language_pk:
            return None
        return item.valueset.language


class FrequencyCol(Col):
    def format(self, item):
        return format_frequency(self.dt.req, item)


class _ParameterCol(ParameterCol):
    def order(self):
        return cast(Parameter.id, Integer)


class _ParameterIdCol(ParameterCol):
    def order(self):
        return cast(Parameter.id, Integer)

    def get_attrs(self, item):
        return {'label': item.valueset.parameter.id}


class Values(datatables.Values):
    def __init__(self, req, model, **kw):
        self.ftype = kw.pop('ftype', req.params.get('ftype', None))
        if self.ftype:
            kw['eid'] = 'dt-values-' + self.ftype
        super(Values, self).__init__(req, model, **kw)

    def get_options(self):
        opts = super(Values, self).get_options()
        if self.parameter:
            opts['aaSorting'] = [[0, 'asc'], [2 if self.parameter.multivalued else 1, 'desc']]
        if self.language:
            opts['aaSorting'] = [[0, 'asc'], [2, 'asc']]
        opts['sDescription'] = description(
            self.req, "language" if self.language else 'parameter')
        return opts

    def xhr_query(self):
        _q = super(Values, self).xhr_query()
        if self.ftype:
            _q['ftype'] = self.ftype
        return _q

    def base_query(self, query):
        query = DBSession.query(self.model)\
            .join(ValueSet)\
            .options(joinedload_all(
                Value.valueset, ValueSet.references, ValueSetReference.source)
            ).distinct()

        if not self.parameter:
            query = query.join(ValueSet.parameter).filter(Parameter.id != '0')
            if self.ftype:
                query = query.filter(Feature.feature_type == self.ftype)

        if self.language:
            return query\
                .options(joinedload(Value.domainelement))\
                .filter(ValueSet.language_pk.in_(
                    [l.pk for l in [self.language] + self.language.lects]))

        self.vs_lang = aliased(Language)
        self.vs_lect = aliased(Lect)
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
        name_col = ValueNameCol(self, 'value', **kw)
        if self.parameter and self.parameter.domain:
            name_col.choices = [de.name for de in self.parameter.domain]

        class _ValueLanguageCol(ValueLanguageCol):
            def get_obj(self, item):
                return item.valueset.language

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

        class LexifierCol(Col):
            def format(self, item):
                return item.valueset.language.lexifier

            def search(self, qs):
                return icontains(self.dt.vs_lect.lexifier, qs)

            def order(self):
                return self.dt.vs_lect.lexifier

        lang_col = _ValueLanguageCol(
            self,
            'language',
            model_col=Language.name,
            bSearchable=bool(self.parameter or self.language),
            bSortable=bool(self.parameter or self.language))
        if self.language:
            if self.language.lects:
                lang_col.choices = [(l.pk, l.name) for l in [self.language] + self.language.lects]
                lang_col.js_args['sTitle'] = 'lect'
            else:
                lang_col = None

        frequency_col = FrequencyCol(
            self, '%',
            sClass='center',
            bSearchable=False,
            model_col=Value.frequency,
            input_size='mini')

        if self.parameter:
            return filter(None, [
                lang_col,
                name_col,
                frequency_col if self.parameter.multivalued else None,
                LexifierCol(
                    self,
                    'lexifier',
                    choices=get_distinct_values(
                        Lect.lexifier,
                        key=lambda v: 'z' + v if v == 'Other' else v)),
                _LinkToMapCol(self, 'm'),
                DetailsRowLinkCol(self, 'more') if self.parameter.feature_type != 'sociolinguistic' else None,
                RefsCol(self, 'source', bSearchable=False, bSortable=False) if self.parameter.feature_type != 'segment' else None,
            ])
        if self.language:
            return filter(None, [
                _ParameterIdCol(self, 'feature id', sTitle="No.", input_size='mini', sClass='right'),
                _ParameterCol(self, 'parameter', model_col=Parameter.name),
                name_col,
                frequency_col,
                lang_col,
                DetailsRowLinkCol(self, 'more'),
                RefsCol(self, 'source', bSearchable=False, bSortable=False),
            ])
        return [
            _ParameterCol(self, 'parameter', sTitle="No.", model_col=Parameter.name),
            name_col,
            frequency_col,
            lang_col,
            DetailsRowLinkCol(self, 'more'),
            RefsCol(self, 'source', bSearchable=False, bSortable=False),
        ]


#
# Contributions
#
class RegionCol(Col):
    def format(self, item):
        return item.language.region

    def search(self, qs):
        return icontains(Lect.region, qs)

    def order(self):
        return Lect.region


class LexifierCol(Col):
    def format(self, item):
        return item.language.lexifier

    def search(self, qs):
        return Lect.lexifier == qs

    def order(self):
        return Lect.lexifier


class ApicsContributions(datatables.Contributions):
    def base_query(self, query):
        return super(ApicsContributions, self).base_query(query).join(Language)

    def col_defs(self):
        return [
            OrderNumberCol(self, 'id'),
            LinkCol(self, 'name', sTitle='Language'),
            ContributorsCol(self, 'contributors', bSearchable=False, bSortable=False),
            LexifierCol(
                self,
                'lexifier',
                choices=get_distinct_values(
                    Lect.lexifier, key=lambda v: 'z' + v if v == 'Other' else v)),
            RegionCol(self, 'region', choices=get_distinct_values(Lect.region)),
            CitationCol(self, 'cite', bSearchable=False, bSortable=False),
        ]

    def get_options(self):
        return {'sDescription': description(self.req, 'languages')}
