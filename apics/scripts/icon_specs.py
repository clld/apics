from __future__ import unicode_literals
import os
import sys
import transaction
from collections import defaultdict
from itertools import groupby
import csv
import codecs
import unicodedata
import re

from path import path
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy.orm import joinedload_all
from pylab import *
import matplotlib

from pyramid.paster import get_appsettings, setup_logging

from clld.db.meta import DBSession, Base
from clld.db.models import common

import apics
from apics import models


matplotlib.rcParams['lines.linewidth'] = 2


def setup_session(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


def main():
    setup_session()

    values = {}
    icons = {}

    for v in DBSession.query(common.Value).options(
        joinedload_all(common.Value.domainelement, common.DomainElement.data)
    ):
        if not v.domainelement.datadict():
            # value of a sociolinguistic or segment feature
            continue
        key = (v.language_pk, v.parameter_pk)
        if key in values:
            values[key].append((v.frequency, v.domainelement.datadict()['color']))
        else:
            values[key] = [(v.frequency, v.domainelement.datadict()['color'])]

    for key, spec in values.items():
        #fracs = [int((1.0 / len(colors)) * 100) for c in colors]
        fracs = [int(s[0]) for s in spec]
        icons[(tuple(fracs), tuple([s[1] for s in spec]))] = 1

    icons_dir = path(apics.__file__).dirname().joinpath('static', 'icons')
    for fracs, colors in icons:
        figure(figsize=(0.4, 0.4))
        axes([0.1, 0.1, 0.8, 0.8])
        pie(fracs, colors=['#' + color for color in colors])
        id_ = '-'.join('%s-%s' % (f, c) for f, c in zip(fracs, colors))
        print('writing %s' % id_)
        savefig(str(icons_dir.joinpath('pie-%s.png' % id_)), transparent=True)


if __name__ == '__main__':
    main()
