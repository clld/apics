from pyramid.view import view_config
from io import open
from base64 import b64encode

from path import path

from clld.db.meta import DBSession
from clld.db.models.common import Contributor
from clld.util import jsonload

import apics
from apics.models import ApicsContribution, Feature


def get_html(p):
    with open(p, encoding='utf8') as fp:
        html = fp.read()
    html = html.split('<body')[1]
    html = html.split('</body>')[0]
    return '<div' + html.replace('.popover(', '.clickover(') + '</div>'


def ppath(what, *comps, **kw):
    return path(apics.__file__).dirname().joinpath(
        '..', 'data', 'texts', what, kw.get('processed', 'processed'), *comps)


@view_config(route_name='chapters', renderer='chapters.mako')
def chapters(request):
    ids = [fname.namebase for fname in ppath('Atlas').files('*.html')]
    return {'chapters': [c for c in DBSession.query(Feature) if c.id in ids]}


@view_config(route_name='chapter', renderer='chapter.mako')
def chapter(request):
    _html = get_html(ppath('Atlas', '%s.html' % request.matchdict['id']))
    return {
        'md': jsonload(ppath('Atlas', '%s.json' % request.matchdict['id'])),
        'html': lambda vt: _html.replace('<p>value-table</p>', vt),
        'ctx': Feature.get(request.matchdict['id']),
    }


@view_config(route_name='surveys', renderer='surveys.mako')
def surveys(request):
    ids = {}
    for fname in ppath('Surveys').files('*.html'):
        ids[fname.namebase.split('.')[0]] = fname.namebase
    contribs = {c.id: c for c in DBSession.query(ApicsContribution)}
    return {'surveys': [(ids[id_], contribs[id_]) for id_ in contribs if id_ in ids]}


@view_config(route_name='survey', renderer='survey.mako')
def survey(request):
    id_ = request.matchdict['id']
    md = jsonload(ppath('Surveys', '%s.json' % id_))
    maps = []
    for fname in sorted(
            ppath('Surveys', processed='maps').files(
                            '%s*.png' % id_.split('.')[1].replace('-', '_')),
            key=lambda fn: fn.namebase):
        maps.append(b64encode(open(fname, 'rb').read()))

    return {
        'maps': maps,
        'md': md,
        'authors': [Contributor.get(a['id']) for a in md['authors']],
        'html': get_html(ppath('Surveys', '%s.html' % id_)),
        'ctx': ApicsContribution.get(id_.split('.')[0]),
    }
