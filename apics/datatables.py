from clld.web import datatables

from apics.models import Feature


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.filter(Feature.feature_type == None)
