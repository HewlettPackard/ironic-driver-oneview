#
# Copyright 2016 Hewlett Packard Development Company, LP
# Copyright 2016 Universidade Federal de Campina Grande
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

from neutron_lib.db import model_base
import sqlalchemy as sa


class NeutronOneviewNetwork(model_base.BASEV2):
    __tablename__ = 'neutron_oneview_network'
    neutron_network_id = sa.Column(sa.String(36), primary_key=True)
    oneview_network_id = sa.Column(sa.String(36), nullable=False)
    manageable = sa.Column(sa.Boolean, nullable=False)

    def __init__(
        self, neutron_network_id, oneview_network_id, manageable=True
    ):
        self.neutron_network_id = neutron_network_id
        self.oneview_network_id = oneview_network_id
        self.manageable = manageable


class OneviewNetworkUplinkset(model_base.BASEV2):
    __tablename__ = 'oneview_network_uplinkset'
    oneview_network_id = sa.Column(sa.String(36), primary_key=True)
    oneview_uplinkset_id = sa.Column(sa.String(36), primary_key=True)

    def __init__(self, oneview_network_id, oneview_uplinkset_id):
        self.oneview_network_id = oneview_network_id
        self.oneview_uplinkset_id = oneview_uplinkset_id
