# Copyright 2016 Hewlett Packard Enterprise Development LP.
# Copyright 2016 Universidade Federal de Campina Grande
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
from ironic_oneview_cli import facade
from ironic_oneview_cli import service_logging as logging

LOG = logging.getLogger(__name__)
NODE_MIGRATING_TO_DYNAMIC_ALLOCATION = 'Migrating to dynamic allocation'


class NodeMigrator(object):
    def __init__(self, facade_cli):
        self.facade = facade_cli

    def list_pre_allocation_nodes(self):
        pre_allocation_nodes = filter(
            lambda x: x.driver in common.SUPPORTED_DRIVERS
            and x.driver_info.get('dynamic_allocation')
            in (None, False, 'False')
            or x.maintenance_reason == NODE_MIGRATING_TO_DYNAMIC_ALLOCATION,
            self.facade.get_ironic_node_list()
        )

        return pre_allocation_nodes

    def filter_nodes_by_state(self, pre_allocation_nodes_list):
        pre_allocation_nodes_allow_to_migrate = []
        for node in pre_allocation_nodes_list:
            if node.provision_state in ('enroll', 'manageable', 'available',
                                        'active', 'inspect failed',
                                        'clean failed', 'error'):
                pre_allocation_nodes_allow_to_migrate.append(node)
            else:
                message = ("The following node is not in a state available"
                           "to migrate: %s" % (node.uuid))
                LOG.warning(message)

        return pre_allocation_nodes_allow_to_migrate

    def update_nodes_with_oneview_fields(self, pre_allocation_nodes_list):
        nodes_updated = []

        for node in pre_allocation_nodes_list:
            node_server_hardware_uri = node.driver_info.get(
                'server_hardware_uri'
            )

            server_hardware = self.facade.get_server_hardware(
                node_server_hardware_uri
            )

            enclosure_group = self.facade.get_enclosure_group(
                server_hardware.enclosure_group_uri
            )

            server_hardware_type = self.facade.get_server_hardware_type(
                server_hardware.server_hardware_type_uri
            )

            node.server_hardware_name = server_hardware.name
            node.server_profile_uri = server_hardware.server_profile_uri
            node.server_hardware_type_name = server_hardware_type.name
            node.enclosure_group_name = enclosure_group.name

            nodes_updated.append(node)

        return nodes_updated

    def get_ironic_nodes_by_uuid(self, list_nodes_uuid):
        list_nodes_to_migrate = []
        for node_uuid in list_nodes_uuid:
            try:
                node = self.facade.get_ironic_node(node_uuid)
                if self.is_node_in_dynamic_allocation(node) is False:
                    list_nodes_to_migrate.append(node)
            except Exception as e:
                print(e.message)

        return list_nodes_to_migrate

    def is_node_in_dynamic_allocation(self, node):
        if node.driver_info.get('dynamic_allocation') in (
            None, False, 'False'
        ):
            return False
        else:
            if node.maintenance_reason == NODE_MIGRATING_TO_DYNAMIC_ALLOCATION:
                self.facade.node_set_maintenance(
                    node.uuid,
                    False,
                    ''
                )

            message = ("The following node is already in the "
                       "dynamic allocation model: %s" % (node.uuid))
            LOG.warning(message)

            return True

    def verify_nodes_with_instances_and_migrate(self, nodes_to_migrate):
        for node in nodes_to_migrate:
            if node.instance_uuid:
                self.migrate_node_with_instance(node)
            else:
                self.migrate_idle_node(node)

    def migrate_idle_node(self, node_to_migrate):
        maintenance_reason = NODE_MIGRATING_TO_DYNAMIC_ALLOCATION
        add_dynamic_flag = [{'op': 'add',
                             'path': '/driver_info/dynamic_allocation',
                             'value': True}]

        self.facade.node_set_maintenance(
            node_to_migrate.uuid,
            True,
            maintenance_reason
        )

        try:
            self.facade.delete_server_profile(
                node_to_migrate.server_profile_uri
            )
        # NOTE(nicodemos): Ignore in case the operation fails because
        # there is not a server profile;
        except ValueError:
            pass
        except Exception as e:
            print(e.message)

        self.facade.node_update(
            node_to_migrate.uuid,
            add_dynamic_flag
        )
        self.facade.node_set_maintenance(
            node_to_migrate.uuid,
            False,
            ''
        )

    def migrate_node_with_instance(self, node_to_migrate):
        if self.is_node_in_dynamic_allocation(node_to_migrate) is False:
            add_dynamic_flag = [
                {'op': 'add',
                 'path': '/driver_info/dynamic_allocation',
                 'value': True}
            ]
            add_applied_server_profile = [
                {'op': 'add',
                 'path': '/driver_info/'
                         'applied_server_profile_uri',
                 'value':
                         node_to_migrate.server_profile_uri}
            ]
            self.facade.node_update(
                node_to_migrate.uuid,
                add_applied_server_profile + add_dynamic_flag
            )


