from __future__ import unicode_literals
import os
import sys
import transaction
from collections import defaultdict
import csv
import codecs
import re
from cStringIO import StringIO

from path import path

from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import compute_language_sources, compute_number_of_values
from clld.util import LGR_ABBRS, slug
from clld.scripts.util import setup_session, Data

from apics import models


def read(table):
    """Read APiCS data from a csv file exported from filemaker.
    """
    data = path('/home/robert/venvs/clld/data/apics-data')
    with codecs.open(data.joinpath('%s.csv' % table), encoding='utf8') as fp:
        content = StringIO(fp.read().replace('\r', '__newline__').encode('utf8'))
        content.seek(0)

    for item in csv.DictReader(content):
        for key in item:
            item[key] = item[key].decode('utf8').replace('__newline__', '\n')
        yield item


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        usage(sys.argv)

    setup_session(sys.argv[1])
    data = Data()

    with transaction.manager:
        for key, value in {
            'publication.sitetitle':
                'The Atlas of Pidgin and Creole language Structures online',
            'publication.editors': 'Susanne Maria Michaelis, Philippe Maurer, '
                                   'Martin Haspelmath, and Magnus Huber',
            'publication.year': '2013',
            'publication.publisher': 'MPI EVA',
            'publication.place': 'Leipzig',
        }.items():
            DBSession.add(common.Config(key=unicode(key), value=unicode(value)))

        colors = dict((row['ID'], row['RGB_code']) for row in read('Colours'))

        for id_, name in LGR_ABBRS.items():
            DBSession.add(common.GlossAbbreviation(id=id_, name=name))

        for row in read('References'):
            year = ', '.join(
                m.group('year')
                for m in re.finditer('(?P<year>(1|2)[0-9]{3})', row['Year']))
            title = row['Article_title'] or row['Book_title']
            kw = dict(
                id=row['Reference_ID'],
                name=row['Reference_name'],
                description=title,
                authors=row['Authors'],
                year=year,
            )
            p = data.add(common.Source, row['Reference_ID'], **kw)
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
                value = row.get(attr)
                if attr == 'Issue':
                    try:
                        value = str(int(value))
                    except ValueError:
                        pass
                if value:
                    DBSession.add(common.Source_data(
                        object_pk=p.pk,
                        key=attr,
                        value=value))

        feature_count = 0
        for row in read('Features'):
            id_ = row['Feature_number']
            if int(id_) > feature_count:
                feature_count = int(id_)
            wals_id = None
            if row['WALS_match'] == 'Total':
                wals_id = str(int(row['WALS_No.'].split('.')[0].strip())) + 'A'

            p = data.add(
                models.Feature, row['Feature_code'],
                name=row['Feature_name'],
                id=id_,
                description=row['Feature_annotation_publication'],
                feature_type='default',
                multivalued=row['Value_relation_type'] != 'Single',
                category=row['Category'],
                wals_id=wals_id)

            names = {}
            for i in range(1, 10):
                if not row['Value%s_publication' % i].strip():
                    continue
                name = row['Value%s_publication' % i].strip()
                if name in names:
                    name += ' (%s)' % i
                names[name] = 1
                de = data.add(
                    common.DomainElement, '%s-%s' % (row['Feature_code'], i),
                    id='%s-%s' % (id_, i), name=name, parameter=p)
                DBSession.flush()
                DBSession.add(common.DomainElement_data(
                    object_pk=de.pk,
                    key='color',
                    # TODO: fix random color assignment!
                    value=colors.get(
                        row['Value_%s_colour_ID' % i], colors.values()[i])))

        DBSession.flush()

        for row in read('People'):
            #
            # TODO: store alternative email and website in data?
            #
            kw = dict(
                name='%(First name)s %(Last name)s' % row,
                id=slug('%(Last name)s%(First name)s' % row),
                email=row['Contact Email'].split()[0] if row['Contact Email'] else None,
                url=row['Contact Website'].split()[0] if row['Contact Website'] else None,
                address=row['Contact_address'],
            )
            data.add(common.Contributor, row['Author ID'], **kw)

        DBSession.flush()

        for row in read('Languages'):
            lon, lat = [float(c.strip()) for c in row['Coordinates'].split(',')]
            kw = dict(
                name=row['Language_name'],
                id=str(row['Order_number']),
                latitude=lat,
                longitude=lon,
                region=row['Category_region'],
                base_language=row['Category_base_language'],
            )
            lect = data.add(models.Lect, row['Language_ID'], **kw)
            data.add(
                models.ApicsContribution, row['Language_ID'],
                id=row['Order_number'],
                name=row['Language_name'],
                language=lect)

            iso = None
            if len(row['ISO_code']) == 3:
                iso = row['ISO_code'].lower()
                if 'iso:%s' % row['ISO_code'] not in data['Identifier']:
                    data.add(
                        common.Identifier, 'iso:%s' % row['ISO_code'],
                        id=row['ISO_code'].lower(),
                        name=row['ISO_code'].lower(),
                        type='iso639-3')

                DBSession.add(common.LanguageIdentifier(
                    language=data['Lect'][row['Language_ID']],
                    identifier=data['Identifier']['iso:%s' % row['ISO_code']]))

            if row['Language_name_ethnologue']:
                if row['Language_name_ethnologue'] not in data['Identifier']:
                    data.add(
                        common.Identifier, row['Language_name_ethnologue'],
                        id=iso or 'ethnologue:%s' % row['Language_name_ethnologue'],
                        name=row['Language_name_ethnologue'],
                        type='ethnologue')

                DBSession.add(common.LanguageIdentifier(
                    language=data['Lect'][row['Language_ID']],
                    identifier=data['Identifier'][row['Language_name_ethnologue']]))

        DBSession.flush()

        for row in read('Sociolinguistic_features'):
            feature_count += 1
            p = data.add(
                models.Feature, row['Sociolinguistic_feature_code'],
                name='%s (S)' % row['Sociolinguistic_feature_name'],
                id='%s' % feature_count,
                category='Sociolinguistic',
                feature_type='sociolinguistic')

            names = {}

            for i in range(1, 7):
                id_ = '%s-%s' % (row['Sociolinguistic_feature_code'], i)
                if row['Value%s' % i].strip():
                    name = row['Value%s' % i].strip()
                    if name in names:
                        name += ' (%s)' % i
                    names[name] = 1
                else:
                    name = '%s - %s' % (row['Sociolinguistic_feature_name'], i)
                kw = dict(id='%s-%s' % (p.id, i), name=name, parameter=p)
                de = data.add(common.DomainElement, id_, **kw)
                DBSession.flush()
                DBSession.add(common.DomainElement_data(
                    object_pk=de.pk,
                    key='color',
                    value=colors.values()[i]))

        DBSession.flush()

        number_map = {}
        names = {}
        for row in read('Segment_features'):
            truth = lambda s: s.strip().lower() == 'yes'
            name = '%s - %s' % (row['Segment_symbol'], row['Segment_name'])

            if name in names:
                number_map[row['Segment_feature_number']] = names[name]
                continue

            number_map[row['Segment_feature_number']] = row['Segment_feature_number']
            names[name] = row['Segment_feature_number']
            feature_count += 1
            kw = dict(
                name=name,
                id=str(feature_count),
                description=row['Comments'],
                feature_type='segment',
                category='Segment',
                jsondata=dict(
                    number=int(row['Segment_feature_number']),
                    vowel=truth(row['Vowel']),
                    consonant=truth(row['Consonant']),
                    obstruent=truth(row['Obstruent']),
                    core_list=truth(row['Core_list_segment']),
                    symbol=row['Segment_symbol'],
                ),
            )
            p = data.add(models.Feature, row['Segment_feature_number'], **kw)

            for i, de in enumerate([
                u'Exists only as a minor allophone',
                u'Exists only in loanwords',
                u'Exists (as a major allophone)',
                u'Does not exist'
            ]):
                de = data.add(
                    common.DomainElement, '%s-%s' % (row['Segment_feature_number'], de),
                    id='%s-%s' % (p.id, i),
                    name=de,
                    parameter=p)
                DBSession.flush()
                DBSession.add(common.DomainElement_data(
                    object_pk=de.pk,
                    key='color',
                    value=colors.values()[i]))

        DBSession.flush()

        for row in read('Segment_data'):
            if row['Segment_feature_number'] not in number_map:
                continue
            number = number_map[row['Segment_feature_number']]

            #Language_ID,Segment_feature_number,Comments,Audio_file_name,Example_word,
            #Example_word_gloss,Presence_in_the_language,Refers_to_references_Reference_ID
            if not row['Presence_in_the_language']:
                continue

            if number not in data['Feature']:
                print('problem!!')
                continue

            id_ = '%s-%s' % (row['Language_ID'], number)
            valueset = data.add(
                common.ValueSet,
                id_,
                id=id_,
                parameter=data['Feature'][number],
                language=data['Lect'][row['Language_ID']],
                contribution=data['ApicsContribution'][row['Language_ID']],
                description=row['Comments'],
            )
            data.add(
                common.Value,
                id_,
                id=id_,
                valueset=valueset,
                domainelement=data['DomainElement']['%s-%s' % (
                    number, row['Presence_in_the_language'])],
            )
            #
            # TODO: add example constructed from Example_word,Example_word_gloss
            #

        for row in read('Language_references'):
            if row['Reference_ID'] not in data['Source']:
                print('missing source for language: %s' % row['Reference_ID'])
                continue
            if row['Language_ID'] not in data['ApicsContribution']:
                print('missing contribution for language reference: %s'
                      % row['Language_ID'])
                continue
            source = data['Source'][row['Reference_ID']]
            DBSession.add(common.ContributionReference(
                contribution=data['ApicsContribution'][row['Language_ID']],
                source=source,
                description=row['Pages'],
                key=source.id))

        lects = defaultdict(lambda: 1)
        lect_map = {}
        records = {}
        false_values = {}
        no_values = {}

        def prefix(attr, _prefix):
            if _prefix:
                return '%s_%s' % (_prefix, attr)
            return attr.capitalize()

        for _prefix, abbr, num_values in [
            ('', '', 10),
            ('Sociolinguistic', 'sl', 7),
        ]:
            for row in read(prefix('data', _prefix)):
                lid = row['Language_ID']
                lect_attr = row.get('Lect_attribute', 'my default lect').lower()
                if lect_attr != 'my default lect':
                    if (row['Language_ID'], row['Lect_attribute']) in lect_map:
                        lid = lect_map[(row['Language_ID'], row['Lect_attribute'])]
                    else:
                        lang = data['Lect'][row['Language_ID']]
                        c = lects[row['Language_ID']]
                        lid = '%s-%s' % (row['Language_ID'], c)
                        kw = dict(
                            name='%s (%s)' % (lang.name, row['Lect_attribute']),
                            id='%s' % (1000 + 10 * int(lang.id) + c),
                            latitude=lang.latitude,
                            longitude=lang.longitude,
                            description=row['Lect_attribute'],
                            language=lang,
                        )
                        data.add(models.Lect, lid, **kw)
                        lects[row['Language_ID']] += 1
                        lect_map[(row['Language_ID'], row['Lect_attribute'])] = lid

                id_ = abbr + row[prefix('data_record_id', _prefix)]
                if id_ in records:
                    print('%s already seen' % id_)
                    continue
                else:
                    records[id_] = 1

                language = data['Lect'][lid]
                parameter = data['Feature'][row[prefix('feature_code', _prefix)]]
                valueset = data.add(
                    common.ValueSet,
                    id_,
                    id='%s-%s' % (language.id, parameter.id),
                    parameter=parameter,
                    language=language,
                    contribution=data['ApicsContribution'][row['Language_ID']],
                    description=row['Comments_on_value_assignment'],
                )

                values_found = 0
                for i in range(1, num_values):
                    if row['Value%s_true_false' % i].strip() != 'True':
                        if row['Value%s_true_false' % i].strip() == 'False':
                            false_values[row[prefix('data_record_id', _prefix)]] = 1
                        continue

                    #if not _prefix and not float(row['c_V%s_frequency_normalised' % i]) and parameter.multivalued:
                    #    print 'frequency 0 for value %s in dataset %s' % (i, id_)

                    values_found += 1
                    v = data.add(
                        common.Value, '%s-%s' % (id_, i),
                        id='%s-%s' % (valueset.id, i),
                        valueset=valueset,
                        domainelement=data['DomainElement']['%s-%s' % (
                            row[prefix('feature_code', _prefix)], i)],
                        confidence=row['Value%s_confidence' % i],
                        frequency=float(row['c_V%s_frequency_normalised' % i])
                        if _prefix == '' else 100)
                DBSession.flush()

                if not filter(None, [v.frequency for v in valueset.values]):
                    # all values have frequency 0, we can fix that!
                    for v in valueset.values:
                        v.frequency = 100.0 / len(valueset.values)

                if [v for v in valueset.values if v.frequency == 0]:
                    print 'frequency 0 for value %s in dataset %s' % (v.id, id_)

                if not values_found:
                    no_values[id_] = 1
                    #print('Data without values: %s' % row['Data_record_id'])
                if values_found > 1 and not parameter.multivalued:
                    print 'multiple values for single-valued parameter: %s' % id_

        DBSession.flush()

        for row in read('Examples'):
            #
            # TODO: honor row['Lect'] -> (row['Language_ID'], row['Lect']) in lect_map!
            #
            if not row['Language_ID'].strip():
                print('example without language: %s' % row['Example_number'])
                continue
            lang = data['Lect'][row['Language_ID']]
            id_ = '%(Language_ID)s-%(Example_number)s' % row

            atext = row['Analyzed_text'] or row['Text']
            if not row['Gloss'] or not atext:
                print row
                continue

            p = data.add(
                common.Sentence, id_,
                id='%s-%s' % (lang.id, row['Example_number']),
                name=row['Text'],
                description=row['Translation'],
                source=row['Type'],
                comment=row['Comments'],
                gloss='\t'.join(row['Gloss'].split()),
                analyzed='\t'.join(atext.split()),
                original_script=row['Original_script'],
                language=lang)

            if row['Reference_ID']:
                source = data['Source'][row['Reference_ID']]
                DBSession.add(common.SentenceReference(
                    sentence=p,
                    source=source,
                    key=source.id,
                    description=row['Reference_pages'],
                ))

        DBSession.flush()

        for prefix, abbr, num_values in [
            ('D', '', 10),
            ('Sociolinguistic_d', 'sl', 7),
        ]:
            for row in read(prefix + 'ata_references'):
                if row['Reference_ID'] not in data['Source']:
                    print('Reference with unknown source: %s' % row['Reference_ID'])
                    continue
                source = data['Source'][row['Reference_ID']]
                try:
                    DBSession.add(common.ValueSetReference(
                        valueset=data['ValueSet'][abbr + row[prefix + 'ata_record_id']],
                        source=source,
                        key=source.id,
                        description=row['Pages'],
                    ))
                except KeyError:
                    print('Reference for unknown dataset: %s'
                          % row[prefix + 'ata_record_id'])
                    continue

        DBSession.flush()

        missing = 0
        for row in read('Value_examples'):
            try:
                DBSession.add(common.ValueSentence(
                    value=data['Value']['%(Data_record_id)s-%(Value_number)s' % row],
                    sentence=data['Sentence']['%(Language_ID)s-%(Example_number)s' % row],
                    description=row['Notes'],
                ))
            except KeyError:
                missing += 1
        print('%s Value_examples are missing data' % missing)

        print('%s data sets with false values' % len(false_values))
        print('%s data sets without values' % len(no_values))

        for i, row in enumerate(read('Contributors')):
            kw = dict(
                contribution=data['ApicsContribution'][row['Language ID']],
                contributor=data['Contributor'][row['Author ID']]
            )
            if row['Order_of_appearance']:
                kw['ord'] = int(float(row['Order_of_appearance']))
            data.add(common.ContributionContributor, i, **kw)

        DBSession.flush()


def prime_cache():
    setup_session(sys.argv[1])

    with transaction.manager:
        compute_language_sources()
        compute_number_of_values()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main()
    prime_cache()
