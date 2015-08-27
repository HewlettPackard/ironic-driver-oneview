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

from ironic.common import boot_devices
from ironic.common import exception
from ironic.common.i18n import _
from ironic.drivers import base
from ironic.drivers.modules.oneview import common
from ironic.drivers.modules.oneview import oneview_client
from ironic.openstack.common import log as logging

LOG = logging.getLogger(__name__)

BOOT_DEVICE_MAPPING_TO_OV = {
    boot_devices.DISK: 'HardDisk',
    boot_devices.PXE: 'PXE',
    boot_devices.CDROM: 'CD'
}

BOOT_DEVICE_OV_TO_GENERIC = {
    v: k
    for k, v in BOOT_DEVICE_MAPPING_TO_OV.items()
}


class OneViewManagement(base.ManagementInterface):

    def get_properties(self):
        return common.COMMON_PROPERTIES

    def validate(self, task):
        common.parse_driver_info(task.node)

    def get_supported_boot_devices(self):
        return list(sorted(BOOT_DEVICE_MAPPING_TO_OV.keys()))

    def set_boot_device(self, task, device, persistent=False):
        driver_info = common.parse_driver_info(task.node)

        if device not in self.get_supported_boot_devices():
            raise exception.InvalidParameterValue(
                _("Invalid boot device %s specified.") % device)

        node_has_server_profile = (oneview_client
                                   .get_server_profile_from_hardware(
                                       driver_info
                                   )
                                   )
        if not node_has_server_profile:
            raise exception.OperationNotPermitted(
                _("A Server Profile is not associated with the node."))

        device_to_oneview = BOOT_DEVICE_MAPPING_TO_OV.get(device)
        oneview_client.set_boot_device(driver_info, device_to_oneview)

    def get_boot_device(self, task):
        driver_info = common.parse_driver_info(task.node)
        node_has_server_profile = (oneview_client
                                   .get_server_profile_from_hardware(
                                       driver_info
                                   )
                                   )

        if not node_has_server_profile:
            raise exception.OperationNotPermitted(
                _("A Server Profile is not associated with the node."))

        boot_order = oneview_client.get_boot_order(driver_info)
        boot_device = {
            'boot_device': BOOT_DEVICE_OV_TO_GENERIC.get(boot_order[0]),
            'persistent': False
        }

        return boot_device

    def get_sensors_data(self, task):
        return {}
