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

import json
import re

from hpOneView import exceptions
from networking_oneview.ml2.drivers.oneview import (
    database_manager as db_manager)
from networking_oneview.ml2.drivers.oneview import common
from oslo_log import log
from oslo_service import loopingcall
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itertools import chain

LOG = log.getLogger(__name__)


class Synchronization(object):
    def __init__(
            self, oneview_client, neutron_oneview_client, connection,
            uplinkset_mappings, flat_net_mappings):
        self.oneview_client = oneview_client
        self.neu_ov_client = neutron_oneview_client
        self.connection = connection
        self.uplinkset_mappings = uplinkset_mappings
        self.flat_net_mappings = flat_net_mappings
        self.check_unique_lig_per_provider_constraint()
        self.check_uplinkset_types_constraint()

    def start(self):
        heartbeat = loopingcall.FixedIntervalLoopingCall(self.synchronize)
        heartbeat.start(interval=3600, initial_delay=0)

    def get_session(self):
        Session = sessionmaker(bind=create_engine(self.connection),
                               autocommit=True)
        return Session()

    def synchronize(self):
        self.delete_outdated_flat_mapped_networks()
        self.create_oneview_networks_from_neutron()
        self.delete_unmapped_oneview_networks()
        self.synchronize_uplinkset_from_mapped_networks()
        self.create_connection()

    def get_oneview_network(self, oneview_net_id):
        try:
            return self.oneview_client.ethernet_networks.get(oneview_net_id)
        except exceptions.HPOneViewException as err:
            LOG.error(err)

    def _remove_inconsistence_from_db(
        self, session, neutron_network_id, oneview_network_id
    ):
        db_manager.delete_neutron_oneview_network(
            session, neutron_network_id=neutron_network_id
        )
        db_manager.delete_oneview_network_lig(
            session, oneview_network_id=oneview_network_id
        )

    def check_uplinkset_types_constraint(self):
        """Check the number of uplinkset types for a provider in a LIG.

        It is only possible to map one provider to at the most one uplink
        of each type.
        """
        for provider in self.uplinkset_mappings:
            provider_mapping = zip(
                self.uplinkset_mappings.get(provider)[::2],
                self.uplinkset_mappings.get(provider)[1::2])
            uplinksets_type = {}
            for lig_id, ups_name in provider_mapping:
                lig_mappings = uplinksets_type.setdefault(lig_id, [])
                lig = self.oneview_client.logical_interconnect_groups.get(
                    lig_id
                )
                uplinkset = common.get_uplinkset_by_name_from_list(
                    lig.get('uplinkSets'), ups_name)
                lig_mappings.append(uplinkset.get('ethernetNetworkType'))

                if len(lig_mappings) != len(set(lig_mappings)):
                    err = (
                        "The provider %(provider)s has more than one "
                        "uplinkset of the same type in the logical "
                        "interconnect group %(lig_id)s."
                    ) % {"provider": provider, "lig_id": lig_id}
                    LOG.error(err)
                    raise Exception(err)

    def check_unique_lig_per_provider_constraint(self):
        for provider in self.uplinkset_mappings:
            for provider2 in self.uplinkset_mappings:
                if provider != provider2:
                    provider_lig_mapping_tupples = zip(
                        self.uplinkset_mappings.get(provider)[::2],
                        self.uplinkset_mappings.get(provider)[1::2])
                    provider2_lig_mapping_tupples = zip(
                        self.uplinkset_mappings.get(provider2)[::2],
                        self.uplinkset_mappings.get(provider2)[1::2])
                    identical_mappings = (set(provider_lig_mapping_tupples) &
                                          set(provider2_lig_mapping_tupples))
                    if identical_mappings:
                        err_message_attrs = {
                            "prov1": provider,
                            "prov2": provider2,
                            "identical_mappings": "\n".join(
                                (", ".join(mapping)
                                    for mapping in identical_mappings)
                            )
                        }
                        err = (
                            "The providers %(prov1)s and %(prov2)s are being "
                            "mapped to the same Logical Interconnect Group "
                            "and the same Uplinkset.\n"
                            "The LIG ids and Uplink names are:\n"
                            "%(identical_mappings)s"
                        ) % err_message_attrs
                        LOG.error(err)
                        raise Exception(err)

    def create_oneview_networks_from_neutron(self):
        session = self.get_session()
        for network, network_segment in (
            db_manager.list_networks_and_segments_with_physnet(session)
        ):
            net_id = network.get('id')
            neutron_oneview_network = db_manager.get_neutron_oneview_network(
                session, net_id
            )
            if neutron_oneview_network:
                oneview_network = self.get_oneview_network(
                    neutron_oneview_network.oneview_network_id
                )
                if not oneview_network:
                    self._remove_inconsistence_from_db(
                        session,
                        neutron_oneview_network.neutron_network_id,
                        neutron_oneview_network.oneview_network_id
                    )

            physical_network = network_segment.get('physical_network')
            network_type = network_segment.get('network_type')
            segmentation_id = network_segment.get('segmentation_id')
            network_dict = common.network_dict_for_network_creation(
                physical_network, network_type, net_id, segmentation_id
            )

            self.neu_ov_client.network.create(session, network_dict)

    def synchronize_uplinkset_from_mapped_networks(self):
        session = self.get_session()
        for neutron_oneview_network in (
            db_manager.list_neutron_oneview_network(session)
        ):
            oneview_network_id = neutron_oneview_network.oneview_network_id
            neutron_network_id = neutron_oneview_network.neutron_network_id
            network_segment = db_manager.get_network_segment(
                session, neutron_network_id
            )
            if network_segment:
                self.neu_ov_client.network.update_network_lig(
                    session, oneview_network_id, network_segment.get(
                        'network_type'), network_segment.get(
                        'physical_network'))

    def delete_unmapped_oneview_networks(self):
        session = self.get_session()
        for network in self.oneview_client.ethernet_networks.get_all():
            m = re.search('Neutron \[(.*)\]', network.get('name'))
            if m:
                oneview_network_id = common.id_from_uri(network.get('uri'))
                neutron_network_id = m.group(1)
                neutron_network = db_manager.get_neutron_network(
                    session, neutron_network_id
                )
                network_segment = db_manager.get_network_segment(
                    session, neutron_network_id
                )
                if neutron_network is None:
                    self.oneview_client.ethernet_networks.delete(
                        oneview_network_id
                    )
                    self._remove_inconsistence_from_db(
                        session, neutron_network_id, oneview_network_id
                    )
                else:
                    physnet = network_segment.get('physical_network')
                    network_type = network_segment.get('network_type')
                    if not self.neu_ov_client.network.is_uplinkset_mapping(
                        physnet, network_type
                    ):
                        self._delete_connections(neutron_network_id)
                        self.neu_ov_client.network.delete(
                            session, {'id': neutron_network_id}
                        )

    def delete_outdated_flat_mapped_networks(self):
        session = self.get_session()
        mappings = self.flat_net_mappings.values()
        mapped_networks_uuids = list(chain.from_iterable(mappings))
        oneview_networks_uuids = (
            network.oneview_network_id for network
            in db_manager.list_neutron_oneview_network(session)
            if not network.manageable)
        unmapped_networks_uuids = (
            uuid for uuid
            in oneview_networks_uuids
            if uuid not in mapped_networks_uuids)
        for uuid in unmapped_networks_uuids:
            db_manager.delete_neutron_oneview_network(
                session, oneview_network_id=uuid)

    def _delete_connections(self, neutron_network_id):
        session = self.get_session()
        for port, port_binding in (
            db_manager.get_port_with_binding_profile_by_net(
                session, neutron_network_id
            )
        ):
            port_dict = common.port_dict_for_port_creation(
                port.get('network_id'), port_binding.get('vnic_type'),
                port.get('mac_address'),
                json.loads(port_binding.get('profile'))
            )
            local_link_info = common.local_link_information_from_port(
                port_dict)
            server_hardware_id = (
                common.server_hardware_id_from_local_link_information_list(
                    local_link_info))
            server_profile = (
                self.neu_ov_client.port.server_profile_from_server_hardware(
                    server_hardware_id
                )
            )

            self.neu_ov_client.port.check_server_hardware_availability(
                server_hardware_id
            )
            previous_power_state = (
                self.neu_ov_client.port.get_server_hardware_power_state(
                    server_hardware_id
                )
            )
            self.neu_ov_client.port.update_server_hardware_power_state(
                server_hardware_id, "Off")

            for connection in server_profile.get('connections'):
                if connection.get('mac') == port.get('mac_address'):
                    self._remove_connection(
                        server_profile, connection.get('id')
                    )
            self.neu_ov_client.port.update_server_hardware_power_state(
                server_hardware_id, previous_power_state
            )

    def _remove_connection(self, server_profile, connection_id):
        connection_primary = False
        connections = []
        for connection in server_profile.get('connections'):
            if connection.get('id') != connection_id:
                connections.append(connection)
            elif connection.get('boot').get('priority') == 'Primary':
                connection_primary = True

        for connection in connections:
            if (
                (connection.get('boot').get('priority') == 'Secondary') and
                connection_primary
            ):
                connection['boot']['priority'] = 'Primary'

        server_profile_to_update = server_profile.copy()
        server_profile_to_update['connections'] = connections
        self.oneview_client.server_profiles.update(
            resource=server_profile_to_update,
            id_or_uri=server_profile_to_update.get('uri')
        )

    def create_connection(self):
        """Recreate connection that were deleted on Oneview.

        Calls method to fix critical connections in the Server Profile that
        will be used.
        """
        session = self.get_session()

        for port, port_binding in db_manager.get_port_with_binding_profile(
            session
        ):
            port_dict = common.port_dict_for_port_creation(
                port.get('network_id'),
                port_binding.get('vnic_type'),
                port.get('mac_address'),
                json.loads(port_binding.get('profile'))
            )
            local_link_info = common.local_link_information_from_port(
                port_dict)
            server_hardware_id = (
                common.server_hardware_id_from_local_link_information_list(
                local_link_info))
            server_profile = (
                self.neu_ov_client.port.server_profile_from_server_hardware(
                    server_hardware_id
                )
            )
            neutron_oneview_network = db_manager.list_neutron_oneview_network(
                session, neutron_network_id=port.get('network_id')
            )
            connection_updated = False
            if len(neutron_oneview_network) > 0:
                oneview_uri = "/rest/ethernet-networks/" + (
                    neutron_oneview_network[0].oneview_network_id
                )
                self.fix_connections_with_removed_networks(
                    server_profile
                )
                for c in server_profile.get('connections'):
                    if c.get('mac') == port.get('mac_address'):
                        connection_updated = True
                        if c.get('networkUri') != oneview_uri:
                            self.update_connection(
                                oneview_uri, server_profile, c)
            if not connection_updated:
                self.neu_ov_client.port.create(session, port_dict)

    def update_connection(
        self, oneview_uri, server_profile, connection
    ):
        connection['networkUri'] = oneview_uri
        self.neu_ov_client.port.check_server_hardware_availability(
            server_profile.get('uuid')
        )
        previous_power_state = (
            self.neu_ov_client.port.get_server_hardware_power_state(
                server_profile.get('uuid')
            )
        )
        self.neu_ov_client.port.update_server_hardware_power_state(
            server_profile.get('uuid'), "Off"
        )
        self.oneview_client.server_profiles.update(
            resource=server_profile,
            id_or_uri=server_profile.get('uri')
        )
        self.neu_ov_client.port.update_server_hardware_power_state(
            server_profile.get('uuid'), previous_power_state
        )

    def fix_connections_with_removed_networks(self, server_profile):
        sp_cons = []

        for connection in server_profile.get('connections'):
            conn_network_id = common.id_from_uri(
                connection.get('networkUri')
            )
            if self.get_oneview_network(conn_network_id):
                sp_cons.append(connection)

        server_profile['connections'] = sp_cons
        self.neu_ov_client.port.check_server_hardware_availability(
            server_profile.get('serverHardwareUri')
        )
        previous_power_state = (
            self.neu_ov_client.port.get_server_hardware_power_state(
                server_profile.get('serverHardwareUri')
            )
        )

        self.neu_ov_client.port.update_server_hardware_power_state(
            server_profile.get('serverHardwareUri'), "Off")
        self.oneview_client.server_profiles.update(
            resource=server_profile,
            id_or_uri=server_profile.get('uri')
        )
        self.neu_ov_client.port.update_server_hardware_power_state(
            server_profile.get('serverHardwareUri'), previous_power_state
        )
