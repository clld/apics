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

from pyramid.paster import get_appsettings, setup_logging

from clld.db.meta import DBSession, Base
from clld.db.models import common

from apics import models


def slug(s):
    res = ''.join((c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn'))
    res = res.lower()
    res = re.sub('\s+|\.|\-', '', res)
    assert re.match('[a-z]+$', res)
    return res


def read(table):
    data = path('/home/robert/venvs/clld/data/apics-data')
    with codecs.open(data.joinpath('%s.csv' % table), encoding='utf8') as fp:
        content = fp.read()

    with codecs.open('%s.csv' % table, 'w', encoding='utf8') as fp:
        fp.write(content.replace('\r', '__newline__'))

    for item in csv.DictReader(open('%s.csv' % table)):
        for key in item:
            item[key] = item[key].decode('utf8').replace('__newline__', '\n')
        yield item


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


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

    data = defaultdict(dict)

    def add(model, type, key, **kw):
        new = model(**kw)
        data[type][key] = new
        DBSession.add(new)
        return new

    with transaction.manager:
        colors = dict((row['ID'], row['RGB_code']) for row in read('Colours'))

        for row in read('Features'):
            kw = dict(
                name=row['Feature_name'],
                id=row['Feature_code'],
                description=row['Feature_annotation_publication'],
            )
            p = add(common.Parameter, 'parameter', row['Feature_code'], **kw)

            names = {}

            for i in range(1, 10):
                id_ = '%s-%s' % (row['Feature_code'], i)
                if row['Value%s' % i].strip() or row['Value%s_publication' % i].strip():
                    name = row['Value%s_publication' % i].strip()
                    if not name:
                        name = row['Value%s' % i].strip()
                    if name in names:
                        name += ' (%s)' % i
                    names[name] = 1
                    kw = dict(id=id_, name=name, parameter=p)
                    de = add(common.DomainElement, 'domainelement', id_, **kw)
                    DBSession.flush()
                    d = common.DomainElement_data(
                        object_pk=de.pk,
                        key='color',
                        # TODO: fix random color assignment!
                        value=colors.get(row['Value_%s_colour_ID' % i], colors.values()[0]))
                    DBSession.add(d)

        DBSession.flush()

        for row in read('People'):
            kw = dict(
                name='%(First name)s %(Last name)s' % row,
                id=slug('%(Last name)s%(First name)s' % row),
                email=row['Contact Email'],
                url=row['Contact Website'],
            )
            add(common.Contributor, 'contributor', row['Author ID'], **kw)

        DBSession.flush()

        for row in read('Languages'):
            try:
                lon, lat = [float(c.strip()) for c in row['Coordinates'].split(',')]
            except:
                print row['Coordinates']
                raise
            kw = dict(
                name=row['Language_name'], id=row['Language_ID'], latitude=lat, longitude=lon,
            )
            add(common.Language, 'language', row['Language_ID'], **kw)
            add(common.Contribution, 'contribution', row['Language_ID'],
                **dict(id=row['Language_ID'], name=row['Language_name']))

        DBSession.flush()

        records = {}
        for row in read('Data'):
            if row['Data_record_id'] in records:
                print('%s already seen' % row['Data_record_id'])
                continue
            else:
                records[row['Data_record_id']] = 1
            for i in range(1, 10):
                if row['Value%s_true_false' % i].strip() != 'True':
                    continue

                id_ = '%s-%s' % (row['Data_record_id'], i)
                kw = dict(
                    id=id_,
                    language=data['language'][row['Language_ID']],
                    parameter=data['parameter'][row['Feature_code']],
                    contribution=data['contribution'][row['Language_ID']],
                    domainelement=data['domainelement']['%s-%s' % (row['Feature_code'], i)],
                )
                add(common.Value, 'cc', id_, **kw)

        DBSession.flush()

        for i, row in enumerate(read('Contributors')):
            kw = dict(
                contribution=data['contribution'][row['Language ID']],
                contributor=data['contributor'][row['Author ID']]
            )
            if row['Order_of_appearance']:
                kw['ord'] = int(float(row['Order_of_appearance']))
            add(common.ContributionContributor, 'cc', i, **kw)

        DBSession.flush()


def prime_cache():
    setup_session()

    with transaction.manager:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main()
    prime_cache()
