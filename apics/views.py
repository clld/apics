import json

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from path import path

from clld.db.meta import DBSession
from clld.db.models.common import Parameter
from clld.interfaces import IIcon
from clld.web.util.helpers import external_link
from clld.web.views import datatable_xhr_view

import apics
from apics.maps import WalsMap, ApicsWalsMap
from apics.datatables import WalsFeatures


@view_config(route_name="credits", renderer='credits.mako')
def credits(req):
    return {}


@view_config(route_name="help", renderer='help.mako')
def help(req):
    return {}


@view_config(route_name="wals_index", renderer='wals_index.mako')
def wals_index(req):
    dt = WalsFeatures(req, Parameter)
    if req.is_xhr and 'sEcho' in req.params:
        return datatable_xhr_view(dt, req)
    return {'dt': dt}


@view_config(route_name="wals", renderer='wals.mako')
def wals(req):
    ctx = DBSession.query(Parameter).filter(Parameter.id == req.matchdict['id']).one()
    wals_data = path(apics.__file__).dirname().joinpath(
        'static', 'wals', '%sA.json' % ctx.wals_id)
    if not wals_data.exists():
        raise HTTPNotFound()

    with open(wals_data, 'r') as fp:
        wals_data = json.load(fp)

    value_map = {}

    for layer in wals_data['layers']:
        for feature in layer['features']:
            feature['properties']['icon'] = req.registry.getUtility(
                IIcon, name=feature['properties']['icon']).url(req)
            feature['properties']['popup'] = external_link(
                'http://wals.info/languoid/lect/wals_code_' + feature['properties']['language']['id'],
                label=feature['properties']['language']['name'])
        value_map[layer['properties']['number']] = {
            'icon': layer['features'][0]['properties']['icon'],
            'name': layer['properties']['name'],
            'number': layer['properties']['number'],
        }

    return {
        'ctx': ctx,
        'wals_data': wals_data,
        'wals_map': WalsMap(ctx, req, data=wals_data, value_map=value_map),
        'apics_map': ApicsWalsMap(ctx, req, data=wals_data, value_map=value_map)}
