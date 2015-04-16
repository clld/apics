from pyramid.view import view_config
from io import open

from path import path

from clld.util import jsonload

import apics
from apics.models import ApicsContribution


def get_html(p):
    with open(p, encoding='utf8') as fp:
        html = fp.read()
    html = html.split('<body')[1]
    html = html.split('</body>')[0]
    return '<div' + html + '</div>'


@view_config(route_name='survey', renderer='survey.mako')
def survey(request):
    pdir = path(apics.__file__).dirname().joinpath(
        '..', 'data', 'texts', 'Surveys', 'processed')
    id_ = request.matchdict['id']
    return {
        'md': jsonload(pdir.joinpath('%s.json' % id_)),
        'html': get_html(pdir.joinpath('%s.html' % id_)),
        'ctx': ApicsContribution.get(id_.split('.')[0]),
    }
