from sqlalchemy import and_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from sqlalchemy.orm import joinedload_all, joinedload

from clld.web import datatables
from clld.web.util.helpers import external_link
from clld.web.datatables.base import (
    LinkToMapCol, Col, LinkCol, IdCol, filter_number, DetailsRowLinkCol,
)
from clld.web.datatables.value import (
    ValueNameCol, ParameterCol, ValueLanguageCol, RefsCol,
)
from clld.db.meta import DBSession
from clld.db.models.common import (
    Value_data, Value, Parameter, Language, ValueSet, ValueSetReference, DomainElement,
    Contribution,
)

from apics.models import Feature, Lect, ApicsContribution


class OrderNumberCol(IdCol):
    def __init__(self, dt, name='id', **kw):
        kw.setdefault('input_size', 'mini')
        kw.setdefault('sClass', 'right')
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
            LinkCol(self, 'name'),
            Col(
                self,
                'feature_type',
                model_col=Feature.feature_type,
                sFilter='primary',
                choices=['primary', 'sociolinguistic', 'segment']),
            WalsCol(self, 'WALS feature', input_size='mini', model_col=Feature.wals_id)]


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.valueset.language

    def get_layer(self, item):
        if item.valueset.parameter.multivalued:
            return -1
        return item.domainelement.name


class FrequencyCol(Col):
    def format(self, item):
        return '%s%%' % round(item.frequency or 100.0, 1)


class _ValueLanguageCol(ValueLanguageCol):
    def get_obj(self, item):
        return item.valueset.language

    def search(self, qs):
        if self.dt.language:
            return ValueSet.language_pk == int(qs)
        return Language.name.contains(qs)


class _ValueNameCol(ValueNameCol):
    def search(self, qs):
        return DomainElement.name.contains(qs)


class Values(datatables.Values):
    def base_query(self, query):
        query = DBSession.query(self.model)\
            .join(ValueSet)\
            .options(joinedload_all(
                Value.valueset, ValueSet.references, ValueSetReference.source)
            ).distinct()

        if not self.parameter:
            query = query.join(ValueSet.parameter)\
                .filter(Feature.feature_type == 'primary')

        if self.language:
            return query\
                .options(joinedload(Value.domainelement))\
                .filter(ValueSet.language_pk.in_(
                    [l.pk for l in [self.language] + self.language.lects]))

        if self.parameter:
            query = query.join(ValueSet.contribution)\
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

        lang_col = _ValueLanguageCol(self, 'language', model_col=Language.name, bSortable=False)
        if self.language:
            if self.language.lects:
                lang_col.choices = [(l.pk, l.name) for l in [self.language] + self.language.lects]
                lang_col.js_args['sTitle'] = 'lect'
                lang_col.js_args['sDecription'] = 'main language or lects'
            else:
                lang_col = None

        frequency_col = FrequencyCol(self, '%', sDescription='Frequency', model_col=Value.frequency, input_size='mini')

        if self.parameter:
            return filter(None, [
                name_col,
                frequency_col if self.parameter.feature_type == 'primary' else None,
                lang_col,
                _LinkToMapCol(self),
                DetailsRowLinkCol(self, 'more') if self.parameter.feature_type != 'segment' else None,
                RefsCol(self, 'source', bSearchable=False, bSortable=False) if self.parameter.feature_type != 'segment' else None,
            ])
        if self.language:
            return filter(None, [
                ParameterCol(self, 'parameter', model_col=Parameter.name),
                name_col,
                frequency_col,
                lang_col,
                DetailsRowLinkCol(self, 'more'),
                RefsCol(self, 'source', bSearchable=False, bSortable=False),
            ])
        return [
            ParameterCol(self, 'parameter', model_col=Parameter.name),
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
        return item.language.base_language

    def search(self, qs):
        return Lect.base_language.contains(qs)


class ApicsContributions(datatables.Contributions):
    def base_query(self, query):
        return super(ApicsContributions, self).base_query(query).join(Language)

    def col_defs(self):
        choices = lambda attr: [r[0] for r in DBSession.query(attr).distinct()]
        region_col = RegionCol(self, 'region', choices=choices(Lect.region))
        lexifier_col = LexifierCol(self, 'lexifier', choices=choices(Lect.base_language))
        cols = super(ApicsContributions, self).col_defs()
        return [OrderNumberCol(self)] + cols[:-1] + [lexifier_col, region_col] + cols[-1:]
