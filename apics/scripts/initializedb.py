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
from clld.util import LGR_ABBRS

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

        for id_, name in LGR_ABBRS.items():
            DBSession.add(common.GlossAbbreviation(id=id_, name=name))

        for row in read('References'):
            year = ', '.join(m.group('year') for m in re.finditer('(?P<year>(1|2)[0-9]{3})', row['Year']))
            title = row['Article_title'] or row['Book_title']
            kw = dict(
                id=row['Reference_ID'],
                name=row['Reference_name'],
                description=title,
                authors=row['Authors'],
                year=year,
            )
            p = add(common.Source, 'source', row['Reference_ID'], **kw)
            DBSession.flush()

            for attr in [
                'Additional_information',
                'Article_title',
                'BibTeX_type',
                'Book_title',
                'City',
                'Editors',
                'Full_reference',
                'Issue',
                'Journal',
                'Language_codes',
                'LaTeX_cite_key',
                'Pages',
                'Publisher',
                'Reference_type',
                'School',
                'Series_title',
                'URL',
                'Volume',
            ]:
                if row.get(attr):
                    DBSession.add(common.Source_data(
                        object_pk=p.pk,
                        key=attr,
                        value=row[attr]))

        for row in read('Features'):
            if not row['Feature_code']:
                continue

            wals_id = row['WALS_No.'].split('.')[0].strip()
            if wals_id:
                wals_id += 'A'
            kw = dict(
                name=row['Feature_name'],
                id=row['Feature_code'],
                description=row['Feature_annotation_publication'],
                feature_type='default',
                wals_id=wals_id,
            )
            p = add(models.Feature, 'parameter', row['Feature_code'], **kw)

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
            add(models.Lect, 'language', row['Language_ID'], **kw)
            add(common.Contribution, 'contribution', row['Language_ID'],
                **dict(id=row['Language_ID'], name=row['Language_name']))

        DBSession.flush()

        for row in read('Sociolinguistic_features'):
            kw = dict(
                name='%s (S)' % row['Sociolinguistic_feature_name'],
                id=row['Sociolinguistic_feature_code'],
                feature_type='sociolinguistic',
            )
            p = add(models.Feature, 'parameter', row['Sociolinguistic_feature_code'], **kw)

            names = {}

            for i in range(1, 7):
                id_ = '%s-%s' % (row['Sociolinguistic_feature_code'], i)
                if row['Value%s' % i].strip():
                    name = row['Value%s' % i].strip()
                    if name in names:
                        name += ' (%s)' % i
                    names[name] = 1
                    kw = dict(id=id_, name=name, parameter=p)
                    de = add(common.DomainElement, 'domainelement', id_, **kw)

        DBSession.flush()

        for row in read('Language_references'):
            #common.ContributionReference()
            pass

        lects = defaultdict(lambda: 1)
        lect_map = {}
        records = {}
        for row in read('Data'):
            lid = row['Language_ID']
            if row['Lect_attribute'].lower() != 'my default lect':
                if (row['Language_ID'], row['Lect_attribute']) in lect_map:
                    lid = lect_map[(row['Language_ID'], row['Lect_attribute'])]
                else:
                    lang = data['language'][row['Language_ID']]
                    c = lects[row['Language_ID']]
                    lid = '%s-%s' % (row['Language_ID'], c)
                    kw = dict(
                        name='%s (%s)' % (lang.name, row['Lect_attribute']),
                        id=lid,
                        latitude=lang.latitude,
                        longitude=lang.longitude,
                        description=row['Lect_attribute'],
                        default_lect=False,
                    )
                    add(models.Lect, 'language', lid, **kw)
                    lects[row['Language_ID']] += 1
                    lect_map[(row['Language_ID'], row['Lect_attribute'])] = lid

            if row['Data_record_id'] in records:
                print('%s already seen' % row['Data_record_id'])
                continue
            else:
                records[row['Data_record_id']] = 1

            if row['Comments_on_value_assignment']:
                DBSession.add(models.ParameterContribution(
                    comment=row['Comments_on_value_assignment'],
                    parameter=data['parameter'][row['Feature_code']],
                    contribution=data['contribution'][row['Language_ID']]))

            one_value_found = False
            for i in range(1, 10):
                if row['Value%s_true_false' % i].strip() != 'True':
                    continue

                one_value_found = True
                id_ = '%s-%s' % (row['Data_record_id'], i)
                kw = dict(
                    id=id_,
                    language=data['language'][lid],
                    parameter=data['parameter'][row['Feature_code']],
                    contribution=data['contribution'][row['Language_ID']],
                    domainelement=data['domainelement']['%s-%s' % (row['Feature_code'], i)],
                    confidence=row['Value%s_confidence' % i],
                    frequency=float(row['c_V%s_frequency_normalised' % i]),
                )
                add(common.Value, 'value', id_, **kw)
            if not one_value_found:
                print('Data without values: %s' % row['Data_record_id'])

        DBSession.flush()

        for row in read('Examples'):
            #
            # TODO: honor row['Lect'] -> (row['Language_ID'], row['Lect']) in lect_map!
            #
            if not row['Language_ID'].strip():
                print('example without language: %s' % row['Example_number'])
                continue
            id_ = '%(Language_ID)s-%(Example_number)s' % row

            if not row['Gloss'] or not row['Analyzed_text']:
                print row
                continue

            kw = dict(
                id=id_,
                name=row['Text'],
                description=row['Translation'],
                source=row['Type'],
                comment=row['Comments'],
                gloss='\t'.join(row['Gloss'].split()),
                analyzed='\t'.join((row['Analyzed_text'] or row['Text']).split()),
                #
                # TODO: original_script: find out what encoding is used!
                #
            )
            p = add(common.Sentence, 'sentence', id_, **kw)
            p.language = data['language'][row['Language_ID']]

            if row['Reference_ID']:
                source = data['source'][row['Reference_ID']]
                r = common.SentenceReference(
                    sentence=p,
                    source=source,
                    key=source.id,
                    description=row['Reference_pages'],
                )
                DBSession.add(r)

        DBSession.flush()

        records = {}
        for row in read('Sociolinguistic_data'):
            if row['Sociolinguistic_data_record_id'] in records:
                print('%s already seen' % row['Sociolinguistic_data_record_id'])
                continue
            else:
                records[row['Sociolinguistic_data_record_id']] = 1

            if row['Comments_on_value_assignment']:
                DBSession.add(models.ParameterContribution(
                    comment=row['Comments_on_value_assignment'],
                    parameter=data['parameter'][row['Sociolinguistic_feature_code']],
                    contribution=data['contribution'][row['Language_ID']]))

            one_value_found = False
            for i in range(1, 7):
                if row['Value%s_true_false' % i].strip() != 'True':
                    continue

                if '%s-%s' % (row['Sociolinguistic_feature_code'], i) not in data['domainelement']:
                    print('sociolinguistic data point without domainelement: %s' % row['Sociolinguistic_data_record_id'])
                    continue

                one_value_found = True
                id_ = 's-%s-%s' % (row['Sociolinguistic_data_record_id'], i)
                kw = dict(
                    id=id_,
                    language=data['language'][row['Language_ID']],
                    parameter=data['parameter'][row['Sociolinguistic_feature_code']],
                    contribution=data['contribution'][row['Language_ID']],
                    domainelement=data['domainelement']['%s-%s' % (row['Sociolinguistic_feature_code'], i)],
                    confidence=row['Value%s_confidence' % i],
                )
                add(common.Value, 'value', id_, **kw)
            if not one_value_found:
                print('Sociolinguistic data without values: %s' % row['Sociolinguistic_data_record_id'])

        DBSession.flush()

        for row in read('Data_references'):
            one_value_found = False
            for i in range(1, 10):
                value = '%s-%s' % (row['Data_record_id'], i)
                if value not in data['value']:
                    continue

                one_value_found = True
                if row['Reference_ID'] not in data['source']:
                    print('Reference with unknown source: %s' % row['Reference_ID'])
                    continue
                source = data['source'][row['Reference_ID']]
                r = common.ValueReference(
                    value=data['value'][value],
                    source=source,
                    key=source.id,
                    description=row['Pages'],
                )
                DBSession.add(r)
            if not one_value_found:
                print('Reference with unknown value: %s' % row['Data_record_id'])

        DBSession.flush()

        missing = 0
        for row in read('Value_examples'):
            try:
                DBSession.add(common.ValueSentence(
                    value=data['value']['%(Data_record_id)s-%(Value_number)s' % row],
                    sentence=data['sentence']['%(Language_ID)s-%(Example_number)s' % row],
                    description=row['Notes'],
                ))
            except KeyError:
                missing += 1
        print('%s Value_examples are missing data' % missing)

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
