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

from ironic_oneviewd import utils


class Facade(object):

    def __init__(self):
        self.ironicclient = utils.get_ironic_client()
        self.oneview_client = utils.get_hponeview_client()

    # =========================================================================
    # Ironic actions
    # =========================================================================

    def get_ironic_node_list(self):
        return self.ironicclient.node.list(detail=True)

    def get_ironic_node(self, node_uuid):
        return self.ironicclient.node.get(node_uuid)

    def delete_ironic_node(self, node_uuid):
        return self.ironicclient.node.delete(node_uuid)

    def node_set_maintenance(self, node_uuid, maintenance_mode, maint_reason):
        return self.ironicclient.node.set_maintenance(
            node_uuid,
            maintenance_mode,
            maint_reason=maint_reason
        )

    def create_ironic_node(self, **attrs):
        return self.ironicclient.node.create(**attrs)

    def set_node_provision_state(self, node, state):
        return self.ironicclient.node.set_provision_state(node.uuid, state)

    # =========================================================================
    # OneView actions
    # =========================================================================

    def get_server_hardware(self, node_info):
        server_hardware_uri = node_info.get('server_hardware_uri')
        return self.oneview_client.server_hardware.get(server_hardware_uri)

    def get_server_hardware_remote_console_url(self, node_info):
        server_hardware_uri = node_info.get('server_hardware_uri')
        return self.oneview_client.server_hardware.get_remote_console_url(
            server_hardware_uri
        )
