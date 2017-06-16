from __future__ import unicode_literals
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from clld.db.meta import DBSession
from clld.db.models.common import Contributor
from clld.web.util.htmllib import HTML
from clldutils import jsonlib

from apics.models import ApicsContribution, Feature
from apics.util import get_text, text_path, get_data_uri


@view_config(route_name='chapters', renderer='chapters.mako')
def chapters(request):
    ids = [fname.stem for fname in text_path('Atlas').glob('*.html')]
    return {'chapters': [c for c in DBSession.query(Feature) if c.id in ids]}


@view_config(route_name='chapter', renderer='chapter.mako')
def chapter(request):
    try:
        _html = get_text('Atlas', request.matchdict['id'], 'html')
    except ValueError:
        raise HTTPNotFound()
    return {
        'md': get_text('Atlas', request.matchdict['id'], 'json'),
        'html': lambda vt: _html.replace('<p>value-table</p>', HTML.div(vt)),
        'css': get_text('Atlas', request.matchdict['id'], 'css'),
        'ctx': Feature.get(request.matchdict['id']),
    }


@view_config(route_name='surveys', renderer='surveys.mako')
def surveys(request):
    ids = [fname.stem for fname in text_path('Surveys').glob('*.html')]
    contribs = {c.id: c for c in DBSession.query(ApicsContribution)}
    return {'surveys': [(id_, contribs[id_]) for id_ in contribs if id_ in ids]}


@view_config(route_name='survey', renderer='survey.mako')
def survey(request):
    id_ = request.matchdict['id']
    try:
        md = get_text('Surveys', id_, 'json')
        html = get_text('Surveys', id_, 'html')
    except ValueError:
        raise HTTPNotFound()
    maps = []
    for fname in sorted(text_path('Surveys').glob('%s-*.png' % id_), key=lambda p: p.stem):
        data_uri = get_data_uri(fname)
        if 'figure' in fname.stem:
            html = html.replace('{%s}' % fname.name, '%s' % data_uri)
        else:
            maps.append(data_uri)

    return {
        'maps': maps,
        'md': md,
        'authors': [Contributor.get(a['id']) for a in md.get('authors', [])],
        'html': html,
        'css': get_text('Surveys', id_, 'css'),
        'ctx': ApicsContribution.get(id_, default=None),
    }
