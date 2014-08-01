from clld.web.maps import ParameterMap, LanguageMap as BaseLanguageMap, Map, Layer, Legend
from clld.web.util.helpers import map_marker_img, JS
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.models.common import Parameter
from clld.db.util import get_distinct_values

from apics.models import Lect
from apics.adapters import GeoJsonApicsWals


class WalsMap(Map):
    def __init__(self, ctx, req, eid='wals', data=None, value_map=None):
        super(WalsMap, self).__init__(ctx, req, eid=eid)
        self.data = data
        self.value_map = value_map

    def get_layers(self):
        for layer in self.data['layers']:
            yield Layer(
                layer['properties']['number'],
                layer['properties']['name'],
                layer,
                marker=HTML.img(
                    src=self.value_map[layer['properties']['number']]['icon'],
                    height=20,
                    width=20),
                representation=len(layer['features']))

    def get_options(self):
        return {'hash': True, 'icon_size': 20}


class ApicsWalsMap(WalsMap):
    def __init__(self, ctx, req, eid='apics', data=None, value_map=None):
        super(ApicsWalsMap, self).__init__(
            ctx, req, eid=eid, data=data, value_map=value_map)

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
    def get_options(self):
        return {'max_zoom': 6, 'icon_size': 25}

    def get_layers(self):
        if self.ctx.multivalued:
            yield Layer(
                self.ctx.id,
                self.ctx.name,
                self.req.resource_url(self.ctx, ext='geojson'))
        else:
            for layer in super(FeatureMap, self).get_layers():
                yield layer

    def get_legends(self):
        if self.ctx.multivalued:
            def value_li(de):
                return HTML.label(
                    map_marker_img(self.req, de),
                    literal(de.abbr),
                    style='margin-left: 1em; margin-right: 1em;')

            yield Legend(self, 'values', map(value_li, self.ctx.domain), label='Legend')

        def li(label,
               label_class,
               input_class,
               onclick,
               type_='checkbox',
               name='',
               checked=False):
            input_attrs = dict(
                type=type_,
                class_=input_class + ' inline',
                name=name,
                value=label,
                onclick=onclick)
            if checked:
                input_attrs['checked'] = 'checked'
            return HTML.label(
                HTML.input(**input_attrs),
                ' ',
                label,
                class_="%s" % label_class,
                style="margin-left:5px; margin-right:5px;",
            )

        def lexifier_li(lexifier):
            return li(
                lexifier,
                'stay-open',
                'stay-open lexifier',
                JS("APICS.toggle_languages")(self.eid),
                type_='radio',
                name='lexifier')

        for legend in super(FeatureMap, self).get_legends():
            yield legend

        items = [li(
            '--any--',
            'stay-open',
            'stay-open lexifier',
            JS("APICS.toggle_languages")(self.eid),
            type_="radio",
            name='lexifier',
            checked=True)]
        for l in get_distinct_values(
            Lect.lexifier, key=lambda v: 'z' + v if v == 'Other' else v
        ):
            items.append(lexifier_li(l))

        yield Legend(self, 'lexifier', items, stay_open=True)


class LexifierMap(FeatureMap):
    def __init__(self, ctx, req, eid='map'):
        ctx = DBSession.query(Parameter).filter(Parameter.id == '0').one()
        super(LexifierMap, self).__init__(ctx, req, eid=eid)


def includeme(config):
    config.register_map('contribution', LanguageMap)
    config.register_map('contributions', LexifierMap)
    config.register_map('parameter', FeatureMap)
