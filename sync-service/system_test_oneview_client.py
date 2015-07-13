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

from oneview_client import OneViewClient
from sync_exceptions import OneViewConnectionError


class OneViewClientTestCase(unittest.TestCase):


    def test_get_server_hardware_by_valid_uri(self):
        ov_client = OneViewClient()
        result = ov_client.server_hardware_api.get_server_hardware("/rest/server-hardware/30313436-3631-5242-4333-323033414653")
        print result


    def test_should_raise_error_when_invalid_uri_requested(self):
        ov_client = OneViewClient()
        try:
            ov_client.server_hardware_api.get_server_hardware("invalid-rest-uri")
            self.fail()
        except OneViewConnectionError as ex:
            pass


    def test_get_sh_as_dict(self):
        ov_client = OneViewClient()
        server_hardware = ov_client.server_hardware_api.get_server_hardware("/rest/server-hardware/30313436-3631-5242-4333-323033414653")
        ov_client.server_hardware_api.parse_server_hardware_to_dict(server_hardware)


if __name__ == '__main__':
    unittest.main()
