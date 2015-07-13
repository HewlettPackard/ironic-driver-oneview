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

from ironic.common import exception
from ironic.drivers.modules.oneview import common
from ironic.drivers.modules.oneview import oneview_client
from ironic.tests.db import base as db_base
from ironic.tests.objects import utils as obj_utils


PROPERTIES_DICT = {"cpu_arch": "x86_64",
                   "cpus": "8",
                   "local_gb": "10",
                   "memory_mb": "4096",
                   "capabilities": "server_hardware_type_uri:fake_sht_uri,"
                                   "enclosure_group_uri:fake_eg_uri"}

EXTRA_DICT = {'server_hardware_uri': 'fake_sh_uri'}
DRIVER_INFO_DICT = {}
INSTANCE_INFO_DICT = {"capabilities":
                      '{"server_profile_template_uri":"s!=fake_spt_uri"}'}


class OneViewCommonTestCase(db_base.DbTestCase):

    def setUp(self):
        super(OneViewCommonTestCase, self).setUp()
        self.node = obj_utils.create_test_node(
            self.context, driver='fake_oneview', properties=PROPERTIES_DICT,
            extra=EXTRA_DICT, driver_info=DRIVER_INFO_DICT,
            instance_info=INSTANCE_INFO_DICT)

    def tearDown(self):
        super(OneViewCommonTestCase, self).tearDown()
        self.node.properties = PROPERTIES_DICT
        self.node.extra = EXTRA_DICT
        self.node.driver_info = DRIVER_INFO_DICT
        self.node.instance_info = INSTANCE_INFO_DICT

    @mock.patch.object(oneview_client, 'get_server_hardware', autospec=True)
    def test_node_has_server_profile(self, mock_get_server_hardware):
        mock_get_server_hardware.return_value = {
            "serverProfileUri": "/rest/any"
        }
        self.assertTrue(common.node_has_server_profile({}))

    def test__capabilities_to_dict(self):
        capabilities_more_than_one_item = 'a:b,c:d'
        capabilities_exactly_one_item = 'e:f'
        capabilities_without_items = ''

        self.assertEqual(common._capabilities_to_dict(
            capabilities_without_items), {}
        )

        self.assertEqual(common._capabilities_to_dict(
            capabilities_exactly_one_item), {'e': 'f'}
        )

        self.assertEqual(common._capabilities_to_dict(
            capabilities_more_than_one_item), {'a': 'b', 'c': 'd'}
        )

    def test__capabilities_to_dict_with_only_key_or_value_fail(self):
        capabilities_only_key_or_value = 'xpto'
        try:
            common._capabilities_to_dict(capabilities_only_key_or_value)
            self.fail()
        except exception.InvalidParameterValue as e:
            self.assertEqual('Malformed capabilities value: xpto', str(e))

    def test__capabilities_to_dict_with_invalid_character_fail(self):
        capabilities_invalid_character_end = 'xpto:a,'
        capabilities_invalid_character_beggining = ',xpto:a'

        try:
            common._capabilities_to_dict(capabilities_invalid_character_end)
            self.fail()
        except exception.InvalidParameterValue as e:
            self.assertEqual('Malformed capabilities value: ', str(e))

        try:
            common._capabilities_to_dict(
                capabilities_invalid_character_beggining
            )
            self.fail()
        except exception.InvalidParameterValue as e:
            self.assertEqual('Malformed capabilities value: ', str(e))

    def test__capabilities_to_dict_with_incorrect_format_fail(self):
        capabilities_incomplete_key = ':xpto,'
        capabilities_incomplete_value = 'xpto:,'
        capabilities_incomplete_key_and_value = ':,'

        try:
            common._capabilities_to_dict(capabilities_incomplete_key)
            self.fail()
        except exception.InvalidParameterValue as e:
            self.assertEqual('Malformed capabilities value: ', str(e))

        try:
            common._capabilities_to_dict(capabilities_incomplete_value)
            self.fail()
        except exception.InvalidParameterValue as e:
            self.assertEqual('Malformed capabilities value: ', str(e))

        try:
            common._capabilities_to_dict(capabilities_incomplete_key_and_value)
            self.fail()
        except exception.InvalidParameterValue as e:
            self.assertEqual('Malformed capabilities value: ', str(e))

    def test_parse_driver_info(self):
        complete_node = self.node
        expected_node_info = {
            'server_hardware_uri': 'fake_sh_uri',
            'server_hardware_type_uri': 'fake_sht_uri',
            'enclosure_group_uri': 'fake_eg_uri',
            'server_profile_template_uri': 'fake_spt_uri',
        }

        self.assertEqual(
            expected_node_info,
            common.parse_driver_info(complete_node)
        )

    def test_parse_driver_info_missing_properties(self):
        self.node.properties = {
            "cpu_arch": "x86_64",
            "cpus": "8",
            "local_gb": "10",
            "memory_mb": "4096",
            "capabilities": "enclosure_group_uri:fake_eg_uri"
        }

        try:
            common.parse_driver_info(self.node)
            self.fail()
        except exception.MissingParameterValue as e:
            self.assertEqual("Missing the following OneView data in "
                              "node\'s properties/capabilities: "
                              "server_hardware_type_uri.", str(e))

    def test_parse_driver_info_missing_extra(self):
        self.node.extra = {}
        try:
            common.parse_driver_info(self.node)
            self.fail()
        except exception.MissingParameterValue as e:
            self.assertEqual("Missing the following OneView data in "
                              "node\'s extra: server_hardware_uri.", str(e))

    def test_parse_driver_info_catch_invalid_spt(self):
        self.node.instance_info = {
            "capabilities": "server_profile_template_uri,fake_spt_uri"
        }

        expected_node_info = {
            'server_hardware_uri': 'fake_sh_uri',
            'server_hardware_type_uri': 'fake_sht_uri',
            'enclosure_group_uri': 'fake_eg_uri',
            'server_profile_template_uri': '',
        }

        self.assertEqual(
            expected_node_info,
            common.parse_driver_info(self.node)
        )
