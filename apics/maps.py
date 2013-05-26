import json

#from requests import get
from path import path

from clld.web.maps import ParameterMap, LanguageMap as BaseLanguageMap, Map, Layer
from clld.web.util.helpers import map_marker_img, JS
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.models.common import Parameter
from clld.db.util import get_distinct_values
from clld.interfaces import IIcon

import apics
from apics.models import Lect
from apics.adapters import GeoJsonApicsWals


class WalsMap(Map):
    def __init__(self, ctx, req, eid='wals', data=None, value_map=None):
        wals_id = '%sA' % ctx.wals_id
        super(WalsMap, self).__init__(ctx, req, eid=eid)
        self.data = data
        self.value_map = value_map

    def get_layers(self):
        for layer in self.data['layers']:
            yield Layer(
                layer['properties']['number'],
                layer['properties']['name'],
                layer,
                marker=HTML.img(src=self.value_map[layer['properties']['number']]['icon'], height=20, width=20),
                representation=len(layer['features']))

    def options(self):
        return {'hash': True, 'icon_size': 20}


class ApicsWalsMap(WalsMap):
    def __init__(self, ctx, req, eid='apics', data=None, value_map=None):
        super(ApicsWalsMap, self).__init__(ctx, req, eid=eid, data=data, value_map=value_map)

    def get_layers(self):
        for spec in self.value_map.values():
            geojson = GeoJsonApicsWals(spec).render(self.ctx, self.req, dump=False)
            yield Layer(
                spec['number'],
                spec['name'],
                geojson,
                marker=HTML.img(src=spec['icon'], height=20, width=20),
                representation=len(geojson['features']))


class LanguageMap(BaseLanguageMap):
    """small map on contribution detail page
    """
    def __init__(self, ctx, req, eid='map'):
        super(LanguageMap, self).__init__(ctx.language, req, eid=eid)


class FeatureMap(ParameterMap):
    def get_layers(self):
        if self.ctx.multivalued:
            yield Layer(
                self.ctx.id, self.ctx.name, self.req.resource_url(self.ctx, ext='geojson'))

            #layer = ParameterMap.get_layers(self)[0]
            #layer['name'] = 'APiCS: %s' % self.ctx.name
            #layer['zindex'] = 50

            #res = []
            #if self.ctx.wals_id:
            #    r = get('http://localhost:8887/feature-info/' + self.ctx.wals_id).json()
            #    for value in r['values']:
            #        res.append({
            #            'url': self.req.route_url(
            #                'wals_proxy',
            #                _query={
            #                'q': '/parameter/{0}.geojson?domainelement={0}-{1}'.format(
            #                    self.ctx.wals_id, value['number'])}),
            #            'name': 'WALS: %s - %s' % (r['name'], value['name']),
            #            'no_select': True,
            #            'style_map': 'wals_feature'})
            #res.append(layer)
            #return res
        else:
            for layer in super(FeatureMap, self).get_layers():
                yield layer

    def legend(self):
        res = []
        if self.ctx.multivalued:
            def value_li(de):
                return HTML.li(
                    HTML.label(
                        map_marker_img(self.req, de),
                        literal(de.abbr),
                        style='margin-left: 1em; margin-right: 1em;'))

            res.append(HTML.li(
                HTML.a(
                    'Legend',
                    HTML.b(class_='caret'),
                    **{'class': 'dropdown-toggle', 'data-toggle': "dropdown", 'href': "#"}
                ),
                HTML.ul(
                    *[value_li(de) for de in self.ctx.domain],
                    class_='dropdown-menu'
                ),
                class_='dropdown'
            ))

        def li(label, label_class, input_class, onclick, type_='checkbox', name='', checked=False):
            input_attrs = dict(
                type=type_,
                class_=input_class + ' inline',
                name=name,
                value=label,
                onclick=onclick)
            if checked:
                input_attrs['checked'] = 'checked'
            return HTML.li(
                HTML.label(
                    HTML.input(**input_attrs),
                    ' ',
                    label,
                    class_="%s" % label_class,
                    style="margin-left:5px; margin-right:5px;",
                ),
                class_=label_class,
            )

        def lexifier_li(lexifier):
            return li(
                lexifier,
                'stay-open',
                'stay-open lexifier',
                JS("APICS.toggle_languages")(self.eid),
                type_='radio',
                name='lexifier')

        res.append(HTML.li(
            HTML.a(
                'Lexifier',
                HTML.b(class_='caret'),
                **{'class': 'dropdown-toggle', 'data-toggle': "dropdown", 'href': "#"}
            ),
            HTML.ul(
                li('--any--', 'stay-open', 'stay-open lexifier', JS("APICS.toggle_languages")(self.eid), type_="radio", name='lexifier', checked=True),
                *[lexifier_li(l) for l in get_distinct_values(Lect.lexifier)],
                class_='dropdown-menu stay-open'
            ),
            class_='dropdown'
        ))
        return res


class LexifierMap(FeatureMap):
    def __init__(self, ctx, req, eid='map'):
        ctx = DBSession.query(Parameter).filter(Parameter.id == '0').one()
        super(LexifierMap, self).__init__(ctx, req, eid=eid)
