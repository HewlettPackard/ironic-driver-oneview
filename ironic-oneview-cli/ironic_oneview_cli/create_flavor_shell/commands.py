# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2015 Universidade Federal de Campina Grande
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

import re

from ironic_oneview_cli import common
from ironic_oneview_cli.create_flavor_shell import objects
from ironic_oneview_cli import facade
from ironic_oneview_cli import service_logging as logging

LOG = logging.getLogger(__name__)


class FlavorCreator(object):

    def __init__(self, facade):
        self.facade = facade

    def get_nodes_using_oneview_drivers(self):
        return filter(lambda x: x.driver in common.SUPPORTED_DRIVERS,
                      self.facade.get_ironic_node_list())

    def get_flavor_from_ironic_node(self, flavor_id, node):
        server_hardware_uri = node.driver_info.get("server_hardware_uri")
        server_hardware = self.facade.get_server_hardware(server_hardware_uri)

        server_hardware_type = self.facade.get_server_hardware_type(
            server_hardware.server_hardware_type_uri
        )

        enclosure_group = self.facade.get_enclosure_group(
            server_hardware.enclosure_group_uri
        )

        capabilities = node.properties.get("capabilities")
        match = re.search(
            "server_profile_template_uri:(?P<uri>[a-zA-Z0-9\-\/]+)",
            capabilities
        )
        server_profile_template_uri = match.group('uri')
        server_profile_template = self.facade.get_server_profile_template(
            server_profile_template_uri
        )

        flavor = self.set_flavor_properties(
            node, server_hardware_type,
            enclosure_group, server_profile_template
        )

        return objects.Flavor(id=flavor_id, info=flavor)

    def set_flavor_properties(self, node, server_hardware_type,
                              enclosure_group, server_profile_template):
        flavor = {}

        flavor['ram_mb'] = node.properties.get('memory_mb')
        flavor['cpus'] = node.properties.get('cpus')
        flavor['disk'] = node.properties.get('local_gb')
        flavor['cpu_arch'] = node.properties.get('cpu_arch')

        flavor['server_hardware_type_name'] = getattr(
            server_hardware_type, 'name', '')
        flavor['server_hardware_type_uri'] = getattr(
            server_hardware_type, 'uri', '')

        flavor['enclosure_group_name'] = getattr(enclosure_group, 'name', '')
        flavor['enclosure_group_uri'] = getattr(enclosure_group, 'uri', '')

        flavor['server_profile_template_name'] = getattr(
            server_profile_template, 'name', ''
        )
        flavor['server_profile_template_uri'] = getattr(
            server_profile_template, 'uri', ''
        )

        return flavor

    def get_flavor_list(self, nodes):
        flavors = []

        id_counter = 1
        for node in nodes:
            if node.properties.get('memory_mb'):
                flavors.append(
                    self.get_flavor_from_ironic_node(id_counter, node)
                )
                id_counter += 1
        return sorted(set(flavors), key=lambda x: x.cpus)

    def create_flavor(self, name, ram, vcpus, disk, extra_specs={}):
        attrs = {
            'name': name,
            'ram': ram,
            'vcpus': vcpus,
            'disk': disk
        }

        try:
            flavor = self.facade.create_nova_flavor(**attrs)
            flavor.set_keys(extra_specs)
        except Exception as e:
            raise e


def do_flavor_create(args):
    """Create flavors based on available Ironic nodes.

    Shows a list with suggested Flavors to be created based on OneView's Server
    Profile Templates. The user can then select a Flavor to create based on
    it's ID.
    """
    cli_facade = facade.Facade(args)
    flavor_creator = FlavorCreator(cli_facade)
    nodes = flavor_creator.get_nodes_using_oneview_drivers()

    if not nodes:
        print("No Ironic nodes running OneView drivers were found. "
              "Please, create a node to be used as base for the Flavor.")
        return

    print("Retrieving possible configurations for Flavor creation...")

    LOG.info("Flavor creation...")

    flavor_list = flavor_creator.get_flavor_list(nodes)
    common.assign_elements_with_new_id(flavor_list)

    while True:
        input_id = common.print_prompt(
            flavor_list,
            [
                'id',
                'cpus',
                'disk',
                'ram_mb',
                'server_profile_template_name',
                'server_hardware_type_name',
                'enclosure_group_name'
            ],
            "Insert Flavor ID to add in OneView. Press 'q' to quit> ",
            [
                'Id',
                'CPUs',
                'Disk GB',
                'Memory MB',
                'Server Profile Template',
                'Server Hardware Type',
                'Enclosure Group Name'
            ],
        )
        if input_id == "q":
            break

        invalid_entry_id = common.is_entry_invalid(input_id, flavor_list)
        if invalid_entry_id:
            print('Invalid Flavor ID. Please enter a valid ID.')
            continue

        flavor = common.get_element_by_id(flavor_list, input_id)

        print("Listing chosen flavor configuration...")
        common.print_prompt(
            [flavor],
            [
                'cpus',
                'disk',
                'ram_mb',
                'server_profile_template_name',
                'server_hardware_type_name',
                'enclosure_group_name'
            ],
            field_labels=[
                'CPUs',
                'Disk GB',
                'Memory MB',
                'Server Profile Template',
                'Server Hardware Type',
                'Enclosure Group Name'
            ]
        )

        flavor_name = common.set_flavor_name(flavor)

        flavor_creator.create_flavor(
            flavor_name,
            flavor.ram_mb,
            flavor.cpus,
            flavor.disk,
            flavor.extra_specs()
        )

        print('Flavor created!\n')

        message = 'Would you like to create another Flavor(s)? [y/N] '
        response = common.approve_command_prompt(message)
        if not response:
            break
