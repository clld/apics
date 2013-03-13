from __future__ import unicode_literals
import sys

from path import path
from sqlalchemy.orm import joinedload_all, joinedload
from pylab import figure, axes, pie, savefig
import matplotlib

from clld.db.meta import DBSession
from clld.db.models import common
from clld.scripts.util import setup_session

import apics


matplotlib.rcParams['lines.linewidth'] = 2


def main():
    setup_session(sys.argv[1])

    icons = {}
    icons_dir = path(apics.__file__).dirname().joinpath('static', 'icons')

    for valueset in DBSession.query(common.ValueSet).options(
        joinedload(common.ValueSet.parameter),
        joinedload_all(common.ValueSet.values, common.Value.domainelement)
    ):
        if valueset.parameter.feature_type != 'default':
            continue

        fracs = tuple(int(v.frequency) for v in valueset.values)
        colors = tuple(v.domainelement.datadict()['color'] for v in valueset.values)

        if (fracs, colors) not in icons:
            figure(figsize=(0.4, 0.4))
            axes([0.1, 0.1, 0.8, 0.8])
            pie(fracs, colors=['#' + color for color in colors])
            id_ = '-'.join('%s-%s' % (f, c) for f, c in zip(fracs, colors))
            #print('writing %s' % id_)
            savefig(str(icons_dir.joinpath('pie-%s.png' % id_)), transparent=True)
            icons[(fracs, colors)] = True


if __name__ == '__main__':
    main()
