from pyramid.config import Configurator

from clld import interfaces

from apics import views
from apics.adapters import GeoJsonFeature
from apics.maps import FeatureMap


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['mako.directories'] = ['apics:templates', 'clld:web/templates']
    settings['clld.app_template'] = "apics.mako"

    config = Configurator(settings=settings)
    config.add_translation_dirs('apics:locale')
    config.include('clld.web.app')

    config.register_map('parameter', FeatureMap)

    config.register_adapter(
        GeoJsonFeature,
        interfaces.IParameter,
        interfaces.IRepresentation,
        GeoJsonFeature.mimetype)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan(views)
    return config.make_wsgi_app()
