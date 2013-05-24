from __future__ import unicode_literals
import os
import sys
from collections import defaultdict
import re
import csv
import json
from cStringIO import StringIO
from subprocess import check_call
from math import ceil, floor

import transaction
from sqlalchemy.orm import joinedload, joinedload_all
from path import path
from pylab import figure, axes, pie, savefig

from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import compute_language_sources, compute_number_of_values
from clld.util import LGR_ABBRS, slug
from clld.scripts.util import setup_session, Data

import apics
from apics import models


icons_dir = path(apics.__file__).dirname().joinpath('static', 'icons')
data_dir = path('/home/robert/venvs/clld/data/apics-data')
GLOSS_ABBR_PATTERN = re.compile(
    '(?P<personprefix>1|2|3)?(?P<abbr>[A-Z]+)(?P<personsuffix>1|2|3)?(?=([^a-z]|$))')


def save(basename, recreate=False):
    """saves the current figure from pylab to disc, and rotates it.
    """
    unrotated = str(icons_dir.joinpath('_%s.png' % basename))
    target = icons_dir.joinpath('%s.png' % basename)
    if recreate or not target.exists():
        savefig(unrotated, transparent=True)
        check_call(('convert -rotate 270 %s %s' % (unrotated, target)).split())
        os.remove(unrotated)


def round(f):
    """Custom rounding for percent values.

    We basically just take ceiling, thus making smaller percentages relatively bigger.
    """
    return min([100, int(ceil(f))])


def read(table, sortkey=None):
    """Read APiCS data from a json file created from filemaker's xml export.
    """
    load = lambda t: json.load(open(data_dir.joinpath('%s.json' % t)))
    res = load(table)

    if table == 'Features':
        # merge the data from two other sources:
        secondary = [
            dict((r['Feature_number'], r) for r in load(table + l)) for l in ['p', 'v']]
        for r in res:
            for d in secondary:
                r.update(d[r['Feature_number']])
    if sortkey:
        return sorted(res, key=lambda d: d[sortkey])
    return res


