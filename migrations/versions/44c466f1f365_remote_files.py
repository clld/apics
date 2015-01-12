# coding=utf-8
"""remote files

Revision ID: 44c466f1f365
Revises: 34d43c0d9d31
Create Date: 2014-11-05 14:29:47.194532

"""

# revision identifiers, used by Alembic.
revision = '44c466f1f365'
down_revision = '34d43c0d9d31'

import json
from xml.etree import ElementTree

from alembic import op
import requests


EDMOND_URL = "http://edmond.mpdl.mpg.de/imeji/export?format=xml&type=image&n=10000&col=4WkY1hHhw8iEuNQ4&q="

qname = lambda localname: '{http://imeji.org/terms}' + localname


def get(e, k):
    return e.find(qname(k)).text


def upgrade():
    conn = op.get_bind()
    items = ElementTree.fromstring(requests.get(EDMOND_URL).text)
    for e in items.findall(qname('item')):
        d = dict(id=e.attrib['id'])
        for k in 'full web thumbnail'.split():
            d[k] = get(e, k + 'ImageUrl')
        d['url'] = d['full']
        id_ = get(e, 'filename')
        table = 'contribution_files' if 'gt' in id_ else 'sentence_files'
        conn.execute(
            "update {0} set jsondata = %s where id = %s".format(table),
            (json.dumps(d), id_))


def downgrade():
    pass
