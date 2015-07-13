# -*- encoding: utf-8 -*-
#
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

from ironic.common import exception
from ironic.common.i18n import _
from ironic.common.i18n import _LI
from ironic.common import states
from ironic.conductor import task_manager
from ironic.drivers import base
from ironic.drivers.modules.oneview import common
from ironic.drivers.modules.oneview import oneview_client
from ironic.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class OneViewPower(base.PowerInterface):

    def get_properties(self):
        return common.COMMON_PROPERTIES

    def validate(self, task):
        common.parse_driver_info(task.node)

    def get_power_state(self, task):
        driver_info = common.parse_driver_info(task.node)
        return oneview_client.get_node_power_state(driver_info)

    @task_manager.require_exclusive_lock
    def set_power_state(self, task, power_state):
        driver_info = common.parse_driver_info(task.node)

        if power_state == states.POWER_ON:
            state = oneview_client.power_on(driver_info)
        elif power_state == states.POWER_OFF:
            state = oneview_client.power_off(driver_info)
        else:
            raise exception.InvalidParameterValue(
                _("set_power_state called with invalid power state %s.")
                % power_state)

        if state != power_state:
            raise exception.PowerStateFailure(pstate=power_state)

        task.node.power_state = power_state

    @task_manager.require_exclusive_lock
    def reboot(self, task):
        driver_info = common.parse_driver_info(task.node)
        oneview_client.power_off(driver_info)
        power_state = "PoweringOff"

        while power_state == "PoweringOff":
            LOG.debug("Node %(node_uuid)s is powering off",
                      {'node_uuid': task.node.uuid})
            power_state = oneview_client.get_node_power_state(driver_info)

        LOG.info(_LI("Node %(node_uuid)s power state is %(power_state)s"),
                 {'node_uuid': task.node.uuid, 'power_state': power_state})

        oneview_client.power_on(driver_info)
