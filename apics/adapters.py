from clld.web.adapters import GeoJsonParameter


class GeoJsonFeature(GeoJsonParameter):
    def feature_iterator(self, ctx, req):
        for vs in super(GeoJsonFeature, self).feature_iterator(ctx, req):
            if not vs.language.language_pk:
                yield vs


class GeoJsonApicsWals(GeoJsonParameter):
    def featurecollection_properties(self, ctx, req):
        return self.obj

    def feature_properties(self, ctx, req, vs):
        return {'icon': self.obj['icon']}

    def feature_iterator(self, ctx, req):
        return [vs for vs in ctx.valuesets
                if vs.jsondata.get('wals_value_number') == self.obj['number']]
