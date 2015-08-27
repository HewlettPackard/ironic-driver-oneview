# -*- encoding: utf-8 -*-
#
# (c) Copyright 2015 Hewlett Packard Enterprise Development LP
# Copyright 2015 Universidade Federal de Campina Grande
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

from config_client import ConfClient

from ironicclient import client as ironic_client
from ironic.common import keystone
from ironic.common.i18n import _LE
from ironic.common.i18n import _LI

from novaclient import client as nova_client

from oneview_client import OneViewServerHardwareAPI

from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class OpenstackClient:

    def _get_ironic_client(self):
        conf_client = ConfClient()
        keystone_conf = conf_client.keystone
        kwargs = {
            'os_username': keystone_conf.get_admin_user(),
            'os_password': keystone_conf.get_admin_password(),
            'os_auth_url': keystone_conf.get_auth_uri(),
            'os_tenant_name': keystone_conf.get_admin_tenant_name()
        }

        LOG.debug("Using OpenStack credentials specified in synch.conf to get"
                  " an Ironic Client")
        ironic = ironic_client.get_client(1, **kwargs)
        return ironic


    def _update_ironic_node_state(self, node, server_hardware_uri):
        oneview_sh_client = OneViewServerHardwareAPI()
        state = oneview_sh_client.get_node_power_state(server_hardware_uri)

        LOG.info('Setting node %(node_uuid)s power state to %(state)s',
                 {'node_uuid': node.uuid, 'state': state})

        self._get_ironic_client().node.set_power_state(node.uuid, state)


    def get_nova_client(self):
        conf_client = ConfClient()
        LOG.debug("Using OpenStack credentials specified in synch.conf to get"
                  " a Nova Client")
        nova = nova_client.Client(2, conf_client.nova.get_username(),
                                  conf_client.nova.get_user_pass(),
                                  conf_client.nova.get_user_tenant(),
                                  conf_client.keystone.get_auth_uri())
        return nova


    def _is_flavor_available(self, server_hardware_info):
        LOG.info("Getting flavors from nova")
        for flavor in self.get_nova_client().flavors.list():
            extra_specs = flavor.get_keys()
            if('capabilities:server_hardware_type_uri' in extra_specs):
                if(extra_specs.get('capabilities:server_hardware_type_uri') !=
                    server_hardware_info.get('server_hardware_type_uri')):
                    continue
                if(extra_specs.get('cpu_arch') !=
                    server_hardware_info.get('cpu_arch')):
                    continue
                if(flavor._info.get('vcpus') !=
                    server_hardware_info.get('cpus')):
                    continue
                if(flavor._info.get('ram') !=
                    server_hardware_info.get('memory_mb')):
                    continue
                return True
        return False


    def flavor_list(self):
        nova_client = self.get_nova_client()
        return nova_client.flavors.list()
