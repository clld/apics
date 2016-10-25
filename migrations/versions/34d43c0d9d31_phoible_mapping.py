# coding=utf-8
"""phoible mapping

Revision ID: 34d43c0d9d31
Revises: None
Create Date: 2014-08-01 11:27:26.695796

"""

# revision identifiers, used by Alembic.
revision = '34d43c0d9d31'
down_revision = None

import datetime
import json
from clldutils.path import Path

from alembic import op
import sqlalchemy as sa


def upgrade():
    mappings = Path(
        __file__).parent.joinpath('..', '..', 'data', 'apics_phoible.json').as_posix()
    with open(mappings) as fp:
        mappings = json.load(fp)

    conn = op.get_bind()
    for k, v in mappings.items():
        d = conn.execute("select jsondata from parameter where id = %s", (k,)).fetchone()
        d = json.loads(d[0])
        d.update(phoible=v)
        conn.execute(
            "update parameter set jsondata = %s where id = %s", (json.dumps(d), k))


def downgrade():
    pass
