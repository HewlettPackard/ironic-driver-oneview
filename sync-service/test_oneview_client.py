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

import config_client

import mock
import requests
import unittest

import manage_ironic_nodes
import service_manager

from config_client import OneViewConfClient as oneview_conf
from oneview_client import OneViewRequestAPI


class OneViewRequestAPITestCase(unittest.TestCase):

    def setUp(self):
        self.ov_request_api = OneViewRequestAPI()

    @mock.patch.object(oneview_conf, 'get_allow_insecure_connections',
                       autospec=True)
    @mock.patch.object(oneview_conf, 'get_tls_cacert_file', autospec=True)
    def test__get_verify_connection_option_with_insecure_connection_true(
        self, mock_get_tls_cacert_file, mock_get_allow_insecure_connections):
        mock_get_allow_insecure_connections.return_value = True
        mock_get_tls_cacert_file.return_value = True
        self.assertFalse(self.ov_request_api._get_verify_connection_option())
        mock_get_tls_cacert_file.return_value = False
        self.assertFalse(self.ov_request_api._get_verify_connection_option())

    @mock.patch.object(oneview_conf, 'get_allow_insecure_connections',
                       autospec=True)
    @mock.patch.object(oneview_conf, 'get_tls_cacert_file', autospec=True)
    def test__get_verify_connection_option_with_insecure_connection_false(
        self, mock_get_tls_cacert_file, mock_get_allow_insecure_connections):
        mock_get_allow_insecure_connections.return_value = False
        mock_get_tls_cacert_file.return_value = True
        self.assertTrue(self.ov_request_api._get_verify_connection_option())
        mock_get_tls_cacert_file.return_value = False
        self.assertFalse(self.ov_request_api._get_verify_connection_option())
        mock_get_tls_cacert_file.return_value = None
        self.assertTrue(self.ov_request_api._get_verify_connection_option())

    @mock.patch.object(requests, 'request', autospec=True)
    def test__try_execute_request(self, mock_requests):
        response = requests.Response()
        response.json = mock.MagicMock(return_value={'sessionID': 'logged'})
        mock_requests.return_value = response
        self.assertEqual(
            self.ov_request_api._try_execute_request('url', 'GET', None, {},
                                                     True),
            response)

    @mock.patch.object(OneViewRequestAPI, '_try_execute_request',
                       autospec=True)
    @mock.patch.object(oneview_conf, 'get_manager_url', autospec=True)
    @mock.patch.object(oneview_conf, 'get_password', autospec=True)
    @mock.patch.object(oneview_conf, 'get_username', autospec=True)
    def test__new_token_valid_login(
        self, mock_username, mock_password, mock_manage_url, mock_requests):
        response = requests.Response()
        response.json = mock.MagicMock(return_value={'sessionID': 'logged'})
        mock_requests.return_value = response
        mock_manage_url.return_value = 'url'
        mock_password.return_value = 'pass'
        mock_username.return_value = 'user'
        self.assertEqual(self.ov_request_api._new_token(), 'logged')

    @mock.patch.object(OneViewRequestAPI, '_new_token', autospec=True)
    def test__update_token(self, mock_requests):
        mock_requests.return_value = 'token'
        self.assertIsNone(self.ov_request_api.token)
        self.ov_request_api._update_token()
        self.assertIsNotNone(self.ov_request_api.token)

    @mock.patch.object(OneViewRequestAPI, '_try_execute_request',
                       autospec=True)
    @mock.patch.object(oneview_conf, 'get_manager_url', autospec=True)
    def test_prepare_and_do_request(self, mock_manage_url, mock_requests):
        response = requests.Response()
        response.json = mock.MagicMock(return_value={'sessionID': 'logged'})
        mock_requests.return_value = response
        mock_manage_url.return_value = 'url'
        self.assertEqual(self.ov_request_api.prepare_and_do_request('uri'),
                         {'sessionID': 'logged'})


class OneViewServerHardwareAPITestCase(unittest.TestCase):
    def setUp(self):
        self.ov_request_api = OneViewRequestAPI()


class ManageIronicNodeTestCase (unittest.TestCase):

    def test_create_ironic_node(self):
        server_hardware_uri = '/rest/server-hardware/37333036-3831-4753-4831-30305838524E'
        server_hardware_json = service_manager.get_server_hardware(server_hardware_uri)
        server_hardware_info = service_manager.parse_server_hardware_to_dict(server_hardware_json)
        node = manage_ironic_nodes.create_ironic_node(server_hardware_info)
        assert node is not None
        manage_ironic_nodes.delete_ironic_node(server_hardware_uri)

    def test_delete_ironic_node(self):
        server_hardware_uri = '/rest/server-hardware/31393736-3831-4753-4831-30315837524E'
        server_hardware_json = service_manager.get_server_hardware(server_hardware_uri)
        server_hardware_info = service_manager.parse_server_hardware_to_dict(server_hardware_json)
        node = manage_ironic_nodes.create_ironic_node(server_hardware_info)
        manage_ironic_nodes.delete_ironic_node(server_hardware_uri)
        assert manage_ironic_nodes.get_ironic_node_by_server_hardware_uri(server_hardware_uri) is None


    def test_maintenance_state_out(self):
        server_hardware_uri = '/rest/server-hardware/31393736-3831-4753-4831-30305837524E'
        server_hardware_json = service_manager.get_server_hardware(server_hardware_uri)
        server_hardware_info = service_manager.parse_server_hardware_to_dict(server_hardware_json)
        manage_ironic_nodes.create_ironic_node(server_hardware_info)
        manage_ironic_nodes.set_node_maintenance_state(server_hardware_uri, 'true')
        node = manage_ironic_nodes.get_ironic_node_by_server_hardware_uri(server_hardware_uri)
        self.assertTrue(node.maintenance)
        manage_ironic_nodes.set_node_maintenance_state(server_hardware_uri, 'false')
        node = manage_ironic_nodes.get_ironic_node_by_server_hardware_uri(server_hardware_uri)
        self.assertFalse(node.maintenance)
        manage_ironic_nodes.delete_ironic_node(server_hardware_uri)


if __name__ == '__main__':
    unittest.main()
