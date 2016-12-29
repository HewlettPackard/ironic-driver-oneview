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
from neutron.plugins.ml2.models import PortBinding
from sqlalchemy import event
from neutron.db.segments_db import NetworkSegment

from networking_oneview.db.oneview_network_db import NeutronOneviewNetwork
from networking_oneview.db.oneview_network_db import OneviewNetworkUplinkset
from networking_oneview.db import oneview_network_db


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
        return session.query(
            NetworkSegment
        ).filter_by(
            network_id=network_id
        ).first()


def list_networks_segments(session):
    with session.begin(subtransactions=True):
        return session.query(NetworkSegment).all()


# Neutron Network with Network Segments
def list_networks_and_segments_with_physnet(session):
    with session.begin(subtransactions=True):
        return session.query(
            Network, NetworkSegment
        ).filter(
            Network.id == NetworkSegment.network_id,
            NetworkSegment.physical_network.isnot(None)
        ).all()


def get_neutron_network_with_segment(session, id):
    with session.begin(subtransactions=True):
        return session.query(
            Network, NetworkSegment
        ).filter(
            Network.id == id,
            Network.id == NetworkSegment.network_id
        ).first()


# Neutron Ports
# def get_port_by_mac_address(session, mac_address):
#     with session.begin(subtransactions=True):
#         return session.query(
#             Port
#         ).filter_by(
#             mac_address=mac_address
#         ).first()
#
#
# def list_port_with_network(session, network_id):
#     with session.begin(subtransactions=True):
#         return session.query(
#             Port
#         ).filter(
#             Port.network_id == network_id
#         ).all()


def get_port_with_binding_profile(session):
    with session.begin(subtransactions=True):
        return session.query(
            Port, PortBinding
        ).filter(
            Port.id == PortBinding.port_id,
            PortBinding.profile.isnot(None),
            PortBinding.profile != ''
        ).all()


def get_port_with_binding_profile_by_net(session, network_id):
    with session.begin(subtransactions=True):
        return session.query(
            Port, PortBinding
        ).filter(
            Port.network_id == network_id,
            Port.id == PortBinding.port_id,
            PortBinding.profile.isnot(None),
            PortBinding.profile != ''
        ).all()


# OneView Mechanism driver_api
def map_neutron_network_to_oneview(
    session, neutron_network_id, oneview_network_id, uplinksets_id_list,
    manageable
):
    insert_neutron_oneview_network(
        session, neutron_network_id, oneview_network_id, manageable
    )

    if uplinksets_id_list is None:
        return
    for uplinkset_id in uplinksets_id_list:
        insert_oneview_network_uplinkset(
            session, oneview_network_id, uplinkset_id
        )


# Neutron OneView Network
def list_neutron_oneview_network(session, **kwargs):
    with session.begin(subtransactions=True):
        return session.query(NeutronOneviewNetwork).filter_by(**kwargs).all()


# def list_neutron_oneview_network_manageable(session):
#     with session.begin(subtransactions=True):
#         return session.query(
#             oneview_network_db.NeutronOneviewNetwork
#         ).filter_by(
#             manageable=False
#         ).all()


def insert_neutron_oneview_network(
    session, neutron_network_id, oneview_network_id, manageable=True
):
    with session.begin(subtransactions=True):
        net = NeutronOneviewNetwork(
            neutron_network_id, oneview_network_id, manageable
        )
        session.add(net)


# def update_neutron_oneview_network(session, neutron_id, new_oneview_id):
#     with session.begin(subtransactions=True):
#         return session.query(
#             oneview_network_db.NeutronOneviewNetwork
#         ).all()


# def get_management_neutron_network(session, network_id):
#     with session.begin(subtransactions=True):
#         return session.query(
#             oneview_network_db.NeutronOneviewNetwork
#         ).filter_by(
#             neutron_network_id=network_id,
#         ).first()


def get_neutron_oneview_network(session, neutron_network_id):
    with session.begin(subtransactions=True):
        return session.query(
            NeutronOneviewNetwork
        ).filter_by(
            neutron_network_id=neutron_network_id
        ).first()


def delete_neutron_oneview_network(session, **kwargs):
    with session.begin(subtransactions=True):
        session.query(NeutronOneviewNetwork).filter_by(**kwargs).delete()


# OneView Network Uplinkset
def list_oneview_network_uplinkset(session, **kwargs):
    with session.begin(subtransactions=True):
        return session.query(OneviewNetworkUplinkset).filter_by(**kwargs).all()


def get_oneview_network_uplinkset(session, **kwargs):
    with session.begin(subtransactions=True):
        return session.query(
            OneviewNetworkUplinkset
        ).filter_by(**kwargs).first()


def get_network_uplinksets(session, oneview_network_id):
    with session.begin(subtransactions=True):
        return session.query(
            OneviewNetworkUplinkset
        ).filter_by(
            oneview_network_id=oneview_network_id
        ).all()


def insert_oneview_network_uplinkset(
    session, oneview_network_id, uplinkset_id
):
    with session.begin(subtransactions=True):
        oneview_network_uplinkset = OneviewNetworkUplinkset(
            oneview_network_id, uplinkset_id
        )
        session.add(oneview_network_uplinkset)


# def delete_oneview_network_uplinkset(
#     session, uplinkset_id, network_id, commit=False
# ):
#     with session.begin(subtransactions=True):
#         session.query(
#             oneview_network_db.OneviewNetworkUplinkset
#         ).filter_by(
#             oneview_uplinkset_id=uplinkset_id,
#             oneview_network_id=network_id
#         ).delete()
#     if commit:
#         session.commit()


def delete_oneview_network_uplinkset_by_network(session, network_id):
    with session.begin(subtransactions=True):
        session.query(
            OneviewNetworkUplinkset
        ).filter_by(
            oneview_network_id=network_id
        ).delete()
#
#
# def get_ml2_port_binding(session, neutron_port_id):
#     with session.begin(subtransactions=True):
#         return session.query(
#             PortBinding
#         ).filter_by(
#             port_id=neutron_port_id
#         ).first()
