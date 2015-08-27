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

from objects import Flavor
import mock
import unittest


class TestObjects(unittest.TestCase):
    def _get_flavor_default(self, **kwargs):
        flavor = {}
        for key, value in kwargs.items():
            flavor[key] = value
        return Flavor(id=1, info=flavor)

    def test_flavor_get_attributes(self):
        flavor = self._get_flavor_default(key='value')
        self.assertEquals(flavor.key, 'value')

    def test_extra_specs_without_enclosure_group(self):
        flavor = self._get_flavor_default(
            cpu_arch='arch', server_profile_template_uri='spt_uri',
            server_hardware_type_uri='sht_uri',
            enclosure_group_uri=None)
        extra_specs = flavor.extra_specs()
        self.assertEquals(extra_specs.get('cpu_arch'), 'arch')
        self.assertEquals(
            extra_specs.get('capabilities:server_profile_template_uri'),
            's!= spt_uri')
        self.assertEquals(
            extra_specs.get('capabilities:server_hardware_type_uri'),
            'sht_uri')

    def test_extra_specs_with_enclosure_group(self):
        flavor = self._get_flavor_default(
            cpu_arch='arch', server_profile_template_uri='spt_uri',
            server_hardware_type_uri='sht_uri',
            enclosure_group_uri='eg_uri')
        extra_specs = flavor.extra_specs()
        self.assertEquals(extra_specs.get('cpu_arch'), 'arch')
        self.assertEquals(
            extra_specs.get('capabilities:server_profile_template_uri'),
            's!= spt_uri')
        self.assertEquals(
            extra_specs.get('capabilities:server_hardware_type_uri'),
            'sht_uri')
        self.assertEquals(
            extra_specs.get('capabilities:enclosure_group_uri'),
            'eg_uri')


if __name__ == '__main__':
    unittest.main()
