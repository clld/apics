#from requests import get

from clld.web.maps import ParameterMap, LanguageMap as BaseLanguageMap, Map
from clld.web.util.helpers import map_marker_img
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.models.common import Parameter


class LanguageMap(BaseLanguageMap):
    def __init__(self, ctx, req, eid=None):
        super(LanguageMap, self).__init__(ctx.language, req, eid=eid)


class FeatureMap(ParameterMap):
    def get_layers(self):
        if self.ctx.multivalued:
            return [{
                'name': self.ctx.name,
                'url': self.req.resource_url(self.ctx, ext='geojson')}]

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
        return super(FeatureMap, self).get_layers()

    def options(self):
        return {'style_map': 'apics_feature', 'info_query': {'parameter': self.ctx.pk}}

    def legend(self):
        if self.ctx.multivalued:
            def value_li(de):
                return HTML.li(
                    HTML.label(
                        map_marker_img(self.req, de),
                        literal(de.name),
                        #HTML.div('(%s)' % len(de.values), style='float: right;'),
                        style='margin-left: 1em; margin-right: 1em;'))

            return HTML.li(
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
            )
        return ''


class LexifierMap(FeatureMap):
    def __init__(self, ctx, req, eid=None):
        ctx = DBSession.query(Parameter).filter(Parameter.id == '0').one()
        super(LexifierMap, self).__init__(ctx, req, eid=eid)
