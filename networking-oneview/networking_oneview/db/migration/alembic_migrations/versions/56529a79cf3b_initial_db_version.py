# Copyright 2016 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""initial db version

Revision ID: 56529a79cf3b
Revises: abd1dbdb47a5
Create Date: 2016-12-16 11:24:37.752589

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56529a79cf3b'
down_revision = None


def upgrade():
    op.create_table(
        'neutron_oneview_network',
        sa.Column('neutron_network_id', sa.String(length=36)),
        sa.Column('oneview_network_id', sa.String(length=36)),
        sa.Column('manageable', sa.Boolean),
        sa.PrimaryKeyConstraint('neutron_network_id')
    )

    op.create_table(
        'oneview_network_uplinkset',
        sa.Column('oneview_network_id', sa.String(length=36)),
        sa.Column('oneview_uplinkset_id', sa.String(length=36)),
        sa.PrimaryKeyConstraint(
            'oneview_network_id', 'oneview_uplinkset_id'
        )
    )
