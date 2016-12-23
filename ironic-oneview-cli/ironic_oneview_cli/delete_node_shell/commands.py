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


class NodeDelete(object):

    def __init__(self, facade):
        self.facade = facade

    def delete_ironic_nodes(self, number=None):
        nodes = self.facade.get_ironic_node_list()
        try:
            if number:
                for n in range(number):
                    self.facade.node_delete(nodes[n].uuid)
            else:
                for node in nodes:
                    self.facade.node_delete(node.uuid)
        except Exception as e:
            raise e


@common.arg(
    '--all',
    action='store_true',
    help='Delete all ironic nodes'
)
@common.arg(
    '-n', '--number',
    type=int,
    help='Delete multiple ironic nodes'
)
def do_node_delete(args):
    """Delete nodes in Ironic"""

    node_delete = NodeDelete(facade.Facade(args))

    if args.all:
        message = '\nDo you really want to delete all nodes? [y/N] '
        response = common.approve_command_prompt(message)
        if response:
            node_delete.delete_ironic_nodes()
            print('\nNodes deleted!')
    elif args.number:
        node_delete.delete_ironic_nodes(args.number)
        print('\nNodes deleted!')
    else:
        print('\nNot implemented')
