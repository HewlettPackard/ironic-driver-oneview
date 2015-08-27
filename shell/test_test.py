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

import unittest
import mock

from oneviewclient import Client
from oneviewclient import OneViewRequest
from objects import Flavor


class TestOneViewClient(unittest.TestCase):

    def setUp(self):
        self.client = Client('address', 'username', 'password')

    @mock.patch.object(OneViewRequest, 'server_profile_list', autospec=True)
    @mock.patch.object(OneViewRequest, 'server_hardware_list', autospec=True)
    def test_flavor_list_empty_when_oneview_has_no_server_profile_template(self, mock_sh, mock_sp):
        server_hardware_list_empty = []
        server_profile_list_empty = []
        server_profile_template_list_empty = []
        mock_sh.return_value = server_hardware_list_empty
        mock_sp.return_value = server_profile_list_empty

        self.assertEquals(list(self.client.flavor_list()), [])

    @mock.patch.object(OneViewRequest, 'server_profile_list', autospec=True)
    @mock.patch.object(OneViewRequest, 'server_hardware_list', autospec=True)
    @mock.patch.object(OneViewRequest, 'get_volumes', autospec=True)
    def test_flavor_list_reflects_server_profile_template_and_server_hardware(self, mock_vo, mock_sh, mock_sp):
        server_hardware_list_not_empty = [{'name': 'sh1', 'serverHardwareTypeUri': 'shtUri1', 'enclosureGroupUri': 'egUri1', 'memoryMb': 16384, 'processorCoreCount': 3, 'processorCount': 2, }]
        server_profile_list_not_empty = [{'name': 'sp1', 'serverHardwareTypeUri': 'shtUri1', 'enclosureGroupUri': 'egUri1', 'sanStorage': {'volumeAttachments': [{'volumeUri': 'volUri1'}]}, 'uri': 'spUri1'}]

        expected_flavor = {}
        expected_flavor['ram_mb'] = 16384
        expected_flavor['cpus'] = 6
        expected_flavor['disk'] = 2

        extra_spec = {}
        extra_spec['cpu_arch'] = 'x86_64'
        extra_spec['oneview:server_profile_template_uri'] = 'spUri1'
        extra_spec['capabilities:server_hardware_type_uri'] = 'shtUri1'
        extra_spec['capabilities:enclosure_group_uri'] = 'egUri1'

        expected_flavor['extra_specs'] = extra_spec

        expected_flavor_list = [Flavor(len(list(self.client.flavor_list())) + 1, info=expected_flavor)]

        mock_sh.return_value = server_hardware_list_not_empty
        mock_sp.return_value = server_profile_list_not_empty
        mock_vo.return_value = {'provisionedCapacity': 1073741824 * 2}

        # self.assertEquals(sorted(list(self.client.flavor_list())), sorted(expected_flavor_list))



    def test_server_hardware_and_server_profile_not_empty(self):
        return_value = self.client.flavor_list()
        print(return_value)
        self.assertFalse([] == return_value)

if __name__ == '__main__':
    unittest.main()
