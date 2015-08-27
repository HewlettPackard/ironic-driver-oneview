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

import mock

from ironic.common import driver_factory
from ironic.common import exception
from ironic.common.glance_service import base_image_service
from ironic.conductor import task_manager
from ironic.drivers.modules.oneview import common
from ironic.drivers.modules.oneview import oneview_client
from ironic.tests.conductor import utils as mgr_utils
from ironic.tests.db import base as db_base
from ironic.tests.objects import utils as obj_utils

from oslo_utils import uuidutils


# TODO(afaranha) move this variable to db_utils.get_test_oneview_properties()
PROPERTIES_DICT = {"cpu_arch": "x86_64",
                   "cpus": "8",
                   "local_gb": "10",
                   "memory_mb": "4096",
                   "capabilities": "server_hardware_type_uri:fake_sht_uri,"
                                   "enclosure_group_uri:fake_eg_uri"}
# "server_profile_template_uri": 'fake_spt_uri'

EXTRA_DICT = {'server_hardware_uri': 'fake_sh_uri'}
DRIVER_INFO_DICT = {}
INSTANCE_INFO_DICT = {"capabilities":
                      "server_profile_template_uri:fake_spt_uri"}


class OneViewDeployDriverTestCase(db_base.DbTestCase):

    def setUp(self):
        super(OneViewDeployDriverTestCase, self).setUp()
        self.config(manager_url='https://1.2.3.4', group='oneview')
        self.config(username='user', group='oneview')
        self.config(password='password', group='oneview')

        self.mock_verify_oneview_version_obj = mock.patch.object(
            oneview_client,
            'verify_oneview_version',
            autospec=True,
            return_value=120
        )
        self.mock_verify_oneview_version = (self
                                            .mock_verify_oneview_version_obj
                                            .start())
        self.addCleanup(self.mock_verify_oneview_version_obj.stop)
        self.mock_check_oneview_status_obj = mock.patch.object(
            oneview_client,
            'check_oneview_status',
            autospec=True,
            return_value=200
        )
        self.mock_check_oneview_status = (self
                                          .mock_check_oneview_status_obj
                                          .start())
        self.addCleanup(self.mock_check_oneview_status_obj.stop)

        mgr_utils.mock_the_extension_manager(driver="fake_oneview")
        self.driver = driver_factory.get_driver("fake_oneview")

        self.node = obj_utils.create_test_node(
            self.context, driver='fake_oneview', properties=PROPERTIES_DICT,
            extra=EXTRA_DICT, driver_info=DRIVER_INFO_DICT,
            instance_info=INSTANCE_INFO_DICT)
        self.info = common.parse_driver_info(self.node)

    @mock.patch.object(base_image_service.BaseImageService, '_show')
    def test_deploy_interface_validate_good(self, mock_glance):
        mock_glance.return_value = {'properties': {'kernel_id': 'fake-kernel',
                                                   'ramdisk_id': 'fake-initr'}}
        with task_manager.acquire(self.context, self.node.uuid,
                                  shared=True) as task:
            task.driver.deploy.validate(task)

    def test_deploy_interface_validate_fail(self):
        node = obj_utils.create_test_node(self.context,
                                          uuid=uuidutils.generate_uuid(),
                                          id=999,
                                          driver='fake_oneview')
        with task_manager.acquire(self.context, node.uuid) as task:
            self.assertRaises(exception.MissingParameterValue,
                              task.driver.deploy.validate, task)

    def test_deploy_interface_get_properties(self):
        expected = common.COMMON_PROPERTIES
        with task_manager.acquire(self.context, self.node.uuid,
                                  shared=True) as task:
            self.assertEqual(expected, task.driver.deploy.get_properties())

    def test_deploy_interface_prepare(self):
        pass

    def test_deploy_interface_deploy(self):
        pass

    def test_deploy_interface_tear_down(self):
        pass

    def test_deploy_interface_clean_up(self):
        pass

    def test_deploy_interface_take_over(self):
        pass
