from clld.web.adapters import GeoJsonParameter


def icon(req, values):
    #t = ','.join('%.f' % ((1.0 / len(values)) * 100) for v in values)
    #c = '|'.join(v.domainelement.datadict()['color'] for v in values)
    ##return "http://chart.googleapis.com/chart?cht=p&chs=38x38&chd=t:%s&chco=%s&chf=bg,s,FFFFFF00" % (t, c)
    #return "http://chart.googleapis.com/chart?cht=p&chs=45x45&chd=t:%s&chco=%s&chf=bg,s,FFFFFF00" % (t, c)

    #fracs = [int((1.0 / len(values)) * 100) for v in values]
    fracs = [int(v.frequency) for v in values]
    colors = [v.domainelement.datadict()['color'] for v in values]
    id_ = '-'.join('%s-%s' % (f, c) for f, c in zip(fracs, colors))
    return req.static_url('apics:static/icons/pie-%s.png' % id_)


class GeoJsonFeature(GeoJsonParameter):

    def feature_properties(self, ctx, req, feature):
        language, values = feature
        values = list(values)
        res = GeoJsonParameter.feature_properties(self, ctx, req, (language, values))
        res['icon'] = icon(req, values)
        return res
