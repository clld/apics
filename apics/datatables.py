from sqlalchemy import and_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from sqlalchemy.orm import joinedload_all, joinedload, aliased

from clld.web import datatables
from clld.web.util.helpers import external_link, format_frequency
from clld.web.util.htmllib import HTML
from clld.web.datatables.base import (
    LinkToMapCol, Col, LinkCol, IdCol, filter_number, DetailsRowLinkCol,
)
from clld.web.datatables.value import (
    ValueNameCol, ParameterCol, ValueLanguageCol, RefsCol,
)
from clld.web.datatables.contribution import CitationCol, ContributorsCol
from clld.db.meta import DBSession
from clld.db.util import get_distinct_values
from clld.db.models.common import (
    Value_data, Value, Parameter, Language, ValueSet, ValueSetReference, DomainElement,
    Contribution,
)

from apics.models import Feature, Lect, ApicsContribution


class OrderNumberCol(IdCol):
    def __init__(self, dt, name='id', **kw):
        kw.setdefault('input_size', 'mini')
        kw.setdefault('sClass', 'right')
        kw.setdefault('sTitle', 'No.')
        super(OrderNumberCol, self).__init__(dt, name, **kw)

    def search(self, qs):
        return filter_number(cast(self.dt.model.id, Integer), qs, type_=int)

    def order(self):
        return cast(self.dt.model.id, Integer)


class WalsCol(Col):
    def format(self, item):
        if not item.wals_id:
            return ''
        return external_link(
            'http://wals.info/feature/%sA' % item.wals_id, label='%sA' % item.wals_id)


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Parameter.id != '0')

    def col_defs(self):
        return [
            OrderNumberCol(self),
            LinkCol(self, 'name', sTitle='Feature name'),
            Col(
                self,
                'feature_type',
                model_col=Feature.feature_type,
                sFilter='primary',
                choices=['primary', 'sociolinguistic', 'segment']),
            Col(
                self,
                'area',
                model_col=Feature.area,
                choices=get_distinct_values(Feature.area)),
            WalsCol(self, 'WALS feature', sTitle='WALS feature', input_size='mini', model_col=Feature.wals_id)]


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        if item.valueset.language.language_pk:
            return None
        return item.valueset.language

    def get_layer(self, item):
        if item.valueset.parameter.multivalued:
            return -1
        return item.domainelement.name


class FrequencyCol(Col):
    def format(self, item):
        return format_frequency(self.dt.req, item)


class _ParameterCol(ParameterCol):
    def order(self):
        return cast(Parameter.id, Integer)


class _ValueNameCol(ValueNameCol):
    def search(self, qs):
        return DomainElement.name.contains(qs)

    def order(self):
        return DomainElement.number


class Values(datatables.Values):
    #
    # TODO: default sorting:
    # by parameter.id on contribution page
    # by language.id on parameter page
    #
    def get_options(self):
        opts = super(Values, self).get_options()
        if self.parameter:
            opts['aaSorting'] = [[2 if self.parameter.multivalued else 1, 'asc'], [0, 'asc']]
        if self.language:
            opts['aaSorting'] = [[0, 'asc'], [1, 'asc']]
        return opts

    def base_query(self, query):
        query = DBSession.query(self.model)\
            .join(ValueSet)\
            .options(joinedload_all(
                Value.valueset, ValueSet.references, ValueSetReference.source)
            ).distinct()

        if not self.parameter:
            query = query.join(ValueSet.parameter)\
                .filter(Feature.feature_type == 'primary')\
                .filter(Parameter.id != '0')

        if self.language:
            return query\
                .options(joinedload(Value.domainelement))\
                .filter(ValueSet.language_pk.in_(
                    [l.pk for l in [self.language] + self.language.lects]))

        self.vs_lang = aliased(Language)
        if self.parameter:
            query = query.join(ValueSet.contribution)\
                .join(self.vs_lang, ValueSet.language_pk == self.vs_lang.pk)\
                .join(DomainElement)\
                .options(joinedload(Value.domainelement))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

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
                    return self.dt.vs_lang.name.contains(qs)
                return Language.name.contains(qs)

            def order(self):
                if self.dt.parameter:
                    return cast(self.dt.vs_lang.id, Integer)
                if self.dt.language:
                    return ValueSet.language_pk
                return cast(Language.id, Integer)

        lang_col = _ValueLanguageCol(self, 'language', model_col=Language.name)
        if self.language:
            if self.language.lects:
                lang_col.choices = [(l.pk, l.name) for l in [self.language] + self.language.lects]
                lang_col.js_args['sTitle'] = 'lect'
                lang_col.js_args['sDescription'] = 'Some values pertain to sub-lects only'
            else:
                lang_col = None

        frequency_col = FrequencyCol(
            self, '%',
            sDescription='Frequency',
            sClass='center',
            bSearchable=False,
            model_col=Value.frequency,
            input_size='mini')

        if self.parameter:
            return filter(None, [
                name_col,
                frequency_col if self.parameter.multivalued else None,
                lang_col,
                _LinkToMapCol(self),
                DetailsRowLinkCol(self, 'more') if self.parameter.feature_type != 'sociolinguistic' else None,
                RefsCol(self, 'source', bSearchable=False, bSortable=False) if self.parameter.feature_type != 'segment' else None,
            ])
        if self.language:
            return filter(None, [
                _ParameterCol(self, 'parameter', model_col=Parameter.name),
                name_col,
                frequency_col,
                lang_col,
                DetailsRowLinkCol(self, 'more'),
                RefsCol(self, 'source', bSearchable=False, bSortable=False),
            ])
        return [
            _ParameterCol(self, 'parameter', model_col=Parameter.name),
            name_col,
            frequency_col,
            lang_col,
            DetailsRowLinkCol(self, 'more'),
            RefsCol(self, 'source', bSearchable=False, bSortable=False),
        ]


class RegionCol(Col):
    def format(self, item):
        return item.language.region

    def search(self, qs):
        return Lect.region.contains(qs)

    def order(self):
        return Lect.region


class LexifierCol(Col):
    def format(self, item):
        return item.language.lexifier

    def search(self, qs):
        return Lect.lexifier == qs


class ApicsContributions(datatables.Contributions):
    def base_query(self, query):
        return super(ApicsContributions, self).base_query(query).join(Language)

    def col_defs(self):
        return [
            OrderNumberCol(self),
            LinkCol(self, 'name', sTitle='Language'),
            ContributorsCol(self, 'contributors', bSearchable=False, bSortable=False),
            LexifierCol(self, 'lexifier', choices=get_distinct_values(Lect.lexifier)),
            RegionCol(self, 'region', choices=get_distinct_values(Lect.region)),
            CitationCol(self, 'cite', bSearchable=False, bSortable=False),
        ]
