# coding=utf-8
"""fix polymorphic_type

Revision ID: 67337dbafcf
Revises: 34d43c0d9d31
Create Date: 2014-11-26 13:26:55.919000

"""

# revision identifiers, used by Alembic.
revision = '67337dbafcf'
down_revision = '34d43c0d9d31'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['parameter', 'language', 'contribution'], 'base', 'custom')


def downgrade():
    update_pmtype(['parameter', 'language', 'contribution'], 'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))
