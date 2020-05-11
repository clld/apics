"""
recreate the APiCS database from filemaker:

- python apics/scripts/load.py development.ini <fm-host> <fm-user> <fm-password>
- recreatedb.sh apics
- alembic upgrade head
"""
import json
import math
import datetime
import collections

from sqlalchemy.orm import joinedload

from pycldf import Sources
from clldutils.misc import slug
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import compute_language_sources, compute_number_of_values
from clldutils.jsonlib import load as jsonload

from clld.cliutil import Data, bibtex2source, add_language_codes
from clld.lib import bibtex

import apics
from apics import models
from apics.util import SEGMENT_VALUES


def norm(s):
    s = s.replace(u'\u2026', '...')
    s = s.replace('[...]h', '[...] h')
    return s.replace('[...] .', '[...].')


def add_sentence(args, data, id_, **kw):
    p = data.add(common.Sentence, id_, **kw)
    fid = '%s.mp3' % p.id
    if args.data_file('files', 'sentence', p.id, fid).exists():
        common.Sentence_files(object=p, id=fid, name='Audio', mime_type='audio/mpeg')
    return p


def igt(e):
    ao, go = (e['Analyzed_text'] or '').strip(), (e['Gloss'] or '').strip()
    if not ao:
        ao = e['Text']
    assert ao
    if not go:
        return ao, None
    a = norm(ao).split()
    g = norm(go).split()
    if len(a) != len(g):
        for i, m in enumerate(a):
            if m in [
                '~', '/', '*', '(...)', '-', u'\u2013', u'\u2014', '[...]', '[...].'
            ] and (len(g) < i + 1 or g[i] != m) and len(g) < len(a):
                g.insert(i, u'\xa0')
        if len(a) != len(g):
            return ao, go
    return '\t'.join(a), '\t'.join(g)


def round(f):
    """Custom rounding for percent values.

    We basically just take ceiling, thus making smaller percentages relatively bigger.
    """
    return min([100, int(math.ceil(f))])


