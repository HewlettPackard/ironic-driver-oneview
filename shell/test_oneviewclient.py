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

import unittest
import mock

from oneviewclient import Client

class TesOneViewClient(unittest.TestCase):

    def setUp(self):
        self.client = Client('address', 'username', 'password')

    def _mock_oneview_and_return_client_function(self,
                                                oneview_server_profile_list,
                                                client_function):
        with mock.patch('oneviewclient.OneViewRequest.prepare_and_do_request') as mock_req:
            mock_req.return_value = oneview_server_profile_list
            return client_function()

    def _mock_oneview_server_profiles_and_verify__server_profile_list_has_same_length(
        self, oneview_server_profile_list):
        server_profile_list = self._mock_oneview_and_return_client_function(
            {'members': oneview_server_profile_list},
            self.client._server_profile_list)
        self.assertTrue(len(server_profile_list) == len(server_profile_list))

    def _mock_oneview_server_profiles_and_verify__server_profile_template_list_has_same_length(
        self, oneview_server_profile_list, oneview_server_profile_template_list):
        server_profile_list = self._mock_oneview_and_return_client_function(
            {'members': oneview_server_profile_list + oneview_server_profile_template_list},
            self.client._server_profile_template_list)
        self.assertTrue(len(oneview_server_profile_template_list) == len(server_profile_list))

    def _mock_oneview_server_profiles_and_verify_flavor_list_has_same_length(
        self, oneview_server_profile_list, oneview_server_profile_template_list):
        flavor_list = self._mock_oneview_and_return_client_function(
            {'members': oneview_server_profile_list + oneview_server_profile_template_list},
            self.client.flavor_list)
        self.assertTrue(len(oneview_server_profile_template_list) == len(flavor_list))

    def test__server_profile_list_empty_when_oneview_has_no_server_profiles(self):
        self._mock_oneview_server_profiles_and_verify__server_profile_list_has_same_length([])

    def test__server_profile_list_length_one_when_oneview_has_one_server_profiles(self):
        self._mock_oneview_server_profiles_and_verify__server_profile_list_has_same_length([{'name': 'sp1'}])

    def test__server_profile_template_list_same_length_as_oneview_server_profiles_without_serverhardware(self):
        self._mock_oneview_server_profiles_and_verify__server_profile_template_list_has_same_length(
            oneview_server_profile_list=[], oneview_server_profile_template_list=[])
        self._mock_oneview_server_profiles_and_verify__server_profile_template_list_has_same_length(
            oneview_server_profile_list=[{'serverHardwareUri': 'uri'}], oneview_server_profile_template_list=[])

    def test__server_profile_template_list_length_one_when_oneview_has_one_server_profiles_without_serverhardware(self):
        oneview_server_profile_list_length_one = [{'serverHardwareUri': 'uri'}]
        oneview_server_profile_template_list_length_one = [{'name': 'sp1'}]
        self._mock_oneview_server_profiles_and_verify__server_profile_template_list_has_same_length(
            oneview_server_profile_list=oneview_server_profile_list_length_one,
            oneview_server_profile_template_list=oneview_server_profile_template_list_length_one)
        self._mock_oneview_server_profiles_and_verify__server_profile_template_list_has_same_length(
            oneview_server_profile_list=[],
            oneview_server_profile_template_list=oneview_server_profile_template_list_length_one)

    def _create_server_profile_list(self, length, is_template=False):
        server_profile_list = []
        for i in range(length):
            server_profile = {'name': 'SP' + str(i)}
            if is_template:
                server_profile['serverHardwareUri'] = 'uri' + str(i)
            server_profile_list.append(server_profile)

        return server_profile_list

    def _mock_server_profiles_and_verify_flavor_list_length(
        self, server_profile_list_length, server_profile_template_list_length):
        server_profile_list = self._create_server_profile_list(
            length=server_profile_list_length)
        server_profile_template_list = self._create_server_profile_list(
            length=server_profile_template_list_length, is_template=True)
        flavor_list = self._mock_oneview_and_return_client_function(
            {'members': server_profile_list + server_profile_template_list},
            self.client.flavor_list)
        self.assertEquals(len(server_profile_template_list), len(flavor_list))


    def test_flavor_list_empty_when_oneview_has_no_server_profiles_templates(self):
        self._mock_server_profiles_and_verify_flavor_list_length(
            server_profile_list_length=0,
            server_profile_template_list_length=0)

    def test_flavor_list_length_one_when_oneview_has_one_server_profiles_template(self):
        self._mock_server_profiles_and_verify_flavor_list_length(
            server_profile_list_length=0,
            server_profile_template_list_length=1)

    # def test_flavor_list_not_empty(self):
    #    oneview_server_profile_list = [{'name': 'sp1'}]
    #    self.assertTrue(len(self._mock_and_get_server_profile_list(oneview_server_profile_list, self.client.flavor_list)) == len(oneview_server_profile_list))

if __name__ == '__main__':
    unittest.main()

