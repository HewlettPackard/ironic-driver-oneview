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
import requests
from requests import exceptions


import sys
sys.path.insert(0, '../../opt/stack/ironic/')



class TestOneViewFlavorListTable(unittest.TestCase):

  def setUp(self):
    self.client_real = Client('150.165.85.176', 'administrator', '1r0n1c@LSD')
    self.flavor_list_real = self.client_real.flavor_list()
    self.oneviewrequest = OneViewRequest('150.165.85.176', 'administrator', '1r0n1c@LSD')
    self.client_fake = Client('address', 'username', 'password')


  def test_list_not_empty_using_real_oneview_with_server_hardwares_and_server_profiles(self):
    server_hardware_list = self.oneviewrequest.server_hardware_list()
    server_profile_list = self.oneviewrequest.server_profile_list()


    self.assertTrue([] != server_hardware_list)
    self.assertTrue([] != server_profile_list)
    self.assertTrue([] != self.flavor_list_real)


  def test_connection_error_no_valid_auth(self):
    with self.assertRaises(exceptions.ConnectionError):
         flavor_list_error = self.client_fake.flavor_list()


  @mock.patch.object(OneViewRequest, 'server_profile_list', autospec=True)
  @mock.patch.object(OneViewRequest, 'server_hardware_list', autospec=True)
  def test_flavor_list_empty_when_oneview_has_no_server_profile_template(self, mock_sh, mock_sp):
    server_hardware_list_empty = []
    server_profile_list_empty = []
    server_profile_template_list_empty = []
    mock_sh.return_value = server_hardware_list_empty
    mock_sp.return_value = server_profile_list_empty

    self.assertEquals(list(self.client_real.flavor_list()), [])



  @mock.patch.object(OneViewRequest, 'server_profile_list', autospec=True)
  def test_flavor_list_empty_when_oneview_has_no_server_profile(self, mock_sp):
    server_profile_list_empty = []
    server_profile_template_list_empty = []
    mock_sp.return_value = server_profile_list_empty

    self.assertEquals(list(self.client_real.flavor_list()), [])


  @mock.patch.object(OneViewRequest, 'server_hardware_list', autospec=True)
  def test_flavor_list_empty_when_oneview_has_no_server_hardware(self, mock_sh):
    server_hardware_list_empty = []
    mock_sh.return_value = server_hardware_list_empty

    self.assertEquals(list(self.client_real.flavor_list()), [])





if __name__ == '__main__':
   suite = unittest.TestLoader().loadTestsFromTestCase(TestOneViewFlavorListTable)
   unittest.TextTestRunner(verbosity=2).run(suite)
