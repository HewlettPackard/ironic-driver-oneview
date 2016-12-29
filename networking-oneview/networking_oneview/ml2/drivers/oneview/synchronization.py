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
import sys
import time
from datetime import datetime
from oslo_service import loopingcall
from oslo_log import log
from hpOneView import exceptions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from networking_oneview.ml2.drivers.oneview import common
from networking_oneview.ml2.drivers.oneview import (
    database_manager as db_manager
)

LOG = log.getLogger(__name__)


def get_session(connection):
    Session = sessionmaker(bind=create_engine(connection), autocommit=True)
    return Session()


class Synchronization:
    def __init__(self, oneview_client, neutron_oneview_client, connection):
        self.oneview_client = oneview_client
        self.neu_ov_client = neutron_oneview_client
        self.connection = connection
        self.check_unique_uplinkset_constraint()
        self.check_lig_constraint()
        heartbeat = loopingcall.FixedIntervalLoopingCall(self.synchronize)
        heartbeat.start(interval=3600, initial_delay=0)

    def synchronize(self):
        self.create_oneview_networks_from_neutron()
        self.delete_unmapped_oneview_networks()
        self.synchronize_uplinkset_from_mapped_networks()
        self.create_connection()

    def get_oneview_network(self, oneview_network_id):
        try:
            return self.oneview_client.ethernet_networks.get(
                oneview_network_id
            )
        except exceptions.HPOneViewException as err:
            LOG.error(err)

    def _remove_inconsistence_from_db(
        self, session, neutron_network_id, oneview_network_id
    ):
        db_manager.delete_neutron_oneview_network(
            session, neutron_network_id=neutron_network_id
        )

        db_manager.delete_oneview_network_uplinkset_by_network(
            session, oneview_network_id
        )

    def check_lig_constraint(self):
        physnet_mappings = self.neu_ov_client.port.physnet_uplinkset_mapping
        for key in physnet_mappings:
            for _type in physnet_mappings[key]:
                uplinksets = physnet_mappings[key][_type]
                lgis = []
                for uplinkset in uplinksets:
                    us = self.oneview_client.uplink_sets.get(uplinkset)
                    uplink_type = us.get('ethernetNetworkType')
                    li = self.oneview_client.logical_interconnects.get(
                        us.get('logicalInterconnectUri'))
                    lig = self.oneview_client.logical_interconnect_groups.get(
                        li.get('logicalInterconnectGroupUri')
                    )
                    lig_uri = lig.get('uri')
                    if lig_uri not in lgis:
                        lgis.append(lig_uri)
                    else:
                        err = (
                            "There is more than one uplinkset of "
                            "type %(uplinktype)s from the same logical "
                            "interconnect group mapped "
                            "for the same physnet") % {
                                'uplinktype': uplink_type
                                }
                        LOG.error(err)
                        sys.exit(1)

    def check_unique_uplinkset_constraint(self):
        mapped_uplinksets = []
        physnet_mappings = self.neu_ov_client.port.physnet_uplinkset_mapping
        for key in physnet_mappings:
            for _type in physnet_mappings[key]:
                uplinksets = physnet_mappings[key][_type]
                uplinksets_checked = []
                for uplinkset in uplinksets:
                    if uplinkset in uplinksets_checked:
                        warning = (
                            "Uplinkset %(uplinkset)s is duplicated "
                            "in the same Physical Network") % {
                                'uplinkset': uplinkset
                                }
                        LOG.warning(warning)
                    else:
                        uplinksets_checked.append(uplinkset)
                for uplinkset in uplinksets_checked:
                    if uplinkset in mapped_uplinksets:
                        err = (
                            "Uplinkset %(uplinkset)s is used by more "
                            "than one Physical Network") % {
                                'uplinkset': uplinkset
                                }
                        LOG.error(err)
                        sys.exit(1)
                    else:
                        mapped_uplinksets.append(uplinkset)

    def create_oneview_networks_from_neutron(self):
        session = get_session(self.connection)
        for network, network_segment in (
            db_manager.list_networks_and_segments_with_physnet(session)
        ):
            id = network.get('id')
            neutron_oneview_network = db_manager.get_neutron_oneview_network(
                session, id
            )
            if neutron_oneview_network is not None:
                oneview_network = self.get_oneview_network(
                    neutron_oneview_network.oneview_network_id
                )
                if oneview_network is not None:
                    continue
                else:
                    self._remove_inconsistence_from_db(
                        session,
                        neutron_oneview_network.neutron_network_id,
                        neutron_oneview_network.oneview_network_id
                    )

            physical_network = network_segment.get('physical_network')
            network_type = network_segment.get('network_type')
            segmentation_id = network_segment.get('segmentation_id')
            network_dict = common.network_dict_for_network_creation(
                physical_network, network_type, id, segmentation_id
            )

            self.neu_ov_client.network.create(session, network_dict)

    def synchronize_uplinkset_from_mapped_networks(self):
        session = get_session(self.connection)
        for neutron_oneview_network in (
            db_manager.list_neutron_oneview_network(session)
        ):
            oneview_network_id = neutron_oneview_network.oneview_network_id
            neutron_network_id = neutron_oneview_network.neutron_network_id
            network_segment = db_manager.get_network_segment(
                session, neutron_network_id
            )
            if network_segment is not None:
                self.neu_ov_client.network.update_uplinksets(
                    session, oneview_network_id, network_segment.get(
                        'network_type'
                    ),
                    network_segment.get('physical_network')
                )

    def delete_unmapped_oneview_networks(self):
        session = get_session(self.connection)

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
                    return self.oneview_client.ethernet_networks.delete(
                        oneview_network_id
                    )
                else:
                    physnet = network_segment.get('physical_network')
                    network_type = network_segment.get('network_type')
                    if not self.neu_ov_client.network.is_managed(
                        physnet, network_type
                    ):
                        self._delete_connections(neutron_network_id)
                        return self.neu_ov_client.network.delete(
                            session, {'id': neutron_network_id}
                        )

    def _delete_connections(self, neutron_network_id):
        session = get_session(self.connection)
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
            lli = common.local_link_information_from_port(port_dict)
            server_hardware_id = lli[0].get('switch_info').get(
                'server_hardware_id'
                )
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
                connection.get('boot').get('priority') == 'Secondary' and
                connection_primary
                    ):
                    connection['boot']['priority'] = 'Primary'

        server_profile_to_update = server_profile.copy()
        server_profile_to_update['connections'] = connections
        self.oneview_client.server_profiles.update(
            resource=server_profile_to_update,
            id_or_uri=server_profile_to_update.get('uri')
        )

    def create_connection(
        self
    ):
        session = get_session(self.connection)
        for port, port_binding in db_manager.get_port_with_binding_profile(
            session
        ):
            port_dict = common.port_dict_for_port_creation(
                port.get('network_id'), port_binding.get('vnic_type'),
                port.get('mac_address'),
                json.loads(port_binding.get('profile'))
            )
            lli = common.local_link_information_from_port(port_dict)
            server_hardware_id = lli[0].get('switch_info').get(
                'server_hardware_id'
                )
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
                    server_profile, oneview_uri
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

    def fix_connections_with_removed_networks(
        self, server_profile, oneview_uri
    ):
        sp_cons = []
        for connection in server_profile.get('connections'):
            conn_network_id = oneview_network_id = common.id_from_uri(
                connection.get('networkUri')
            )
            if self.get_oneview_network(conn_network_id) is not None:
                sp_cons.append(connection)
        server_profile['connections'] = sp_cons
        self.neu_ov_client.port.check_server_hardware_availability(
            server_profile.get('serverHardwareUri')
        )
        previous_power_state = self.neu_ov_client.port\
            .get_server_hardware_power_state(
                server_profile.get('serverHardwareUri')
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
