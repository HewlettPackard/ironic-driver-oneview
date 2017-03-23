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

from hpOneView.oneview_client import OneViewClient
from oslo_config import cfg
from oslo_log import log

from networking_oneview.ml2.drivers.oneview import common
from networking_oneview.ml2.drivers.oneview.neutron_oneview_client import (
    Client)
from networking_oneview.ml2.drivers.oneview import synchronization
from neutron.extensions import portbindings
from neutron.plugins.common import constants as p_const
from neutron.plugins.ml2 import driver_api

LOG = log.getLogger(__name__)

opts = [
    cfg.StrOpt('oneview_host',
               help='IP where OneView is available'),
    cfg.StrOpt('username',
               help='OneView username to be used'),
    cfg.StrOpt('password',
               secret=True,
               help='OneView password to be used'),
    cfg.StrOpt('uplinkset_mappings',
               help='UplinkSets to be used'),
    cfg.StrOpt('tls_cacert_file',
               default='',
               help="TLS File Path"),
    cfg.StrOpt('flat_net_mappings',
               help='Flat Networks on Oneview that are managed by Neutron'),
    cfg.IntOpt('ov_refresh_interval',
               default=3600,
               help='Interval between periodic task executions in seconds')
]

CONF = cfg.CONF
CONF.register_opts(opts, group='oneview')


def get_oneview_client():
    return OneViewClient({"ip": CONF.oneview.oneview_host,
                          "credentials": {"userName": CONF.oneview.username,
                                          "password": CONF.oneview.password}})


class OneViewDriver(driver_api.MechanismDriver):
    def initialize(self):
        self.oneview_client = get_oneview_client()
        self.uplinkset_mappings = common.load_conf_option_to_dict(
            CONF.oneview.uplinkset_mappings)
        self.flat_net_mappings = common.load_conf_option_to_dict(
            CONF.oneview.flat_net_mappings)
        self.neutron_oneview_client = Client(self.oneview_client,
                                             self.uplinkset_mappings,
                                             self.flat_net_mappings)
        if CONF.oneview.tls_cacert_file.strip():
            self.oneview_client.connection.set_trusted_ssl_bundle(
                CONF.oneview.tls_cacert_file
            )
        sync = synchronization.Synchronization(self.oneview_client,
                                               self.neutron_oneview_client,
                                               CONF.database.connection,
                                               self.uplinkset_mappings,
                                               self.flat_net_mappings)
        sync.start()

    def bind_port(self, context):
        """Bind baremetal port to a network."""
        session = common.session_from_context(context)
        port_dict = common.port_from_context(context)
        self.neutron_oneview_client.port.create(session, port_dict)

        port = context.current
        vnic_type = port['binding:vnic_type']

        if vnic_type != portbindings.VNIC_BAREMETAL:
            return

        vif_type = portbindings.VIF_TYPE_OTHER
        vif_details = {portbindings.VIF_DETAILS_VLAN: True}

        for segment in context.segments_to_bind:
            vif_details[portbindings.VIF_DETAILS_VLAN] = (
                str(segment[driver_api.SEGMENTATION_ID])
            )
            context.set_binding(
                segment[driver_api.ID], vif_type, vif_details, p_const.ACTIVE
            )
            LOG.debug(
                "OneViewDriver: bound port info- port ID %(id)s "
                "on network %(network)s", {
                    'id': port['id'], 'network': context.network.current['id']
                }
            )

    def create_network_postcommit(self, context):
        session = common.session_from_context(context)
        network_dict = common.network_from_context(context)

        self.neutron_oneview_client.network.create(session, network_dict)

    def delete_network_postcommit(self, context):
        session = common.session_from_context(context)
        network_dict = common.network_from_context(context)

        self.neutron_oneview_client.network.delete(session, network_dict)

    def create_port_postcommit(self, context):
        pass

    def delete_port_postcommit(self, context):
        session = common.session_from_context(context)
        port_dict = common.port_from_context(context)

        self.neutron_oneview_client.port.delete(session, port_dict)
