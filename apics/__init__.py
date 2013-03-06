from pyramid.config import Configurator

from clld import interfaces

from apics import models
from apics.maps import FeatureMap
from apics.datatables import Features, Values, Lects

#
# we list the i18n messages from clld core which we want to translate just to have them
# extracted by babel.
#
_ = lambda s: s

_('Parameter')
_('Parameters')


def map_marker(ctx, req):
    #t = ','.join('%.f' % ((1.0 / len(values)) * 100) for v in values)
    #c = '|'.join(v.domainelement.datadict()['color'] for v in values)
    ##return "http://chart.googleapis.com/chart?cht=p&chs=38x38&chd=t:%s&chco=%s&chf=bg,s,FFFFFF00" % (t, c)
    #return "http://chart.googleapis.com/chart?cht=p&chs=45x45&chd=t:%s&chco=%s&chf=bg,s,FFFFFF00" % (t, c)

    if interfaces.IValueSet.providedBy(ctx):
        fracs = [int(v.frequency) for v in ctx.values]
        colors = [v.domainelement.datadict()['color'] for v in ctx.values]
        id_ = '-'.join('%s-%s' % (f, c) for f, c in zip(fracs, colors))
        return req.static_url('apics:static/icons/pie-%s.png' % id_)

    if interfaces.IDomainElement.providedBy(ctx):
        dd = ctx.datadict()
        if 'color' in dd:
            return req.static_url('apics:static/icons/pie-100-%s.png' % dd['color'])


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.register_app('apics')

    config.registry.registerUtility(map_marker, interfaces.IMapMarker)

    config.register_map('parameter', FeatureMap)
    config.register_datatable('parameters', Features)
    config.register_datatable('values', Values)
    config.register_datatable('values_alt', Values)
    config.register_datatable('languages', Lects)

    config.add_route('wals_proxy', '/wals-proxy')
    return config.make_wsgi_app()
