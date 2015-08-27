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

from ironic.common.i18n import _
from ironic.common import states
from ironic.conductor import utils as manager_utils
from ironic.drivers import base
from ironic.drivers.modules.oneview import common
from ironic.drivers.modules.oneview import oneview_client
from ironic.drivers.modules import pxe
from ironic.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class FakeOneViewDeploy(base.DeployInterface):
    """Class for a fake deployment driver.

    Example implementation of a deploy interface that uses a
    separate power interface.

    """

    def get_properties(self):
        return common.COMMON_PROPERTIES

    def validate(self, task):
        common.parse_driver_info(task.node)

    def deploy(self, task):
        driver_info = common.parse_driver_info(task.node)
        server_profile_template_uri = driver_info.get(
            "server_profile_template_uri")

        LOG.debug(_('Cloning server profile template %s on OneView'),
                  server_profile_template_uri)

        oneview_client.clone_and_assign(driver_info,
                                        server_profile_template_uri,
                                        task.node._instance_uuid)

        LOG.info(_('Server profile template %s cloned on Oneview'),
                 server_profile_template_uri)

        manager_utils.node_power_action(task, states.REBOOT)

        return states.DEPLOYDONE

    def tear_down(self, task):
        driver_info = common.parse_driver_info(task.node)
        manager_utils.node_power_action(task, states.POWER_OFF)
        oneview_client.unassign_and_delete(driver_info)
        return states.DELETED

    def prepare(self, task):
        pass

    def clean_up(self, task):
        pass

    def take_over(self, task):
        pass


class OneViewDeploy(pxe.PXEDeploy):
    """Class for a fake deployment driver.

    Example imlementation of a deploy interface that uses a
    separate power interface.

    """

    def get_properties(self):
        return common.COMMON_PROPERTIES

    def validate(self, task):
        common.parse_driver_info(task.node)
        super(OneViewDeploy, self).validate(task)

    def deploy(self, task):
        driver_info = common.parse_driver_info(task.node)
        server_profile_template_uri = driver_info.get(
            "server_profile_template_uri")

        LOG.debug(_('Cloning server profile %s on OneView'),
                  server_profile_template_uri)

        oneview_client.clone_and_assign(driver_info,
                                        server_profile_template_uri,
                                        task.node._instance_uuid)

        LOG.info(_('Server profile template %s cloned on Oneview'),
                 server_profile_template_uri)

        return super(OneViewDeploy, self).deploy(task)

    def tear_down(self, task):
        driver_info = common.parse_driver_info(task.node)
        manager_utils.node_power_action(task, states.POWER_OFF)
        oneview_client.unassign_and_delete(driver_info)
        return states.DELETED
