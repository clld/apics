"""
recreate the APiCS database from CLDF
"""
import re
import json
import math
import datetime
import itertools
import collections

from sqlalchemy.orm import joinedload
from bs4 import BeautifulSoup as bs

from pycldf import Sources
from clldutils.misc import slug, data_url
from clldutils.jsonlib import load as jsonload
from clldutils import svg
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import compute_number_of_values, compute_language_sources

from clld.cliutil import Data, bibtex2source, add_language_codes
from clld.lib import bibtex

from apics import models


def round(f):
    """Custom rounding for percent values.

    We basically just take ceiling, thus making smaller percentages relatively bigger.
    """
    return min([100, int(math.ceil(f))])


def main(args):
    data = Data()
    args.raw = args.cldf.tablegroup._fname.parent / '..' / 'raw'
    DBSession.add(common.Config(
        key='intro',
        value=re.sub(
            r'/static/icons/(?P<fname>[^.]+)\.png',
            lambda m: pie_from_filename(m.group('fname')),
            get_text(args.raw / 'Atlas' / 'Intro.html'))
    ))

    dataset = common.Dataset(
        id='apics',
        name='APiCS Online',
        description='Atlas of Pidgin and Creole Language Structures Online',
        domain='apics-online.info',
        published=datetime.date(2013, 11, 4),
        license='https://creativecommons.org/licenses/by/4.0/',
        contact='apics.contact@gmail.com',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International'})
    DBSession.add(dataset)
    media = {r['ID']: r for r in args.cldf['media.csv']}

    for row in sorted(args.cldf['contributors.csv'], key=lambda d: d['editor_ord'] or 0):
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
    sublect_map = {}

    for row in sorted(args.cldf['LanguageTable'], key=lambda d: int(d['Default_Lect_ID'] or 0)):
        lect = data.add(
            models.Lect, row['ID'],
            id=row['ID'],
            name=row['Name'],
            latitude=row['Latitude'],
            longitude=row['Longitude'],
            region=row['Region'],
            lexifier=row['Lexifier'],
        )
        DBSession.flush()
        add_language_codes(data, lect, row['ISO639P3code'], glottocode=row['Glottocode'])

        if row['Default_Lect_ID']:
            lect.language_pk = data['Lect'][row['Default_Lect_ID']].pk
            sublect_map[row['ID']] = row['Default_Lect_ID']
            continue

        if row['Survey_Title']:
            name, desc = row['Survey_Title'].split('. ', maxsplit=1)
            s = data.add(
                models.Survey, row['ID'], id=row['ID'], name=name, description=desc.strip())
            lect.survey = s
            html, spec = detail_html(args.raw / 'Surveys', row['ID'] if row['ID'] != '51' else '50')
            DBSession.add(
                common.Config(key='survey-{}'.format(row['ID']), value=html, jsondata=spec))

            for i, cid in enumerate(row['Survey_Contributor_ID'], start=1):
                DBSession.add(models.SurveyContributor(
                    survey=s, contributor=data['Contributor'][cid], ord=i))

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
        for i, cid in enumerate(row['Data_Contributor_ID'], start=1):
            DBSession.add(common.ContributionContributor(
                contribution=c, contributor=data['Contributor'][cid], ord=i))

        for ref in row['Source']:
            sid, desc = Sources.parse(ref)
            DBSession.add(common.ContributionReference(
                contribution=c,
                source=data['Source'][sid],
                description=desc,
                key=sid))

        for key in ['Glossed_Text_Audio', 'Glossed_Text_PDF']:
            if row[key]:
                md = media[row[key]]
                objid, orig = md['Name'].split('/')
                common.Contribution_files(
                    object=c,
                    id=orig if row['ID'] != '50' else orig.replace('50', '51'),
                    name='Glossed text',
                    mime_type=md['mimetype'],
                    jsondata=dict(mimetype=md['mimetype'], original=orig, objid=objid, size=md['size'])
                )

        if row['Ethnologue_Name']:
            i = data['Identifier'].get(row['Ethnologue_Name'])
            if not i:
                i = data.add(
                    common.Identifier, row['Ethnologue_Name'],
                    id='ethnologue:%s' % row['Ethnologue_Name'],
                    name=row['Ethnologue_Name'],
                    type='ethnologue')

            DBSession.add(common.LanguageIdentifier(language=lect, identifier=i))

    for i, row in enumerate(args.cldf['ExampleTable'], start=1):
        assert row['Language_ID']
        lang = data['Lect'][row['Language_ID']]
        id_ = row['ID']
        p = data.add(
            common.Sentence, id_,
            id=id_,
            name=row['Primary_Text'],
            description=row['Translated_Text'],
            source=row['source_comment'],
            type=row['Type'],
            comment=row['Comment'],
            gloss='\t'.join(row['Gloss']),
            analyzed='\t'.join(row['Analyzed_Word']),
            markup_text=row['markup_text'],
            markup_gloss=row['markup_gloss'],
            markup_comment=row['markup_comment'],
            markup_analyzed=row['markup_analyzed'],
            original_script=row['original_script'],
            jsondata={'sort': row['sort'], 'alt_translation': row['alt_translation']},
            language=lang)

        if row['Audio']:
            md = media[row['Audio']]
            objid, orig = md['Name'].split('/')
            common.Sentence_files(
                object=p,
                id='{}-{}'.format(row['Audio'], i),
                name='Audio',
                mime_type='audio/mpeg',
                jsondata=dict(mimetype=md['mimetype'], original=orig, objid=objid, size=md['size'])
            )

        for ref in row['Source']:
            sid, desc = Sources.parse(ref)
            DBSession.add(common.SentenceReference(
                sentence=p,
                source=data['Source'][sid],
                key=sid,
                description=desc))

    DBSession.flush()

    codes = {
        fid: list(rows) for fid, rows in itertools.groupby(
            sorted(args.cldf['CodeTable'], key=lambda d: (d['Parameter_ID'], d['ID'])),
            lambda d: d['Parameter_ID'])}

    for row in args.cldf['ParameterTable']:
        p = data.add(
            models.Feature, row['ID'],
            name=row['Name'],
            id=row['ID'],
            description=row['Description'],
            markup_description=row['Description'],
            feature_type=row['Type'],
            multivalued=row['Multivalued'],
            area=row['Area'],
            wals_id=int(row['WALS_ID'].replace('A', '')) if row['WALS_ID'] else None,
            wals_representation=row['WALS_Representation'],
            jsondata=json.loads(row['metadata']),
        )
        html, spec = detail_html(args.raw / 'Atlas', row['ID'])
        if html:
            DBSession.add(
                common.Config(key='atlas-{}'.format(row['ID']), value=html, jsondata=spec))

        if row['Map_Gall_Peters']:
            md = media[row['Map_Gall_Peters']]
            objid, orig = md['Name'].split('/')
            common.Parameter_files(
                object=p,
                id=orig,
                name='Feature map in Gall-Peters projection',
                mime_type=md['mimetype'],
                jsondata=dict(mimetype=md['mimetype'], original=orig, objid=objid, size=md['size'])
            )

        if row['WALS_ID']:
            DBSession.add(models.Wals(
                pk=int(row['ID']),
                id=row['ID'],
                parameter=p,
                jsondata=jsonload(args.raw / 'wals' / '{}.json'.format(row['WALS_ID']))))
        for code in codes.get(row['ID'], []):
            data.add(
                common.DomainElement, code['ID'],
                id=code['ID'],
                name=code['Name'],
                parameter=p,
                abbr=code['abbr'],
                number=code['Number'],
                jsondata={'color': code['color']},
            )
        for i, cid in enumerate(row['Contributor_ID'], start=1):
            models.FeatureAuthor(feature=p, contributor=data['Contributor'][cid], ord=i)

    for vsid, values in itertools.groupby(
        sorted(args.cldf['ValueTable'], key=lambda d: tuple(map(int, d['ID'].split('-')[:2]))),
        lambda d: '-'.join(d['ID'].split('-')[:2])
    ):
        values = list(values)
        if values[0]['Language_ID'] in sublect_map:
            contrib = data['ApicsContribution'][sublect_map[values[0]['Language_ID']]]
        else:
            contrib = data['ApicsContribution'][values[0]['Language_ID']]
        valueset = data.add(
            common.ValueSet,
            vsid,
            id=vsid,
            parameter=data['Feature'][values[0]['Parameter_ID']],
            language=data['Lect'][values[0]['Language_ID']],
            contribution=contrib,
            description=values[0]['Comment'],
            source=values[0]['source_comment'],
            jsondata=json.loads(values[0]['Metadata'] or '{}'),
        )
        for value in values:
            v = data.add(
                common.Value,
                value['ID'],
                id=value['ID'],
                frequency=value['Frequency'],
                confidence=value['Confidence'],
                valueset=valueset,
                domainelement=data['DomainElement'][value['Code_ID']],
            )
            for exid in value['Example_ID']:
                DBSession.add(common.ValueSentence(value=v, sentence=data['Sentence'][exid]))
        for ref in values[0]['Source']:
            sid, desc = Sources.parse(ref)
            DBSession.add(common.ValueSetReference(
                valueset=valueset,
                source=data['Source'][sid],
                key=sid,
                description=desc))


def prime_cache(args):
    #
    # TODO: relate survey chapter reference with language!
    #
    args.log.info('computing wals representation')
    for feature in DBSession.query(common.Parameter).options(
        joinedload(common.Parameter.valuesets)
    ):
        feature.representation = len(feature.valuesets)

    compute_number_of_values()
    compute_language_sources((common.ContributionReference, 'contribution'))

    for valueset in DBSession.query(common.ValueSet)\
            .join(common.Parameter)\
            .filter(common.Parameter.id == '0')\
            .options(joinedload(common.ValueSet.language)):
        if valueset.language.language_pk:
            continue
        if len(valueset.values) > 1:
            assert valueset.language.lexifier == 'Other'
        else:
            if valueset.values[0].domainelement.name == 'Other':
                assert valueset.language.lexifier == 'Other'
            else:
                assert valueset.language.lexifier \
                    == valueset.values[0].domainelement.name.replace('-based', '')
        for lect in valueset.language.lects:
            assert lect.lexifier == valueset.language.lexifier


def get_text(p):
    text = p.read_text(encoding='utf8')
    body = bs(text, 'html5lib').find('body')
    body.name = 'div'
    body.attrs.clear()
    return '{0}'.format(body).replace('.popover(', '.clickover(')


def detail_html(directory, sid):
    html_p = directory / '{}.html'.format(sid)
    if not html_p.exists():
        return None, {}
    html = get_text(html_p)
    maps = []
    for fname in sorted(directory.glob('%s-*.png' % sid), key=lambda p: p.stem):
        data_uri = data_url(fname, 'image/png')
        if 'figure' in fname.stem:
            html = html.replace('{%s}' % fname.name, '%s' % data_uri)
        else:
            maps.append(data_uri)

    return html, {
        'maps': maps,
        'md': jsonload(directory / '{}.json'.format(sid)),
        'css': directory.joinpath('{}.css'.format(sid)).read_text(encoding='utf8'),
    }


def pie_from_filename(fname):
    if fname.startswith('pie-'):
        spec = fname.replace('pie-', '').replace('.png', '').split('-')
    elif fname.startswith('freq-'):
        freq = int(fname.replace('freq-', '').replace('.png', ''))
        spec = [freq, '000000', 100 - freq, 'ffffff']
    else:
        raise ValueError(fname)
    slices = [spec[i:i+2] for i in range(0, len(spec), 2)]
    return svg.data_url(svg.pie(
        [float(p[0]) for p in slices],
        ['#' + p[1] for p in slices],
        stroke_circle=True))
