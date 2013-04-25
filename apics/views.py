from pyramid.view import view_config
#from pyramid.response import Response
#import requests
#from purl import URL

from clld.web.adapters.md import TxtCitation
from clld.db.meta import DBSession
from clld.db.models.common import Contribution


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {
        'citation': TxtCitation(None),
        'contribution':
        DBSession.query(Contribution).filter(Contribution.id == '58').one()}


@view_config(route_name='legal', renderer='legal.mako')
def legal(request):
    return {}


#@view_config(route_name="wals_proxy")
#def wals(request):
#    url, rel = URL('http://localhost:8887'), URL(request.params['q'])
#    url = url.path(rel.path())
#    url = url.query(rel.query())
#    r = requests.get(url)
#    return Response(r.content, content_type=r.headers['content-type'])
