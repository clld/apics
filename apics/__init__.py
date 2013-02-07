from pyramid.config import Configurator

from clld import interfaces

from apics import models
from apics.adapters import GeoJsonFeature
from apics.maps import FeatureMap
from apics.datatables import Features

#
# we list the i18n messages from clld core which we want to translate just to have them
# extracted by babel.
#
_ = lambda s: s

_('Parameter')
_('Parameters')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.register_app('apics')

    config.register_map('parameter', FeatureMap)
    config.register_datatable('parameters', Features)

    config.register_adapter(GeoJsonFeature, interfaces.IParameter)

    config.add_route('wals_proxy', '/wals-proxy')
    return config.make_wsgi_app()
