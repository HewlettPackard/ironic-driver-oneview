# Copyright (2015-2017) Hewlett Packard Enterprise Development LP.
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
from ironic_oneview_cli import common
from ironic_oneview_cli import exceptions
from ironic_oneview_cli import facade


class PortCreator(object):
    def __init__(self, facade):
        self.facade = facade

    def create_port(self, args, ironic_node):
        server_hardware_uri = ironic_node.driver_info.get(
            "server_hardware_uri")
        server_hardware = self.facade.get_server_hardware(server_hardware_uri)

        if args.mac:
            mac = args.mac
        else:
            mac = self._get_server_hardware_mac(server_hardware)

        self._verifify_existing_ports_for_node(ironic_node)

        attrs = self._create_attrs_for_port(ironic_node, mac)
        return self.facade.create_ironic_port(**attrs)

    def _get_server_hardware_mac(self, server_hardware):
        if not server_hardware.get('portMap'):
            return self.facade.get_server_hardware_mac_from_ilo(
                server_hardware)

        sh_physical_port = self._get_first_ethernet_physical_port(
            server_hardware)
        if sh_physical_port:
            for virtual_port in sh_physical_port.get('virtualPorts'):
                # NOTE(nicodemos): Ironic oneview drivers needs to use a
                # port that type is Ethernet and function 'a' to be able
                # to peform a deploy.
                if virtual_port.get('portFunction') == 'a':
                    return virtual_port.get('mac').lower()
        else:
            raise exceptions.OneViewResourceNotFoundError(
                "There is no Ethernet port on the Server Hardware: %s"
                % server_hardware.get('uri'))

    def _get_first_ethernet_physical_port(self, server_hardware):
        for device in server_hardware.get('portMap').get(
                'deviceSlots'):
            for physical_port in device.get('physicalPorts', []):
                if physical_port.get('type') == 'Ethernet':
                    return physical_port

    def _create_attrs_for_port(
        self, ironic_node, mac
    ):
        attrs = {
            'address': mac,
            'node_uuid': ironic_node.uuid,
            'portgroup_uuid': None,
            "local_link_connection":
                self._build_local_link_connection(ironic_node),
            'pxe_enabled': True
        }

        return attrs

    def _build_local_link_connection(self, ironic_node):
        local_link_connection = {}
        if ironic_node.driver_info.get('use_oneview_ml2_driver'):
            server_hardware_id = common.get_server_hardware_id_from_node(
                ironic_node)
            switch_info = (
                '{"server_hardware_id": "%(server_hardware_id)s", '
                '"bootable": "%(bootable)s"}') % {
                    'server_hardware_id': server_hardware_id,
                    'bootable': True}
            local_link_connection = {
                "switch_id": "01:23:45:67:89:ab",
                "port_id": "",
                "switch_info": switch_info
            }
        return local_link_connection

    def _verifify_existing_ports_for_node(self, ironic_node):
        ports = filter(lambda p: p.node_uuid == ironic_node.uuid,
                       self.facade.get_ironic_port_list())
        if ports:
            print("There are created ports for this node already. The CLI "
                  "will try to create it as another port.")


@common.arg(
    'node',
    metavar='<node_uuid>',
    help='Create a port based on a given ironic node uuid.')
@common.arg(
    '-m', '--mac',
    help='MAC Address of the HPE OneView Server Hardware.')
def do_port_create(args):
    """Create port based on a Ironic Node.

    If not specified, it retrieves the mac address of the first '-a' available
    port at the Server Hardware to which the Ironic Node is related to. It
    also gathers the local link connection if the Ironic Node is enabled to
    use the OneView ml2 driver.
    """
    facade_obj = facade.Facade(args)
    port_creator = PortCreator(facade_obj)

    ironic_node = facade_obj.get_ironic_node(args.node)
    port = port_creator.create_port(args, ironic_node)

    print("Created port %s" % port.uuid)
