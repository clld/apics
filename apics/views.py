from pyramid.view import view_config
from io import open

from path import path

from clld.db.meta import DBSession
from clld.util import jsonload

import apics
from apics.models import ApicsContribution


def get_html(p):
    with open(p, encoding='utf8') as fp:
        html = fp.read()
    html = html.split('<body')[1]
    html = html.split('</body>')[0]
    return '<div' + html.replace('.popover(', '.clickover(') + '</div>'


def ppath(*comps):
    return path(apics.__file__).dirname().joinpath(
        '..', 'data', 'texts', 'Surveys', 'processed', *comps)


@view_config(route_name='surveys', renderer='surveys.mako')
def surveys(request):
    ids = {}
    for fname in ppath().files('*.html'):
        ids[fname.namebase.split('.')[0]] = fname.namebase
    contribs = {c.id: c for c in DBSession.query(ApicsContribution)}
    return {'surveys': [(ids[id_], contribs[id_]) for id_ in contribs if id_ in ids]}


@view_config(route_name='survey', renderer='survey.mako')
def survey(request):
    id_ = request.matchdict['id']
    return {
        'md': jsonload(ppath('%s.json' % id_)),
        'html': get_html(ppath('%s.html' % id_)),
        'ctx': ApicsContribution.get(id_.split('.')[0]),
    }
