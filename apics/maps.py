from clld.web.maps import Map
from clld.web.util.htmllib import HTML, literal


class FeatureMap(Map):
    def get_layers(self):
        layer = Map.get_layers(self)[0]
        layer['name'] = self.ctx.name
        return [layer]

    def options(self):
        return {'style_map': 'apics_feature'}

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
