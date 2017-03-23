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

from neutron.db.models_v2 import Network
from neutron.db.models_v2 import Port
try:
    from neutron.db.models.segment import NetworkSegment
except ImportError:
    from neutron.db.segments_db import NetworkSegment
from neutron.plugins.ml2.models import PortBinding

from networking_oneview.db.oneview_network_db import (
    OneviewLogicalInterconnectGroup)
from networking_oneview.db.oneview_network_db import NeutronOneviewNetwork


# Neutron Network
def get_neutron_network(session, id):
    with session.begin(subtransactions=True):
        return session.query(Network).get(id)


def list_neutron_networks(session):
    with session.begin(subtransactions=True):
        return session.query(Network).all()


# Neutron Network Segments
def get_network_segment(session, network_id):
    with session.begin(subtransactions=True):
        return session.query(NetworkSegment).filter_by(
            network_id=network_id).first()


def list_networks_segments(session):
    with session.begin(subtransactions=True):
        return session.query(NetworkSegment).all()


# Neutron Network with Network Segments
def list_networks_and_segments_with_physnet(session):
    with session.begin(subtransactions=True):
        return session.query(Network, NetworkSegment).filter(
            Network.id == NetworkSegment.network_id,
            NetworkSegment.physical_network.isnot(None)).all()


def get_neutron_network_with_segment(session, id):
    with session.begin(subtransactions=True):
        return session.query(Network, NetworkSegment).filter(
            Network.id == id,
            Network.id == NetworkSegment.network_id).first()


def get_port_with_binding_profile(session):
    with session.begin(subtransactions=True):
        return session.query(Port, PortBinding).filter(
            Port.id == PortBinding.port_id,
            PortBinding.profile.isnot(None),
            PortBinding.profile != '').all()


def get_port_with_binding_profile_by_net(session, network_id):
    with session.begin(subtransactions=True):
        return session.query(Port, PortBinding).filter(
            Port.network_id == network_id,
            Port.id == PortBinding.port_id,
            PortBinding.profile.isnot(None),
            PortBinding.profile != '').all()


# OneView Mechanism driver_api
def map_neutron_network_to_oneview(
    session, neutron_network_id, oneview_network_id,
    manageable, mappings
):
    insert_neutron_oneview_network(
        session, neutron_network_id, oneview_network_id, manageable
    )

    if not mappings:
        return
    for lig_id, uplinkset_name in zip(mappings[0::2], mappings[1::2]):
        insert_oneview_network_lig(
            session, oneview_network_id, lig_id, uplinkset_name
        )


# Neutron OneView Network
def list_neutron_oneview_network(session, **kwargs):
    with session.begin(subtransactions=True):
        return session.query(NeutronOneviewNetwork).filter_by(**kwargs).all()


def insert_neutron_oneview_network(
    session, neutron_network_id, oneview_network_id, manageable=True
):
    with session.begin(subtransactions=True):
        net = NeutronOneviewNetwork(
            neutron_network_id, oneview_network_id, manageable)
        session.add(net)


def get_neutron_oneview_network(session, neutron_network_id):
    with session.begin(subtransactions=True):
        return session.query(NeutronOneviewNetwork).filter_by(
            neutron_network_id=neutron_network_id).first()


def delete_neutron_oneview_network(session, **kwargs):
    with session.begin(subtransactions=True):
        session.query(NeutronOneviewNetwork).filter_by(**kwargs).delete()


def list_oneview_network_lig(session, **kwargs):
    with session.begin(subtransactions=True):
        return session.query(OneviewLogicalInterconnectGroup).filter_by(
            **kwargs).all()


def get_oneview_network_lig(session, **kwargs):
    with session.begin(subtransactions=True):
        return session.query(OneviewLogicalInterconnectGroup).filter_by(
            **kwargs).first()


def get_network_lig(session, oneview_network_id):
    with session.begin(subtransactions=True):
        return session.query(OneviewLogicalInterconnectGroup).filter_by(
            oneview_network_id=oneview_network_id).all()


def insert_oneview_network_lig(
    session, oneview_network_id, lig_id, uplinkset_name
):
    with session.begin(subtransactions=True):
        oneview_network_lig = OneviewLogicalInterconnectGroup(
            oneview_network_id, lig_id, uplinkset_name
        )
        session.add(oneview_network_lig)


def delete_oneview_network_lig(session, **kwargs):
    with session.begin(subtransactions=True):
        session.query(OneviewLogicalInterconnectGroup).filter_by(
            **kwargs).delete()
