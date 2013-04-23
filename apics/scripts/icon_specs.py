from __future__ import unicode_literals
import sys
from subprocess import check_call
from math import ceil, floor

import transaction
from path import path
from sqlalchemy.orm import joinedload_all, joinedload
import pylab
from pylab import figure, axes, pie, savefig
import matplotlib

from clld.db.meta import DBSession
from clld.db.models import common
from clld.scripts.util import setup_session

import apics


#icons_dir = path(apics.__file__).dirname().joinpath('static', 'icons')
icons_dir = path('/home/robert').joinpath('icons')


def save(basename):
    unrotated = str(icons_dir.joinpath('_%s.png' % basename))
    target = str(icons_dir.joinpath('%s.png' % basename))
    savefig(unrotated, transparent=True)
    check_call(('convert -rotate 270 %s %s' % (unrotated, target)).split())


def round(f):
    return min([100, int(ceil(f))])


def main():
    setup_session(sys.argv[1])

    icons = {}
    frequencies = {}

    with transaction.manager:
        for valueset in DBSession.query(common.ValueSet).options(
            joinedload(common.ValueSet.parameter),
            joinedload_all(common.ValueSet.values, common.Value.domainelement)
        ):
            values = sorted(list(valueset.values), key=lambda v: v.domainelement.number)
            try:
                assert abs(sum(v.frequency for v in values) - 100) < 1
            except AssertionError:
                print valueset.name
                print [v.frequency for v in valueset.values]
                raise

            fracs = []
            colors = []

            for v in values:
                color = v.domainelement.jsondata['color']
                frequency = round(v.frequency)
                assert frequency

                if frequency not in frequencies:
                    figure(figsize=(0.4, 0.4))
                    axes([0.1, 0.1, 0.8, 0.8])
                    coll = pie((int(100 - frequency), frequency), colors=('w', 'k'))
                    coll[0][0].set_linewidth(0.5)
                    save('freq-%s' % frequency)
                    frequencies[frequency] = True

                v.jsondata = {'frequency_icon': 'freq-%s.png' % frequency}
                fracs.append(frequency)
                colors.append(color)
                v.domainelement.jsondata = {
                    'color': color, 'icon': 'pie-100-%s.png' % color}

            assert len(colors) == len(set(colors))
            fracs, colors = tuple(fracs), tuple(colors)

            basename = 'pie-'
            basename += '-'.join('%s-%s' % (f, c) for f, c in zip(fracs, colors))
            valueset.jsondata = {'icon': basename + '.png'}
            if (fracs, colors) not in icons:
                figure(figsize=(0.4, 0.4))
                axes([0.1, 0.1, 0.8, 0.8])
                coll = pie(tuple(reversed(fracs)), colors=['#' + color for color in reversed(colors)])
                for wedge in coll[0]:
                    wedge.set_linewidth(0.5)
                save(basename)
                icons[(fracs, colors)] = True


if __name__ == '__main__':
    main()
