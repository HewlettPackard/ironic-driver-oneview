# Copyright (2015-2017) Hewlett Packard Enterprise Development LP
# Copyright (2015-2017) Universidade Federal de Campina Grande
# All Rights Reserved.
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
import redfish

from ironic_oneview_cli import common
from ironic_oneview_cli import openstack_client

ILOREST_BASE_PORT = 443


class Facade(object):

    def __init__(self, args):
        self.ironicclient = openstack_client.get_ironic_client(args)
        self.novaclient = openstack_client.get_nova_client(args)
        self.hponeview_client = common.get_hponeview_client(args)

    # =========================================================================
    # Ironic actions
    # =========================================================================
    def get_ironic_node_list(self):
        return self.ironicclient.node.list(detail=True)

    def get_ironic_node(self, node_uuid):
        return self.ironicclient.node.get(node_uuid)

    def get_ironic_port_list(self):
        return self.ironicclient.port.list(detail=True)

    def node_set_maintenance(self, node_uuid, maintenance_mode, maint_reason):
        return self.ironicclient.node.set_maintenance(
            node_uuid, maintenance_mode, maint_reason=maint_reason
        )

    def node_update(self, node_uuid, patch):
        return self.ironicclient.node.update(
            node_uuid, patch
        )

    def node_delete(self, node_uuid):
        return self.ironicclient.node.delete(
            node_uuid
        )

    def create_ironic_port(self, **attrs):
        return self.ironicclient.port.create(**attrs)

    def create_ironic_node(self, **attrs):
        return self.ironicclient.node.create(**attrs)

    def get_drivers(self):
        return self.ironicclient.driver.list()

    # =========================================================================
    # Nova actions
    # =========================================================================
    def create_nova_flavor(self, **attrs):
        return self.novaclient.flavors.create(
            name=attrs.get('name'),
            ram=attrs.get('ram'),
            vcpus=attrs.get('vcpus'),
            disk=attrs.get('disk')
        )

    # =========================================================================
    # OneView actions
    # =========================================================================
    def get_server_hardware(self, uri):
        uuid = common.get_uuid_from_uri(uri)
        return self.hponeview_client.server_hardware.get(uuid)

    def get_server_profile_template(self, uri):
        if uri is None:
            return
        uuid = common.get_uuid_from_uri(uri)
        return self.hponeview_client.server_profile_templates.get(uuid)

    def get_enclosure_group(self, uri):
        if uri is None:
            return
        uuid = common.get_uuid_from_uri(uri)
        return self.hponeview_client.enclosure_groups.get(uuid)

    def get_server_hardware_type(self, uri):
        uuid = common.get_uuid_from_uri(uri)
        return self.hponeview_client.server_hardware_types.get(uuid)

    def get_server_profile(self, uri):
        uuid = common.get_uuid_from_uri(uri)
        return self.hponeview_client.server_profiles.get(uuid)

    def list_templates_compatible_with(self, server_hardware_list):
        compatible_server_profile_list = []
        server_hardware_type_list = []
        server_group_list = []

        for server_hardware in server_hardware_list:
            server_hardware_type_list.append(
                server_hardware.get('serverHardwareTypeUri'))
            server_group_list.append(
                server_hardware.get('serverGroupUri'))

        spt_list = self.hponeview_client.server_profile_templates.get_all()
        for spt in spt_list:
            if (spt.get('serverHardwareTypeUri') in server_hardware_type_list
               and spt.get('enclosureGroupUri') in server_group_list):
                compatible_server_profile_list.append(spt)
        return compatible_server_profile_list

    def filter_server_hardware_available(self, filters=''):
        return self.hponeview_client.server_hardware.get_all(filter=filters)

    def get_ilorest_client(self, server_hardware):
        """Generate an instance of the iLORest library client.

        :param: server_hardware: a dict representing the server hardware
        :returns: an instance of the iLORest client
        """
        remote_console = (
            self.hponeview_client.server_hardware.get_remote_console_url(
                server_hardware.get('uri')))
        host_ip, ilo_token = common.get_ilo_access(remote_console)
        base_url = "https://%s:%s" % (host_ip, ILOREST_BASE_PORT)
        return redfish.rest_client(base_url=base_url, sessionkey=ilo_token)

    def get_server_hardware_mac_from_ilo(self, server_hardware):
        """Get the MAC address from a server hardware using iLO

        :param: server_hardware: a server hardware uuid or uri
        :return: the MAC address
        """
        client = self.get_ilorest_client(server_hardware)
        hardware = json.loads(client.get("/rest/v1/systems/1").text)
        hardware_mac = hardware['HostCorrelation']['HostMACAddress'][0]

        return hardware_mac