@common.arg(
    '--all',
    action='store_true',
    help="Migrate all pre-allocation nodes to dynamic allocation")
@common.arg(
    '--nodes',
    nargs='+',
    help="UUID of the nodes you want to migrate.")
def do_migrate_to_dynamic(args):
    """Migrate nodes from pre-allocation to dynamic allocation model."""

    node_migrator = NodeMigrator(facade.Facade(args))

    if args.nodes:
        pre_allocation_nodes = node_migrator.get_ironic_nodes_by_uuid(
            args.nodes
        )
    else:
        pre_allocation_nodes = node_migrator.list_pre_allocation_nodes()

    nodes_allow_to_migrate = node_migrator.filter_nodes_by_state(
        pre_allocation_nodes
    )
    nodes_to_migrate = node_migrator.update_nodes_with_oneview_fields(
        nodes_allow_to_migrate
    )

    if args.nodes or args.all:
        if nodes_to_migrate:
            node_migrator.verify_nodes_with_instances_and_migrate(
                nodes_to_migrate
            )
            print('\nMigration complete!')
        else:
            print("\nThere is no valid pre-allocation nodes to migrate!")
    else:
        common.assign_elements_with_new_id(nodes_to_migrate)

        print("Retrieving pre-allocation Nodes from Ironic...")
        while True:
            input_id = common.print_prompt(
                nodes_to_migrate,
                [
                    'id',
                    'uuid',
                    'server_hardware_name',
                    'server_hardware_type_name',
                    'enclosure_group_name'
                ],
                "Enter a space separated list of pre-allocation nodes ID's "
                "you want to migrate. ('all' to all nodes or 'q' to quit)> ",
                [
                    'Id',
                    'Node UUID',
                    'Server Hardware Name',
                    'Server Hardware Type Name',
                    'Enclosure Group Name'
                ]
            )
            if input_id == 'all':
                node_migrator.verify_nodes_with_instances_and_migrate(
                    nodes_to_migrate
                )
                print("\nMigration Complete!")
                break

            if input_id == 'q':
                break

            pre_allocation_nodes_selected = input_id.split()

            invalid_entry_id = common.is_entry_invalid(
                pre_allocation_nodes_selected, nodes_to_migrate
            )
            if invalid_entry_id:
                print("\nInvalid pre-allocation node ID!")
                continue

            for node_id in pre_allocation_nodes_selected:
                node_selected = common.get_element_by_id(
                    nodes_to_migrate,
                    node_id
                )

                print("\nMigrating the following pre-allocation Node: ")
                common.print_prompt(
                    [node_selected],
                    [
                        'uuid',
                        'server_hardware_name',
                        'server_hardware_type_name',
                        'enclosure_group_name'
                    ],
                    field_labels=[
                        'Node UUID',
                        'Server Hardware Name',
                        'Server Hardware Type Name',
                        'Enclosure Group Name'
                    ]
                )

                node_migrator.verify_nodes_with_instances_and_migrate(
                    [node_selected]
                )

                print('\nNode migrated!')

            message = '\nWould you like to migrate another Node? [y/N] '
            response = common.approve_command_prompt(message)
            if not response:
                break
