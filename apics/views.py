from __future__ import unicode_literals
from pyramid.view import view_config
from io import open
from base64 import b64encode

from clld.db.meta import DBSession
from clld.db.models.common import Contributor
from clldutils.path import Path
from clldutils import jsonlib
from bs4 import BeautifulSoup as bs

import apics
from apics.models import ApicsContribution, Feature


def get_html(p):
    with p.open(encoding='utf8') as fp:
        html = bs(fp.read())

    body = html.find('body')
    body.name = 'div'
    body.attrs.clear()
    return '{0}'.format(body).replace('.popover(', '.clickover(')


def ppath(what, *comps, **kw):
    return Path(apics.__file__).parent.joinpath(
        '..', 'data', 'texts', what, kw.get('processed', 'processed'), *comps)


@view_config(route_name='chapters', renderer='chapters.mako')
def chapters(request):
    ids = [fname.stem for fname in ppath('Atlas').glob('*.html')]
    return {'chapters': [c for c in DBSession.query(Feature) if c.id in ids]}


@view_config(route_name='chapter', renderer='chapter.mako')
def chapter(request):
    _html = get_html(ppath('Atlas', '%s.html' % request.matchdict['id']))
    return {
        'md': jsonlib.load(ppath('Atlas', '%s.json' % request.matchdict['id'])),
        'html': lambda vt: _html.replace('<p>value-table</p>', vt),
        'ctx': Feature.get(request.matchdict['id']),
    }


@view_config(route_name='surveys', renderer='surveys.mako')
def surveys(request):
    ids = {}
    for fname in ppath('Surveys').glob('*.html'):
        ids[fname.stem.split('.')[0]] = fname.stem
    contribs = {c.id: c for c in DBSession.query(ApicsContribution)}
    return {'surveys': [(ids[id_], contribs[id_]) for id_ in contribs if id_ in ids]}


@view_config(route_name='survey', renderer='survey.mako')
def survey(request):
    id_ = request.matchdict['id']
    md = jsonlib.load(ppath('Surveys', '%s.json' % id_))
    html = get_html(ppath('Surveys', '%s.html' % id_))
    maps = []
    for fname in sorted(
            ppath('Surveys', processed='maps').glob(
                            '%s*.png' % id_.split('.')[1].replace('-', '_')),
            key=lambda fn: fn.stem):
        img = b64encode(open(fname.as_posix(), 'rb').read())
        if 'figure' in fname.stem:
            html = html.replace('{%s}' % fname.stem, 'data:image/png;base64,%s' % img)
        else:
            maps.append(img)

    return {
        'maps': maps,
        'md': md,
        'authors': [Contributor.get(a['id']) for a in md['authors']],
        'html': html,
        'ctx': ApicsContribution.get(id_.split('.')[0]),
    }
