from requests import get

from clld.web.maps import Map
from clld.web.util.htmllib import HTML, literal


class FeatureMap(Map):
    def get_layers(self):
        layer = Map.get_layers(self)[0]
        layer['name'] = 'APiCS: %s' % self.ctx.name
        layer['zindex'] = 50

        res = []
        if self.ctx.wals_id:
            r = get('http://localhost:8887/feature-info/' + self.ctx.wals_id).json()
            for value in r['values']:
                res.append({
                    'url': self.req.route_url(
                        'wals_proxy',
                        _query={'q': '/parameter/{0}.geojson?domainelement={0}-{1}'.format(
                            self.ctx.wals_id, value['number'])}),
                    'name': 'WALS: %s - %s' % (r['name'], value['name']),
                    'no_select': True,
                    'style_map': 'wals_feature'})
        res.append(layer)
        return res

    def options(self):
        return {'style_map': 'apics_feature', 'info_query': {'parameter': self.ctx.pk}}

    def legend(self):
        def value_li(de):
            return HTML.li(
                HTML.label(
                    HTML.img(
                        src=self.req.static_url(
                            'apics:static/icons/pie-100-%s.png' % de.datadict()['color']),
                        height='20', width='20'),
                    literal(de.name),
                    style='margin-left: 1em; margin-right: 1em;'))

        return HTML.ul(
            HTML.li(
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
            ),
            class_='nav nav-pills'
        )
