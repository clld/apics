from sqlalchemy import and_

from clld.web import datatables
from clld.web.datatables.base import LinkToMapCol, Col, LinkCol
from clld.db.meta import DBSession
from clld.db.models.common import Value_data, Value

from apics.models import Feature, Lect


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Feature.feature_type == 'default')


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.language


class RelativeImportanceCol(Col):
    def format(self, item):
        res = item.datadict().get('relative_importance', '')
        if '_' in res:
            res = res.split('_', 1)[1]
        return res

    def order(self):
        return Value_data.value


class Values(datatables.Values):
    def base_query(self, query):
        query = super(Values, self).base_query(query)
        return query.outerjoin(Value_data, and_(Value.pk == Value_data.object_pk,
                                                Value_data.key == 'relative_importance'))

    def col_defs(self):
        res = super(Values, self).col_defs()
        res.insert(2, RelativeImportanceCol(self, 'relative_importance', bSearchable=False))
        if self.parameter:
            # we have to circumvent the layer selection of the default LinkToMapCol
            res = res[:-1]
            res.append(_LinkToMapCol(self))
        return res


class Lects(datatables.Languages):
    def col_defs(self):
        _choices = lambda attr: [row[0] for row in DBSession.query(attr).distinct() if row[0]]
        region_col = Col(self, 'region', model_col=Lect.region, choices=_choices(Lect.region))
        base_language_col = Col(self, 'base_language', model_col=Lect.base_language, choices=_choices(Lect.base_language))
        return [
            LinkCol(self, 'name'),
            region_col,
            base_language_col,
            LinkToMapCol(self),
        ]
