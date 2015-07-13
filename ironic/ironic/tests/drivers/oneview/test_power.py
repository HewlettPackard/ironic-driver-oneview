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

import mock

from ironic.common import driver_factory
from ironic.common import exception
from ironic.common import states
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


class OneViewPowerDriverTestCase(db_base.DbTestCase):

    def setUp(self):
        super(OneViewPowerDriverTestCase, self).setUp()
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

    def test_power_interface_validate_good(self):
        with task_manager.acquire(self.context, self.node.uuid) as task:
            task.driver.power.validate(task)

    def test_power_interface_validate_fail(self):
        node = obj_utils.create_test_node(self.context,
                                          uuid=uuidutils.generate_uuid(),
                                          id=999,
                                          driver='fake_oneview')
        with task_manager.acquire(self.context, node.uuid) as task:
            self.assertRaises(exception.MissingParameterValue,
                              task.driver.power.validate, task)

    def test_power_interface_get_properties(self):
        expected = common.COMMON_PROPERTIES
        self.assertItemsEqual(expected, self.driver.power.get_properties())

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    def test_get_power_state(self, mock_exec):
        returns = iter([{'powerState': 'Off'},
                        {'powerState': 'On'},
                        {'powerState': 'PoweringOff'},
                        {'powerState': 'PoweringOn'},
                        {'powerState': 'Resetting'},
                        {'powerState': 'Unknown'}])

        expected = [mock.call(uri=self.info.get('server_hardware_uri'),
                              request_type='GET'),
                    mock.call(uri=self.info.get('server_hardware_uri'),
                              request_type='GET'),
                    mock.call(uri=self.info.get('server_hardware_uri'),
                              request_type='GET'),
                    mock.call(uri=self.info.get('server_hardware_uri'),
                              request_type='GET'),
                    mock.call(uri=self.info.get('server_hardware_uri'),
                              request_type='GET'),
                    mock.call(uri=self.info.get('server_hardware_uri'),
                              request_type='GET')]

        mock_exec.side_effect = returns

        with task_manager.acquire(self.context, self.node.uuid) as task:
            pstate = self.driver.power.get_power_state(task)
            self.assertEqual(states.POWER_OFF, pstate)
            pstate = self.driver.power.get_power_state(task)
            self.assertEqual(states.POWER_ON, pstate)
            pstate = self.driver.power.get_power_state(task)
            self.assertEqual(states.POWER_ON, pstate)
            pstate = self.driver.power.get_power_state(task)
            self.assertEqual(states.POWER_OFF, pstate)
            pstate = self.driver.power.get_power_state(task)
            self.assertEqual(states.REBOOT, pstate)
            pstate = self.driver.power.get_power_state(task)
            self.assertEqual(states.ERROR, pstate)

        self.assertEqual(mock_exec.call_args_list, expected)

    @mock.patch.object(oneview_client, 'power_on', autospec=True)
    @mock.patch.object(oneview_client, 'power_off', autospec=True)
    def test_set_power_on_ok(self, mock_off, mock_on):
        mock_on.return_value = states.POWER_ON
        with task_manager.acquire(self.context, self.node['uuid']) as task:
            self.driver.power.set_power_state(task, states.POWER_ON)
        mock_on.assert_called_once_with(self.info)
        self.assertFalse(mock_off.called)

    @mock.patch.object(oneview_client, 'power_on', autospec=True)
    @mock.patch.object(oneview_client, 'power_off', autospec=True)
    def test_set_power_off_ok(self, mock_off, mock_on):
        mock_off.return_value = states.POWER_OFF
        with task_manager.acquire(self.context, self.node['uuid']) as task:
            self.driver.power.set_power_state(task, states.POWER_OFF)
        mock_off.assert_called_once_with(self.info)
        self.assertFalse(mock_on.called)

    @mock.patch.object(oneview_client, 'power_on', autospec=True)
    @mock.patch.object(oneview_client, 'power_off', autospec=True)
    def test_set_power_on_fail(self, mock_off, mock_on):
        mock_on.return_value = states.ERROR
        with task_manager.acquire(self.context, self.node['uuid']) as task:
            self.assertRaises(exception.PowerStateFailure,
                              self.driver.power.set_power_state, task,
                              states.POWER_ON)
        mock_on.assert_called_once_with(self.info)
        self.assertFalse(mock_off.called)

    def test_set_power_invalid_state(self):
        with task_manager.acquire(self.context, self.node['uuid']) as task:
            self.assertRaises(exception.InvalidParameterValue,
                              self.driver.power.set_power_state, task,
                              "fake state")

    @mock.patch.object(oneview_client, 'get_node_power_state', autospec=True)
    @mock.patch.object(oneview_client, 'power_off', autospec=False)
    @mock.patch.object(oneview_client, 'power_on', autospec=False)
    def test_reboot_ok(self, mock_on, mock_off, mock_state):
        manager = mock.MagicMock()
        mock_on.return_value = states.POWER_ON
        manager.attach_mock(mock_off, 'power_off')
        manager.attach_mock(mock_on, 'power_on')
        expected = [mock.call.power_off(self.info),
                    mock.call.power_on(self.info)]

        with task_manager.acquire(self.context,
                                  self.node['uuid']) as task:
            self.driver.power.reboot(task)

        self.assertEqual(manager.mock_calls, expected)

    @mock.patch.object(oneview_client, 'get_node_power_state', autospec=True)
    @mock.patch.object(oneview_client, 'power_off', autospec=False)
    @mock.patch.object(oneview_client, 'power_on', autospec=False)
    def _test_reboot_fail(self, mock_on, mock_off, mock_state):
        manager = mock.MagicMock()
        mock_on.return_value = states.ERROR
        manager.attach_mock(mock_off, 'power_off')
        manager.attach_mock(mock_on, 'power_on')
        expected = [mock.call.power_off(self.info),
                    mock.call.power_on(self.info)]

        with task_manager.acquire(self.context,
                                  self.node['uuid']) as task:
            self.assertRaises(exception.PowerStateFailure,
                              self.driver.power.reboot,
                              task)

        self.assertEqual(manager.mock_calls, expected)