def main():
    setup_session(sys.argv[1])
    data = Data()

    with transaction.manager:
        for key, value in {
            'publication.sitetitle_short': 'APiCS Online',
            'publication.sitetitle':
                'Atlas of Pidgin and Creole Language Structures Online',
            'publication.editors':
                'Michaelis, Susanne Maria & Maurer, Philippe & '
                'Haspelmath, Martin & Huber, Magnus',
            'publication.year': '2013',
            'publication.publisher': 'Max Planck Institute for Evolutionary Anthropology',
            'publication.place': 'Leipzig',
            'publication.domain': 'apics-online.info',
        }.items():
            DBSession.add(common.Config(key=unicode(key), value=unicode(value)))

        colors = dict((row['ID'], row['RGB_code']) for row in read('Colours'))

        abbrs = {}
        for id_, name in LGR_ABBRS.items():
            DBSession.add(common.GlossAbbreviation(id=id_, name=name))
            abbrs[id_] = 1

        for id_, name in {
            'CLIT': 'clitic',
            'IMPF': 'imperfect',
            'INTERM': 'intermediate',
            'NCOMPL': 'noncompletive',
            'NONFUT': 'nonfuture',
            'NPROX': 'nonproximal',
            'NSG': 'nonsingular',
            'PP': 'past participle',
            'PROP': 'proprietive',
            'TMA': 'tense-mood-aspect',
        }.items():
            DBSession.add(common.GlossAbbreviation(id=id_, name=name))
            abbrs[id_] = 1

        with open(data_dir.joinpath('non-lgr-gloss-abbrs.csv'), 'rb') as csvfile:
            for row in csv.reader(csvfile):
                for match in GLOSS_ABBR_PATTERN.finditer(row[1]):
                    if match.group('abbr') not in abbrs:
                        abbrs[match.group('abbr')] = 1
                        DBSession.add(
                            common.GlossAbbreviation(id=match.group('abbr'), name=row[0]))

        non_bibs = {}
        for row in read('References', 'Reference_ID'):
            if row['Reference_type'] == 'Non-bib':
                non_bibs[row['Reference_ID']] = row['Reference_name']
                continue
            if not isinstance(row['Year'], int) and row['Year']:
                year = ', '.join(
                    m.group('year')
                    for m in re.finditer('(?P<year>(1|2)[0-9]{3})', row['Year']))
            elif row['Year']:
                year = str(row['Year'])
            else:
                year = row['Year']
            title = row['Article_title'] or row['Book_title']
            p = data.add(
                common.Source, row['Reference_ID'],
                id=row['Reference_ID'],
                name=row['Reference_name'],
                description=title,
                authors=row['Authors'],
                year=year)
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
                if attr == 'Issue' and value:
                    try:
                        value = str(int(value))
                    except ValueError:
                        pass
                if value:
                    DBSession.add(common.Source_data(
                        object_pk=p.pk,
                        key=attr,
                        value=value))

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
                address=row['Comments on database'],
            )
            data.add(common.Contributor, row['Author ID'], **kw)

        DBSession.flush()

        for row in read('Languages', 'Order_number'):
            lon, lat = [float(c.strip()) for c in row['map_coordinates'].split(',')]
            kw = dict(
                name=row['Language_name'],
                id=str(row['Order_number']),
                latitude=lat,
                longitude=lon,
                region=row['Category_region'],
                #base_language=row['Category_base_language'],
            )
            lect = data.add(models.Lect, row['Language_ID'], **kw)
            data.add(
                models.ApicsContribution, row['Language_ID'],
                id=row['Order_number'],
                name=row['Language_name'],
                language=lect)

            iso = None
            if row['ISO_code'] and len(row['ISO_code']) == 3:
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

        example_count = 0
        for row in read('Examples'):
            #
            # TODO: honor row['Lect'] -> (row['Language_ID'], row['Lect']) in lect_map!
            #
            if not row['Language_ID']:
                print('example without language: %s' % row['Example_number'])
                continue
            lang = data['Lect'][row['Language_ID']]
            id_ = '%(Language_ID)s-%(Example_number)s' % row

            atext = row['Analyzed_text'] or row['Text']
            if not atext:
                print 'example without text %s' % id_
                continue

            example_count = max([example_count, row['Order_number']])
            p = data.add(
                common.Sentence, id_,
                id=str(row['Order_number']),
                name=row['Text'] or row['Analyzed_text'],
                description=row['Translation'],
                type=row['Type'].strip().lower() if row['Type'] else None,
                comment=row['Comments'],
                gloss='\t'.join(row['Gloss'].split()) if row['Gloss'] else None,
                analyzed='\t'.join(atext.split()),
                original_script=row['Original_script'],
                language=lang)

            if row['Reference_ID']:
                if row['Reference_ID'] in data['Source']:
                    source = data['Source'][row['Reference_ID']]
                    DBSession.add(common.SentenceReference(
                        sentence=p,
                        source=source,
                        key=source.id,
                        description=row['Reference_pages'],
                    ))
                else:
                    p.source = non_bibs[row['Reference_ID']]

        DBSession.flush()

        for row in read('Language_references'):
            if row['Reference_ID'] not in data['Source']:
                if row['Reference_ID'] not in non_bibs:
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

        #
        # global counter for features - across feature types
        #
        feature_count = 0
        for row in read('Features', 'Feature_number'):
            id_ = str(row['Feature_number'])
            if int(id_) > feature_count:
                feature_count = int(id_)
            wals_id = None
            if row['WALS_match'] == 'Total':
                if isinstance(row['WALS_No.'], int):
                    wals_id = row['WALS_No.']
                else:
                    wals_id = int(row['WALS_No.'].split('.')[0].strip())

            p = data.add(
                models.Feature, row['Feature_code'],
                name=row['Feature_name'],
                id=id_,
                description=row['Feature_annotation_publication'],
                feature_type='primary',
                multivalued=row['Value_relation_type'] != 'Single',
                area=row['Feature_area'],
                wals_id=wals_id)

            names = {}
            for i in range(1, 10):
                if not row['Value%s_publication' % i] or not row['Value%s_publication' % i].strip():
                    continue
                name = row['Value%s_publication' % i].strip()
                if name in names:
                    name += ' (%s)' % i
                names[name] = 1
                de = data.add(
                    common.DomainElement, '%s-%s' % (row['Feature_code'], i),
                    id='%s-%s' % (id_, i),
                    name=name,
                    parameter=p,
                    abbr=row['Value%s_for_book_maps' % i] if p.id != '0' else name,
                    number=int(row['Value%s_value_number_for_publication' % i]),
                    jsondata={'color': colors[row['Value_%s_colour_ID' % i]]},
                )

        for row in read('Sociolinguistic_features', 'Sociolinguistic_feature_number'):
            feature_count += 1
            p = data.add(
                models.Feature, row['Sociolinguistic_feature_code'],
                name='%s (S)' % row['Sociolinguistic_feature_name'],
                id='%s' % feature_count,
                area='sociolinguistic',
                feature_type='sociolinguistic')

            names = {}

            for i in range(1, 7):
                id_ = '%s-%s' % (row['Sociolinguistic_feature_code'], i)
                if row['Value%s' % i] and row['Value%s' % i].strip():
                    name = row['Value%s' % i].strip()
                    if name in names:
                        name += ' (%s)' % i
                    names[name] = 1
                else:
                    name = '%s - %s' % (row['Sociolinguistic_feature_name'], i)
                kw = dict(id='%s-%s' % (p.id, i), name=name, parameter=p, number=i)
                de = data.add(
                    common.DomainElement,
                    id_,
                    id='%s-%s' % (p.id, i),
                    name=name,
                    parameter=p,
                    number=i,
                    jsondata={'color': colors.values()[i]})

        primary_to_segment = {123: 63, 126: 35, 128: 45, 130: 41}
        segment_to_primary = dict(zip(
            primary_to_segment.values(), primary_to_segment.keys()))
        number_map = {}
        names = {}
        for row in read('Segment_features', 'Order_number'):
            symbol = row['Segment_symbol']
            if row['Segment_name'] == 'voiceless dental/alveolar sibilant affricate':
                print '---->'
                print symbol
                symbol = 't\u0361s'
                print symbol
            truth = lambda s: s and s.strip().lower() == 'yes'
            name = '%s - %s' % (symbol, row['Segment_name'])

            if name in names:
                number_map[row['Segment_feature_number']] = names[name]
                continue

            number_map[row['Segment_feature_number']] = row['Segment_feature_number']
            names[name] = row['Segment_feature_number']
            feature_count += 1
            if row['Segment_feature_number'] in segment_to_primary:
                primary_to_segment[segment_to_primary[row['Segment_feature_number']]] = str(feature_count)
            p = data.add(
                models.Feature, row['Segment_feature_number'],
                name=name,
                id=str(feature_count),
                feature_type='segment',
                area='vowel' if truth(row['Vowel']) else (
                    'obstruent consonant' if truth(row['Obstruent'])
                    else 'sonorant consonant'),
                jsondata=dict(
                    number=int(row['Segment_feature_number']),
                    vowel=truth(row['Vowel']),
                    consonant=truth(row['Consonant']),
                    obstruent=truth(row['Obstruent']),
                    core_list=truth(row['Core_list_segment']),
                    symbol=symbol,
                ))

            for i, spec in enumerate([
                (u'Exists (as a major allophone)', 'FC3535'),
                (u'Exists only as a minor allophone', 'FFB6C1'),
                (u'Exists only in loanwords', 'F7F713'),
                (u'Does not exist', 'FFFFFF'),
            ]):
                data.add(
                    common.DomainElement,
                    '%s-%s' % (row['Segment_feature_number'], spec[0]),
                    id='%s-%s' % (p.id, i + 1),
                    name=spec[0],
                    parameter=p,
                    jsondata={'color': spec[1]},
                    number=i + 1)

        print '--> remapped:', primary_to_segment
        DBSession.flush()

        sd = {}
        for row in read('Segment_data'):
            if row['Segment_feature_number'] not in number_map:
                continue
            number = number_map[row['Segment_feature_number']]

            #Language_ID,Segment_feature_number,Comments,Audio_file_name,Example_word,
            #Example_word_gloss,Presence_in_the_language,Refers_to_references_Reference_ID
            if not row['Presence_in_the_language']:
                continue

            lang = data['Lect'][row['Language_ID']]
            param = data['Feature'][number]
            id_ = '%s-%s' % (lang.id, param.id)
            if id_ in sd:
                if row['c_Record_is_a_duplicate'] == 'Yes':
                    continue
                else:
                    print row
                    raise ValueError
            sd[id_] = 1
            valueset = data.add(
                common.ValueSet,
                id_,
                id=id_,
                parameter=param,
                language=lang,
                contribution=data['ApicsContribution'][row['Language_ID']],
                description=row['Comments'],
            )
            v = data.add(
                common.Value,
                id_,
                id=id_,
                frequency=float(100),
                valueset=valueset,
                domainelement=data['DomainElement']['%s-%s' % (
                    number, row['Presence_in_the_language'])],
            )
            if row['Example_word'] and row['Example_word_gloss']:
                example_count += 1
                p = data.add(
                    common.Sentence, '%s-p%s' % (lang.id, data['Feature'][number].id),
                    id=str(example_count),
                    name=row['Example_word'],
                    description=row['Example_word_gloss'],
                    language=lang)

                DBSession.add(common.ValueSentence(value=v, sentence=p))

            source = data['Source'].get(row['Refers_to_references_Reference_ID'])
            if source:
                DBSession.add(common.ValueSetReference(
                    valueset=valueset, source=source, key=source.id))
            elif row['Refers_to_references_Reference_ID'] in non_bibs:
                valueset.source = non_bibs[row['Refers_to_references_Reference_ID']]

        lects = defaultdict(lambda: 1)
        lect_map = {}
        records = {}
        false_values = {}
        no_values = {}
        wals_value_number = {}
        for row in read('wals'):
            wals_value_number[row['Data_record_id']] = row['z_calc_WALS_value_number']

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

                id_ = abbr + str(row[prefix('data_record_id', _prefix)])
                if id_ in records:
                    print('%s already seen' % id_)
                    continue
                else:
                    records[id_] = 1

                if row[prefix('feature_code', _prefix)] not in data['Feature']:
                    print 'missing feature %s' % row[prefix('feature_code', _prefix)]
                    continue

                language = data['Lect'][lid]
                parameter = data['Feature'][row[prefix('feature_code', _prefix)]]
                valueset = common.ValueSet(
                    id='%s-%s' % (language.id, parameter.id),
                    description=row['Comments_on_value_assignment'],
                )

                values_found = {}
                for i in range(1, num_values):
                    if not row['Value%s_true_false' % i]:
                        continue

                    if row['Value%s_true_false' % i].strip().lower() != 'true':
                        if row['Value%s_true_false' % i].strip().lower() == 'false':
                            false_values[row[prefix('data_record_id', _prefix)]] = 1
                        else:
                            print row['Value%s_true_false' % i].strip().lower()
                            raise ValueError
                        continue

                    values_found['%s-%s' % (id_, i)] = dict(
                        id='%s-%s' % (valueset.id, i),
                        #valueset=valueset,
                        domainelement=data['DomainElement']['%s-%s' % (
                            row[prefix('feature_code', _prefix)], i)],
                        confidence=row['Value%s_confidence' % i],
                        frequency=float(row['c_V%s_frequency_normalised' % i])
                        if _prefix == '' else 100)

                if values_found:
                    if row[prefix('data_record_id', _prefix)] in wals_value_number:
                        valueset.jsondata = {'wals_value_number': wals_value_number[row[prefix('data_record_id', _prefix)]]}
                    valueset.parameter = parameter
                    valueset.language = language
                    valueset.contribution = data['ApicsContribution'][row['Language_ID']]
                    valueset = data.add(common.ValueSet, id_, _obj=valueset)
                    for i, item in enumerate(values_found.items()):
                        if i > 0 and not parameter.multivalued:
                            print 'multiple values for single-valued parameter: %s' % id_
                            break
                        id_, kw = item
                        kw['valueset'] = valueset
                        value = data.add(common.Value, id_, **kw)

                    #
                    # store references to additional data for segments which should be reused
                    # for corresponding primary features!
                    #
                    if int(parameter.id) in primary_to_segment:
                        try:
                            assert len(values_found) == 1
                        except AssertionError:
                            print len(values_found), language.name, parameter.name
                            raise
                        seg_id = '%s-%s' % (language.id, primary_to_segment[int(parameter.id)])
                        seg_valueset = data['ValueSet'][seg_id]
                        seg_value = data['Value'][seg_id]
                        if not valueset.description and seg_valueset.description:
                            valueset.description = seg_valueset.description

                        for s in seg_value.sentence_assocs:
                            DBSession.add(common.ValueSentence(value=value, sentence=s.sentence))

                        for r in seg_valueset.references:
                            DBSession.add(common.ValueSetReference(
                                valueset=valueset, source=r.source, key=r.key))

                        if not valueset.source and seg_valueset.source:
                            valueset.source = seg_valueset.source

                    DBSession.flush()
                else:
                    no_values[id_] = 1

        DBSession.flush()

        for prefix, abbr, num_values in [
            ('D', '', 10),
            ('Sociolinguistic_d', 'sl', 7),
        ]:
            for row in read(prefix + 'ata_references'):
                if row['Reference_ID'] not in data['Source'] and row['Reference_ID'] not in non_bibs:
                    print('Reference with unknown source: %s' % row['Reference_ID'])
                    continue
                try:
                    vs = data['ValueSet'][abbr + str(row[prefix + 'ata_record_id'])]
                    if row['Reference_ID'] in data['Source']:
                        source = data['Source'][row['Reference_ID']]
                        DBSession.add(common.ValueSetReference(
                            valueset=vs,
                            source=source,
                            key=source.id,
                            description=row['Pages'],
                        ))
                    else:
                        if vs.source:
                            vs.source += '; ' + non_bibs[row['Reference_ID']]
                        else:
                            vs.source = non_bibs[row['Reference_ID']]
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

    icons = {}
    frequencies = {}

    with transaction.manager:
        compute_language_sources()
        compute_number_of_values()

        for valueset in DBSession.query(common.ValueSet)\
                .join(common.Parameter)\
                .filter(common.Parameter.id == '0')\
                .options(joinedload(common.ValueSet.language)):
            if valueset.language.language_pk:
                continue
            if len(valueset.values) > 1:
                valueset.language.lexifier = 'Other'
            else:
                valueset.language.lexifier = valueset.values[0].domainelement.name.replace('-based', '')

        for valueset in DBSession.query(common.ValueSet).options(
            joinedload(common.ValueSet.parameter),
            joinedload_all(common.ValueSet.values, common.Value.domainelement)
        ):
            values = sorted(list(valueset.values), key=lambda v: v.domainelement.number)
            assert abs(sum(v.frequency for v in values) - 100) < 1
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
            valueset.update_jsondata(icon=basename + '.png')
            if (fracs, colors) not in icons:
                figure(figsize=(0.4, 0.4))
                axes([0.1, 0.1, 0.8, 0.8])
                coll = pie(
                    tuple(reversed(fracs)),
                    colors=['#' + color for color in reversed(colors)])
                for wedge in coll[0]:
                    wedge.set_linewidth(0.5)
                save(basename)
                icons[(fracs, colors)] = True

        for de in DBSession.query(common.DomainElement):
            if not de.jsondata.get('icon'):
                de.update_jsondata(icon='pie-100-%s.png' % de.jsondata['color'])


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main()
    prime_cache()
