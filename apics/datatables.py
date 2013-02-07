from clld.web import datatables
from clld.web.datatables.base import LinkToMapCol

from apics.models import Feature


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Feature.feature_type == 'default')


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.language


class Values(datatables.Values):
    def col_defs(self):
        res = super(Values, self).col_defs()
        if self.parameter:
            res = res[:-1]
            res.append(_LinkToMapCol(self))
        return res