def main(args):
    data = Data()
    dataset = common.Dataset(
        id='apics',
        name='APiCS Online',
        description='Atlas of Pidgin and Creole Language Structures Online',
        domain='apics-online.info',
        published=datetime.date(2013, 11, 4),
        license='https://creativecommons.org/licenses/by/3.0/',
        contact='apics.contact@gmail.com',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 3.0 Unported License'})
    DBSession.add(dataset)

    for row in sorted(args.cldf['contributors.csv'], key=lambda d: d['editor_ord']):
        c = data.add(
            common.Contributor,
            row['ID'],
            id=row['ID'],
            name=row['Name'],
            address=row['Address'],
            url=row['URL'],
        )
        if row['editor_ord']:
            common.Editor(dataset=dataset, contributor=c, ord=row['editor_ord'])

    DBSession.flush()

    for row in args.cldf['glossabbreviations.csv']:
        DBSession.add(common.GlossAbbreviation(id=row['ID'], name=row['Name']))

    for rec in bibtex.Database.from_file(args.cldf.bibpath):
        data.add(common.Source, slug(rec.id), _obj=bibtex2source(rec))

    DBSession.flush()

    for row in args.cldf['LanguageTable']:
        lect = data.add(
            models.Lect, row['ID'],
            id=row['ID'],
            name=row['Name'],
            latitude=row['Latitude'],
            longitude=row['Longitude'],
            region=row['Region'],
            # FIXME:
            #survey=,
        )
        DBSession.flush()

        if row['Default_Lect_ID']:
            lect.language_pk = data['Lect'][row['Default_Lect_ID']].pk
            continue

        # FIXME: create and add survey, including contributors
        # Survey_Title, Survey_Contributor_ID

        for i, (k, v) in enumerate(
                json.loads(row['Metadata'], object_pairs_hook=collections.OrderedDict).items()):
           DBSession.add(common.Language_data(object_pk=lect.pk, ord=i, key=k, value=v))

        survey_ref_id = None
        for ref in row['Source']:
            sid, desc = Sources.parse(ref)
            if desc == 'survey':
                survey_ref_id = sid
                break

        c = data.add(
            models.ApicsContribution, row['ID'],
            id=row['ID'],
            name=row['Name'],
            description=row['Description'],
            markup_description=row['Description'],
            survey_reference=data['Source'][survey_ref_id] if survey_ref_id else None,
            language=lect)

    #
    # Set language_pk on varieties!
    #


    infobox = jsonload(args.data_file('infobox.json'))
    glottocodes = jsonload(args.data_file('glottocodes.json'))
    for row in read(args, 'Languages', 'Order_number'):

        for ext, label, mtype in [
            ('pdf', 'Glossed text', 'application/pdf'),
            ('mp3', 'Glossed text audio', 'audio/mpeg'),
        ]:
            fid = '%s-gt.%s' % (c.id, ext)
            if args.data_file('files', 'contribution', c.id, fid).exists():
                common.Contribution_files(object=c, id=fid, name=label, mime_type=mtype)
            else:
                print label, 'missing for:', row['Language_name']

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
                    type=common.IdentifierType.iso.value)

            DBSession.add(common.LanguageIdentifier(
                language=data['Lect'][row['Language_ID']],
                identifier=data['Identifier']['iso:%s' % row['ISO_code']]))

        if lect.id in glottocodes:
            identifier = data.add(
                common.Identifier, 'gc:%s' % glottocodes[lect.id],
                id=glottocodes[lect.id],
                name=glottocodes[lect.id],
                type=common.IdentifierType.glottolog.value)

            DBSession.add(common.LanguageIdentifier(
                language=data['Lect'][row['Language_ID']],
                identifier=identifier))

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

    example_count = {}
    for row in read(args, 'Examples', 'Order_number'):
        assert row['Language_ID']
        lang = data['Lect'][row['Language_ID']]
        id_ = '%(Language_ID)s-%(Example_number)s' % row
        atext, gloss = igt(row)
        example_count[row['Language_ID']] = max(
            [example_count.get(row['Language_ID'], 1), row['Example_number']])
        p = add_sentence(
            args, data, id_,
            id='%s-%s' % (lang.id, row['Example_number']),
            name=row['Text'] or row['Analyzed_text'],
            description=row['Translation'],
            type=row['Type'].strip().lower() if row['Type'] else None,
            comment=row['Comments'],
            gloss=gloss,
            analyzed=atext,
            markup_text=normalize_markup(row['z_calc_Text_CSS']),
            markup_gloss=normalize_markup(row['z_calc_Gloss_CSS']),
            markup_comment=normalize_markup(row['z_calc_Comments_CSS']),
            markup_analyzed=normalize_markup(row['z_calc_Analyzed_text_CSS']),
            original_script=row['Original_script'],
            jsondata={
                'sort': row['Order_number'],
                'alt_translation': (row['Translation_other'] or '').strip() or None},
            language=lang)

        if row['Reference_ID']:
            if row['Reference_ID'] in data['Source']:
                source = data['Source'][row['Reference_ID']]
                DBSession.add(common.SentenceReference(
                    sentence=p,
                    source=source,
                    key=source.id,
                    description=row['Reference_pages']))
            else:
                p.source = non_bibs[row['Reference_ID']]

    DBSession.flush()

    for row in read(args, 'Language_references'):
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
    for row in read(args, 'Features', 'Feature_number'):
        id_ = str(row['Feature_number'])
        if int(id_) > feature_count:
            feature_count = int(id_)
        wals_id = None
        desc = row['Feature_annotation_publication']
        if row['WALS_match'] == 'Total':
            if isinstance(row['WALS_No.'], int):
                wals_id = row['WALS_No.']
            else:
                wals_id = int(row['WALS_No.'].split('.')[0].strip())

        p = data.add(
            models.Feature, row['Feature_code'],
            name=row['Feature_name'],
            id=id_,
            description=desc,
            markup_description=normalize_markup(
                row['z_calc_Feature_annotation_publication_CSS']),
            feature_type='primary',
            multivalued=row['Value_relation_type'] != 'Single',
            area=row['Feature_area'],
            wals_id=wals_id)

        names = {}
        for i in range(1, 10):
            if not row['Value%s_publication' % i] \
                    or not row['Value%s_publication' % i].strip():
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
            assert de

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
    for row in read(args, 'Segment_features', 'Order_number'):
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
            primary_to_segment[segment_to_primary[row['Segment_feature_number']]]\
                = str(feature_count)
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

        for i, spec in SEGMENT_VALUES.items():
            data.add(
                common.DomainElement,
                '%s-%s' % (row['Segment_feature_number'], spec[0]),
                id='%s-%s' % (p.id, i),
                name=spec[0],
                parameter=p,
                jsondata={'color': spec[1]},
                number=i)

    print '--> remapped:', primary_to_segment
    DBSession.flush()

    for row in read(args, 'Sociolinguistic_features', 'Sociolinguistic_feature_number'):
        feature_count += 1
        p = data.add(
            models.Feature, row['Sociolinguistic_feature_code'],
            name=row['Sociolinguistic_feature_name'],
            id='%s' % feature_count,
            description=row['Sociolinguistic_feature_annotation'],
            area='Sociolinguistic',
            feature_type='sociolinguistic')

        names = {}

        for i in range(1, 10):
            id_ = '%s-%s' % (row['Sociolinguistic_feature_code'], i)
            if row.get('Value%s' % i) and row['Value%s' % i].strip():
                name = row['Value%s' % i].strip()
                if name in names:
                    name += ' (%s)' % i
                names[name] = 1
            else:
                continue
            kw = dict(id='%s-%s' % (p.id, i), name=name, parameter=p, number=i)
            data.add(
                common.DomainElement,
                id_,
                id='%s-%s' % (p.id, i),
                name=name,
                parameter=p,
                number=i,
                jsondata={'color': colors.get(
                    row['Value%s_colour_ID' % i], colors.values()[i])})

    sd = {}
    for row in read(args, 'Segment_data'):
        if row['Segment_feature_number'] not in number_map:
            continue
        number = number_map[row['Segment_feature_number']]

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
            example_count[row['Language_ID']] += 1
            p = add_sentence(
                args, data, '%s-p%s' % (lang.id, data['Feature'][number].id),
                id='%s-%s' % (lang.id, example_count[row['Language_ID']]),
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
    for row in read(args, 'wals'):
        if row['z_calc_WALS_value_number']:
            wals_value_number[row['Data_record_id']] = row['z_calc_WALS_value_number']

    def prefix(attr, _prefix):
        if _prefix:
            return '%s_%s' % (_prefix, attr)
        return attr.capitalize()

    for _prefix, abbr in [('', ''), ('Sociolinguistic', 'sl')]:
        num_values = 10
        for row in read(args, prefix('data', _prefix)):
            if not row[prefix('feature_code', _prefix)]:
                print('no associated feature for',
                      prefix('data', _prefix),
                      row[prefix('data_record_id', _prefix)])
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
            language = data['Lect'][lid]
            parameter = data['Feature'][row[prefix('feature_code', _prefix)]]
            valueset = common.ValueSet(
                id='%s-%s' % (language.id, parameter.id),
                description=row['Comments_on_value_assignment'],
                markup_description=normalize_markup(
                    row.get('z_calc_Comments_on_value_assignment_CSS')),
            )

            values_found = {}
            for i in range(1, num_values):
                if not row['Value%s_true_false' % i]:
                    continue

                if row['Value%s_true_false' % i].strip().lower() != 'true':
                    assert row['Value%s_true_false' % i].strip().lower() == 'false'
                    false_values[row[prefix('data_record_id', _prefix)]] = 1
                    continue

                iid = '%s-%s' % (row[prefix('feature_code', _prefix)], i)
                if iid not in data['DomainElement']:
                    print(iid,
                          row[prefix('data_record_id', _prefix)],
                          '--> no domainelement!')
                    continue
                values_found['%s-%s' % (id_, i)] = dict(
                    id='%s-%s' % (valueset.id, i),
                    domainelement=data['DomainElement']['%s-%s' % (
                        row[prefix('feature_code', _prefix)], i)],
                    confidence=row['Value%s_confidence' % i],
                    frequency=float(row['c_V%s_frequency_normalised' % i])
                    if _prefix == '' else 100)

            if values_found:
                if row[prefix('data_record_id', _prefix)] in wals_value_number:
                    valueset.jsondata = {
                        'wals_value_number': wals_value_number.pop(
                            row[prefix('data_record_id', _prefix)])}
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
                    seg_id = '%s-%s' % (
                        language.id, primary_to_segment[int(parameter.id)])
                    seg_valueset = data['ValueSet'][seg_id]
                    seg_value = data['Value'][seg_id]
                    if not valueset.description and seg_valueset.description:
                        valueset.description = seg_valueset.description

                    for s in seg_value.sentence_assocs:
                        DBSession.add(
                            common.ValueSentence(value=value, sentence=s.sentence))

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
        for row in read(args, prefix + 'ata_references'):
            assert row['Reference_ID'] in data['Source'] \
                or row['Reference_ID'] in non_bibs
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
                continue

    DBSession.flush()

    missing = 0
    for row in read(args, 'Value_examples'):
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

    for i, row in enumerate(read(args, 'Contributors')):
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
            data = jsonload(path(apics.__file__).dirname().joinpath(
                'static', 'wals', '%sA.json' % feature.wals_id
            ))
            feature.wals_representation = sum(
                [len(l['features']) for l in data['layers']])

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
                valueset.language.lexifier \
                    = valueset.values[0].domainelement.name.replace('-based', '')
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
                assert icons_dir.joinpath('freq-%s.png' % frequency).exists()
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
                colors=['#' + _color for _color in reversed(colors)])
            for wedge in coll[0]:
                wedge.set_linewidth(0.5)
            assert icons_dir.joinpath('%s.png' % basename).exists()
            icons[(fracs, colors)] = True
            assert icons_dir.joinpath(basename + '.svg').exists()

    for de in DBSession.query(common.DomainElement):
        if not de.jsondata.get('icon'):
            de.update_jsondata(icon='pie-100-%s.png' % de.jsondata['color'])

    gbs_func('update', args)


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
