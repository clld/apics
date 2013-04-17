from sqlalchemy import and_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from sqlalchemy.orm import joinedload_all, joinedload

from clld.web import datatables
from clld.web.datatables.base import (
    LinkToMapCol, Col, LinkCol, IdCol, filter_number, DetailsRowLinkCol,
)
from clld.web.datatables.value import (
    ValueNameCol, ParameterCol, ValueLanguageCol, RefsCol,
)
from clld.db.meta import DBSession
from clld.db.models.common import (
    Value_data, Value, Parameter, Language, ValueSet, ValueSetReference, DomainElement,
)

from apics.models import Feature, Lect


class OrderNumberCol(IdCol):
    def search(self, qs):
        return filter_number(cast(self.dt.model.id, Integer), qs, type_=int)

    def order(self):
        return cast(self.dt.model.id, Integer)


class ApicsContributions(datatables.Contributions):
    def col_defs(self):
        return [OrderNumberCol(self, 'id')] + super(ApicsContributions, self).col_defs()


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Parameter.id != '0')

    def col_defs(self):
        return [
            OrderNumberCol(self, 'id'),
            LinkCol(self, 'name'),
            Col(
                self,
                'category',
                model_col=Feature.category,
                choices=[row[0] for row in DBSession.query(
                    Feature.category).order_by(Feature.category).distinct()])]


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.valueset.language

    def get_layer(self, item):
        if item.valueset.parameter.feature_type == 'default':
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
                .filter(Feature.feature_type == 'default')

        if self.language:
            return query\
                .options(joinedload(Value.domainelement))\
                .filter(ValueSet.language_pk.in_(
                    [l.pk for l in [self.language] + self.language.lects]))

        if self.parameter:
            query = query.join(ValueSet.language)\
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
            return [
                name_col,
                frequency_col,
                lang_col,
                _LinkToMapCol(self),
                DetailsRowLinkCol(self, 'more'),
                RefsCol(self, 'references', bSearchable=False, bSortable=False),
            ]
        if self.language:
            return filter(None, [
                ParameterCol(self, 'parameter', model_col=Parameter.name),
                name_col,
                frequency_col,
                lang_col,
                DetailsRowLinkCol(self, 'more'),
                RefsCol(self, 'references', bSearchable=False, bSortable=False),
            ])
        return [
            ParameterCol(self, 'parameter', model_col=Parameter.name),
            name_col,
            frequency_col,
            lang_col,
            DetailsRowLinkCol(self, 'more'),
            RefsCol(self, 'references', bSearchable=False, bSortable=False),
        ]


class Lects(datatables.Languages):
    def base_query(self, query):
        if self.req.matched_route.name == 'languages_alt':
            # the map of all languages is to be displayed
            query = query.filter(Lect.language_pk == None)
        return super(Lects, self).base_query(query)

    def col_defs(self):
        _choices = lambda attr: [
            row[0] for row in DBSession.query(attr).distinct() if row[0]]
        region_col = Col(
            self,
            'region',
            model_col=Lect.region,
            choices=_choices(Lect.region))
        base_language_col = Col(
            self,
            'base_language',
            model_col=Lect.base_language,
            choices=_choices(Lect.base_language))
        return [
            OrderNumberCol(self, 'id'),
            LinkCol(self, 'name'),
            region_col,
            base_language_col,
            LinkToMapCol(self),
        ]
