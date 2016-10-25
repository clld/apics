# coding=utf-8
"""update lingala

Revision ID: 53ad7f23e30d
Revises: 44c466f1f365
Create Date: 2015-07-09 14:59:20.977488

"""
from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '53ad7f23e30d'
down_revision = '44c466f1f365'

import os
import datetime

from alembic import op
import sqlalchemy as sa

from clldutils.jsonlib import load as jsonload
from clld.db.migration import Connection
from clld.db.models.common import Sentence, ValueSentence, ValueSet, Value, Language
from clldutils.dsv import reader

import apics


def data_file(fname):
    return os.path.join(os.path.dirname(apics.__file__), '..', 'data', fname)


def upgrade():
    conn = Connection(op.get_bind())
    example_map = {}

    sid = 204
    for example in jsonload(data_file('lingala_examples.json')):
        sid += 1
        kw = {
            'id': '60-%s' % sid,
            'language_pk': conn.pk(Language, '60'),
            'name': example['Text'],
            'description': example['Translation'],
            'gloss': '\t'.join(example['Gloss'].split()),
            'analyzed': '\t'.join(example['Text'].split()),
            'type': example['Type'].strip().lower(),
            'jsondata': {'sort': int(example['Order_number']), 'alt_translation': None}
        }
        example_map[example['Example_number']] = conn.insert(Sentence, **kw)

    for ve in jsonload(data_file('lingala_value_examples.json')):
        vspk = conn.pk(ValueSet, '60-%s' % ve['Features::Feature_number'])
        vpk = conn.pk(Value, vspk, attr='valueset_pk')
        conn.insert(
            ValueSentence, value_pk=vpk, sentence_pk=example_map[ve['Example_number']])

    for i, comment in enumerate(reader(data_file('lingala_valueset_comments.tab'), delimiter='\t', dicts=True)):
        vspk = conn.pk(ValueSet, '60-%s' % comment['Features::Feature_number'])
        comment['Comments_on_value_assignment'] = comment['Comments_on_value_assignment'].replace('\x0b', '\n')
        conn.update(
            ValueSet,
            {
                'description': comment['Comments_on_value_assignment'],
                'markup_description': None,
            },
            pk=vspk)


def downgrade():
    pass
