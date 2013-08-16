from __future__ import unicode_literals
import os
import sys
from collections import defaultdict, OrderedDict
import re
import csv
import json
from cStringIO import StringIO
from subprocess import check_call
from math import ceil, floor
from datetime import date

from sqlalchemy.orm import joinedload, joinedload_all
from path import path
from pylab import figure, axes, pie, savefig

from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import compute_language_sources, compute_number_of_values
from clld.util import LGR_ABBRS, slug
from clld.scripts.util import Data, initializedb, gbs_func
from clld.lib.fmpxml import normalize_markup
from clld.lib.bibtex import EntryType

import apics
from apics import models


icons_dir = path(apics.__file__).dirname().joinpath('static', 'icons')
data_dir = path('/home/robert/venvs/clld/data/apics-data')
files_dir = path('/home/robert/venvs/clld/apics/data/files')
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
        res = sorted(res, key=lambda d: d[sortkey])
    for d in res:
        for k, v in d.items():
            if isinstance(v, unicode):
                #if v.strip() != v:
                #    print '"%s"' % v
                d[k] = v.strip()
        yield d


def main(args):
    data = Data()

    files_dir.rmtree()
    files_dir.mkdir()

    editors = OrderedDict()
    editors['Susanne Maria Michaelis'] = None
    editors['Philippe Maurer'] = None
    editors['Martin Haspelmath'] = None
    editors['Magnus Huber'] = None

    for row in read('People'):
        name = row['First name'] + ' ' if row['First name'] else ''
        name += row['Last name']
        kw = dict(
            name=name,
            id=slug('%(Last name)s%(First name)s' % row),
            url=row['Contact Website'].split()[0] if row['Contact Website'] else None,
            address=row['Comments on database'],
        )
        contrib = data.add(common.Contributor, row['Author ID'], **kw)
        if kw['name'] in editors:
            editors[kw['name']] = contrib

    DBSession.flush()

    dataset = common.Dataset(
        id='apics',
        name='APiCS Online',
        description='Atlas of Pidgin and Creole Language Structures Online',
        domain='apics-online.info',
        published=date(2013, 8, 15),
        license='http://creativecommons.org/licenses/by-sa/3.0/',
        contact='apics@eva.mpg.de',
        jsondata={
            'license_icon': 'http://i.creativecommons.org/l/by-sa/3.0/88x31.png',
            'license_name': 'Creative Commons Attribution-ShareAlike 3.0 Unported License'})
    DBSession.add(dataset)
    for i, editor in enumerate(editors.values()):
        common.Editor(dataset=dataset, contributor=editor, ord=i + 1)

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
        attrs = {}
        jsondata = {}
        for attr, field in {
            'Additional_information': 'note',
            'Article_title': 'title',
            'Book_title': 'booktitle',
            'City': 'address',
            'Editors': 'editor',
            'Full_reference': None,
            'Issue': None,
            'Journal': 'journal',
            'Language_codes': None,
            'LaTeX_cite_key': None,
            'Pages': 'pages',
            'Publisher': 'publisher',
            'Reference_type': 'type',
            'School': 'school',
            'Series_title': 'series',
            'URL': 'url',
            'Volume': 'volume',
        }.items():
            value = row.get(attr)
            if not isinstance(value, int):
                value = (value or '').strip()
            if attr == 'Issue' and value:
                try:
                    value = str(int(value))
                except ValueError:
                    pass
            if value:
                if field:
                    attrs[field] = value
                else:
                    jsondata[attr] = value
        p = data.add(
            common.Source, row['Reference_ID'],
            id=row['Reference_ID'],
            name=row['Reference_name'],
            description=title,
            author=row['Authors'],
            year=year,
            bibtex_type=getattr(EntryType, row['BibTeX_type'] or 'misc'),
            jsondata=jsondata,
            **attrs)
        DBSession.flush()

    DBSession.flush()

    gt = {}
    p = re.compile('[0-9]+\_(?P<name>[^\_]+)\_(GT|Text)')
    for d in data_dir.joinpath('gt').files():
        m = p.search(unicode(d.basename()))
        if m:
            for part in m.group('name').split('&'):
                # make sure we prefer files named "Text_for_soundfile"
                if slug(unicode(part)) not in gt or 'Text_for_' in d.basename():
                    gt[slug(unicode(part))] = d
    gt_audio = {}
    p = re.compile('(?P<name>[^\_]+)(\_[0-9]+)?\.mp3')
    for d in data_dir.joinpath('gt', 'audio').files():
        m = p.search(unicode(d.basename()))
        assert m
        for part in m.group('name').split('&'):
            gt_audio[slug(unicode(part))] = d

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

        if row["Languages_contribution_documentation::Lect_description_checked_status"] == "Checked":
            desc = row.get('Languages_contribution_documentation::Lect description', '')
        else:
            desc = ''

        c = data.add(
            models.ApicsContribution, row['Language_ID'],
            id=row['Order_number'],
            name=row['Language_name'],
            description=desc,
            survey_reference=data['Source'][row['Survey_reference_ID']],
            language=lect)

        if slug(row['Language_name']) in gt:
            f = common.Contribution_files(
                object=c, id='%s-gt.pdf' % c.id, name='Glossed text', mime_type='application/pdf')
            f.create(files_dir, file(gt[slug(row['Language_name'])]).read())
        else:
            print '--- no glossed text for:', row['Language_name']
        if slug(row['Language_name']) in gt_audio:
            f = common.Contribution_files(
                object=c, id='%s-gt.mp3' % c.id, name='Glossed text audio', mime_type='audio/mpeg')
            f.create(files_dir, file(gt_audio[slug(row['Language_name'])]).read())
        else:
            print '--- no audio for:', row['Language_name']

        #
        # TODO: for michif, 75, add link http://www.youtube.com/watch?v=f0C4cODsSyE
        #

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
    for row in read('Examples', 'Order_number'):
        assert row['Language_ID']
        lang = data['Lect'][row['Language_ID']]
        id_ = '%(Language_ID)s-%(Example_number)s' % row

        atext = (row['Analyzed_text'] or '').strip() or row['Text']
        assert atext
        example_count = max([example_count, row['Order_number']])
        p = data.add(
            common.Sentence, id_,
            id='%s-%s' % (lang.id, row['Example_number']),
            name=row['Text'] or row['Analyzed_text'],
            description=row['Translation'],
            type=row['Type'].strip().lower() if row['Type'] else None,
            comment=row['Comments'],
            gloss='\t'.join(row['Gloss'].split()) if row['Gloss'] else None,
            analyzed='\t'.join(atext.split()),
            markup_text=normalize_markup(row['z_calc_Text_CSS']),
            markup_gloss=normalize_markup(row['z_calc_Gloss_CSS']),
            markup_comment=normalize_markup(row['z_calc_Comments_CSS']),
            markup_analyzed=normalize_markup(row['z_calc_Analyzed_text_CSS']),
            original_script=row['Original_script'],
            jsondata={'sort': row['Order_number']},
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
            assert row['Reference_ID'] in non_bibs
            continue
        assert row['Language_ID'] in data['ApicsContribution']
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
            markup_description=normalize_markup(row['z_calc_Feature_annotation_publication_CSS']),
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

        if row['Authors_FeatureArticles']:
            authors, _ = row['Authors_FeatureArticles'].split('and the APiCS')
            authors = authors.strip()
            if authors.endswith(','):
                authors = authors[:-1].strip()
            for i, name in enumerate(authors.split(',')):
                assert name.strip() in editors
                p._authors.append(models.FeatureAuthor(
                    ord=i + 1, contributor=editors[name.strip()]))

        DBSession.flush()

    primary_to_segment = {123: 63, 126: 35, 128: 45, 130: 41}
    segment_to_primary = dict(zip(
        primary_to_segment.values(), primary_to_segment.keys()))
    number_map = {}
    names = {}
    for row in read('Segment_features', 'Order_number'):
        symbol = row['Segment_symbol']
        if row['Segment_name'] == 'voiceless dental/alveolar sibilant affricate':
            symbol = 't\u0361s'
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
            area='Vowels' if truth(row['Vowel']) else (
                'Obstruent consonants' if truth(row['Obstruent'])
                else 'Sonorant consonants'),
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

    for row in read('Sociolinguistic_features', 'Sociolinguistic_feature_number'):
        feature_count += 1
        p = data.add(
            models.Feature, row['Sociolinguistic_feature_code'],
            name=row['Sociolinguistic_feature_name'],
            id='%s' % feature_count,
            area='Sociolinguistic',
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
            assert row['c_Record_is_a_duplicate'] == 'Yes'
            continue
        sd[id_] = 1
        valueset = data.add(
            common.ValueSet,
            id_,
            id=id_,
            parameter=param,
            language=lang,
            contribution=data['ApicsContribution'][row['Language_ID']],
            description=row['Comments'],
            markup_description=normalize_markup(row['z_calc_Comments_CSS']),
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
        if row['z_calc_WALS_value_number']:
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
            if not row[prefix('feature_code', _prefix)]:
                print 'no associated feature for', prefix('data', _prefix), row[prefix('data_record_id', _prefix)]
                continue

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
            assert id_ not in records
            records[id_] = 1

            assert row[prefix('feature_code', _prefix)] in data['Feature']
            #if row[prefix('feature_code', _prefix)] not in data['Feature']:
            #    print row[prefix('feature_code', _prefix)]
            #    print str(row[prefix('data_record_id', _prefix)])
            #    raise ValueError
            language = data['Lect'][lid]
            parameter = data['Feature'][row[prefix('feature_code', _prefix)]]
            valueset = common.ValueSet(
                id='%s-%s' % (language.id, parameter.id),
                description=row['Comments_on_value_assignment'],
                markup_description=normalize_markup(row.get('z_calc_Comments_on_value_assignment_CSS')),
            )

            values_found = {}
            for i in range(1, num_values):
                if not row['Value%s_true_false' % i]:
                    continue

                if row['Value%s_true_false' % i].strip().lower() != 'true':
                    assert row['Value%s_true_false' % i].strip().lower() == 'false'
                    false_values[row[prefix('data_record_id', _prefix)]] = 1
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
                    valueset.jsondata = {'wals_value_number': wals_value_number.pop(row[prefix('data_record_id', _prefix)])}
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
                    assert len(values_found) == 1
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
            assert row['Reference_ID'] in data['Source'] or row['Reference_ID'] in non_bibs
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

    for k, v in wals_value_number.items():
        print 'unclaimed wals value number:', k, v

    for i, row in enumerate(read('Contributors')):
        kw = dict(
            contribution=data['ApicsContribution'][row['Language ID']],
            contributor=data['Contributor'][row['Author ID']]
        )
        if row['Order_of_appearance']:
            kw['ord'] = int(float(row['Order_of_appearance']))
        data.add(common.ContributionContributor, i, **kw)

    DBSession.flush()


def prime_cache(args):
    #
    # TODO: relate survey chapter reference with language!
    #
    icons = {}
    frequencies = {}

    args.log.info('computing wals representation')
    for feature in DBSession.query(common.Parameter).options(
        joinedload(common.Parameter.valuesets)
    ):
        feature.representation = len(feature.valuesets)
        if feature.wals_id:
            with open(path(apics.__file__).dirname().joinpath(
                'static', 'wals', '%sA.json' % feature.wals_id
            ), 'r') as fp:
                data = json.load(fp)
            feature.wals_representation = sum([len(l['features']) for l in data['layers']])

    args.log.info('computing language sources')
    compute_language_sources((common.ContributionReference, 'contribution'))
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
            if valueset.values[0].domainelement.name == 'Other':
                valueset.language.lexifier = 'Other'
            else:
                valueset.language.lexifier = valueset.values[0].domainelement.name.replace('-based', '')
        for lect in valueset.language.lects:
            lect.lexifier = valueset.language.lexifier

    args.log.info('creating icons')
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

    gbs_func('update', args)


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
