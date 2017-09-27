# Copyright (2016-2017) Hewlett Packard Enterprise Development LP
# Copyright (2016-2017) Universidade Federal de Campina Grande
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
import unittest

from ironic_oneview_cli import common
from ironic_oneview_cli.create_flavor_shell import (
    commands as create_flavor_cmd)
from ironic_oneview_cli.create_flavor_shell import (
    objects as flavor_objs)
from ironic_oneview_cli.create_node_shell import (
    commands as create_node_cmd)
from ironic_oneview_cli import facade
from ironic_oneview_cli.tests import stubs

POOL_OF_STUB_IRONIC_NODES = [
    stubs.StubIronicNode(
        id=1,
        uuid='111111111-2222-8888-9999-000000000000',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        provision_state='enroll',
        ports=[
            {'id': 987,
             'uuid': '11111111-2222-3333-4444-555555555555',
             'node_uuid': '66666666-7777-8888-9999-000000000000',
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}
        ],
        driver='agent_pxe_oneview',
        driver_info={'user': 'foo',
                     'password': 'bar'},
        properties={'num_cpu': 4},
        name='fake-node-1',
        extra={}
    ),
    stubs.StubIronicNode(
        id=2,
        uuid='22222222-3333-8888-9999-000000000000',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        provision_state='enroll',
        ports=[
            {'id': 987,
             'uuid': '11111111-2222-3333-4444-555555555555',
             'node_uuid': '66666666-7777-8888-9999-000000000000',
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}
        ],
        driver='iscsi_pxe_oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/22222",
                     'user': 'foo',
                     'password': 'bar'},
        properties={'num_cpu': 4},
        instance_uuid='1111-2222-3333-4444-5555',
        name='fake-node-1',
        extra={}
    ),
    stubs.StubIronicNode(
        id=3,
        uuid='33333333-2222-8888-9999-000000000000',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        provision_state='enroll',
        ports=[{}],
        driver='fake_oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/33333",
                     'user': 'foo',
                     'password': 'bar'},
        properties={'cpu_arch': 'x86_64',
                    'capabilities': 'server_hardware_type_uri:'
                                    '/rest/server-hardware-types/'
                                    '61720699-7D89-4E3E-BFC4-32FB9BBE2E71/'
                                    'enclosure_group_uri:'
                                    '/rest/enclosure-groups/'
                                    'c02d2e96-6142-49d6-bd38-0ce9d371e94f'
                                    'server_profile_template_uri:'
                                    '/rest/server-profile-templates/'
                                    '40ca74f8-65af-419a-b0cc-76af12b4f908'},
        name='fake-node-3',
        extra={}
    ),
    stubs.StubIronicNode(
        id=4,
        uuid='4444444-3333-8888-9999-000000000000',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        provision_state='enroll',
        ports=[{}],
        driver='fake',
        driver_info={'server_hardware_uri': "/rest/server-hardware/22222",
                     'user': 'foo',
                     'password': 'bar'},
        properties={'num_cpu': 4},
        name='fake-node-4',
        extra={}
    ),
    stubs.StubIronicNode(
        id=5,
        uuid='33333333-2222-8888-9999-000000000000',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        provision_state='enroll',
        ports=[{}],
        driver='oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/33333",
                     'user': 'foo',
                     'password': 'bar'},
        properties={'cpu_arch': 'x86_64',
                    'capabilities': 'server_hardware_type_uri:'
                                    '/rest/server-hardware-types/'
                                    '61720699-7D89-4E3E-BFC4-32FB9BBE2E71/'
                                    'enclosure_group_uri:'
                                    '/rest/enclosure-groups/'
                                    'c02d2e96-6142-49d6-bd38-0ce9d371e94f'
                                    'server_profile_template_uri:'
                                    '/rest/server-profile-templates/'
                                    '40ca74f8-65af-419a-b0cc-76af12b4f908'},
        name='fake-node-5',
        extra={}
    )
]

ENCLOSURE_GROUP = {
    "name": 'ENCLGROUP',
    "uuid": '22222222-TTTT-BBBB-9999-AAAAAAAAAAA',
    "uri": '/rest/server-hardware/22222222-TTTT-BBBB-9999-AAAAAAAAAAA',
}

SERVER_HARDWARE_TYPE = {
    "name": 'TYPETYPETYPE',
    "uuid": '22222222-7777-8888-9999-AAAAAAAAAAA',
    "uri": '/rest/server-hardware/22222222-7777-8888-9999-AAAAAAAAAAA',
}

POOL_OF_SERVER_HARDWARE = [
    {
        'name': 'AAAAA',
        'uuid': '11111111-7777-8888-9999-000000000000',
        'uri': '/rest/server-hardware/11111',
        'powerState': 'Off',
        'serverProfileUri': '',
        'serverHardwareTypeUri':
            '/rest/server-hardware-types/111112222233333',
        'serverGroupUri': '/rest/enclosure-groups/1111112222233333',
        'status': 'OK',
        'state': 'Unknown',
        'stateReason': '',
        'locationUri': '/rest/enclosures/1111112222233333',
        'processorCount': 12,
        'processorCoreCount': 12,
        'memoryMb': 16384,
        'portMap': {},
        'mpHostInfo': {}
    },
    {
        'name': 'BBBBB',
        'uuid': '22222222-7777-8888-9999-000000000000',
        'uri': '/rest/server-hardware/22222',
        'powerState': 'Off',
        'serverProfileUri': '/rest/server-profile/1111-2222',
        'serverHardwareTypeUri':
            '/rest/server-hardware-types/111111222233333',
        'serverGroupUri': '/rest/enclosure-groups/1111112222233333',
        'status': 'OK',
        'state': 'Unknown',
        'stateReason': '',
        'locationUri': '/rest/enclosures/1111112222233333',
        'processorCount': 12,
        'processorCoreCount': 12,
        'memoryMb': 16384,
        'portMap': {},
        'mpHostInfo': {}
    },
    {
        'name': 'CCCCC',
        'uuid': '33333333-7777-8888-9999-000000000000',
        'uri': '/rest/server-hardware/33333',
        'powerState': 'Off',
        'serverProfileUri': '',
        'serverHardwareTypeUri':
            '/rest/server-hardware-types/111111222223333',
        'serverGroupUri': '/rest/enclosure-groups/1111112222233333',
        'status': 'OK',
        'state': 'Unknown',
        'stateReason': '',
        'locationUri': '/rest/enclosures/1111112222233333',
        'processorCount': 12,
        'processorCoreCount': 12,
        'memoryMb': 16384,
        'portMap': {},
        'mpHostInfo': {}
    },
    {
        'name': 'RackServer',
        'uuid': '33333333-7777-8888-9999-111111',
        'uri': '/rest/server-hardware/44444',
        'powerState': 'Off',
        'serverProfileUri': '',
        'serverHardwareTypeUri':
            '/rest/server-hardware-types/111111222223333',
        'serverGroupUri': None,
        'status': 'OK',
        'state': 'Unknown',
        'stateReason': '',
        'locationUri': None,
        'processorCount': 12,
        'processorCoreCount': 12,
        'memoryMb': 16384,
        'portMap': {},
        'mpHostInfo': {}
    }
]


POOL_OF_SERVER_PROFILE_TEMPLATE = [
    {
        'uri': '/rest/server-profile-templates/1111112222233333',
        'name': 'TEMPLATETEMPLATETEMPLATE',
        'serverHardwareTypeUri':
            '/rest/server-hardware-types/111111222223333',
        'enclosureGroupUri': '/rest/enclosure-groups/1111112222233333',
        'connections': [],
        'boot': {}
    }
]

POOL_OF_STUB_NOVA_FLAVORS = [
    stubs.StubNovaFlavor(
        id=123,
        uuid='66666666-7777-8888-9999-000000000000',
        name='fake-flavor',
        memory_mb=32000,
        ram_mb=32000,
        vcpus=8,
        cpus=8,
        cpu_arch='x64',
        disk=120,
        root_gb=120,
        ephemeral_gb=0,
        flavorid='abc',
        swap=0,
        rxtx_factor=1,
        vcpu_weight=1,
        disabled=False,
        is_public=True,
        extra_specs={},
        projects=[]
    )
]


@mock.patch('ironic_oneview_cli.facade.Facade')
class UnitTestIronicOneviewCli(unittest.TestCase):
    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_get_oneview_nodes(self, mock_ironic_node_list, mock_facade):
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        oneview_nodes = common.get_oneview_nodes(ironic_nodes)

        self.assertEqual(5, len(ironic_nodes))
        self.assertEqual(4, len(list(oneview_nodes)))

    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_is_enrolled_on_ironic(self, mock_ironic_node_list, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        server_hardware = POOL_OF_SERVER_HARDWARE[1]

        self.assertTrue(node_creator.is_enrolled_on_ironic(server_hardware))

    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_is_enrolled_on_ironic_false(
        self, mock_ironic_node_list, mock_facade
    ):
        node_creator = create_node_cmd.NodeCreator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        server_hardware = POOL_OF_SERVER_HARDWARE[0]
        self.assertFalse(node_creator.is_enrolled_on_ironic(server_hardware))

    def test_is_server_profile_applied(self, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)

        self.assertTrue(node_creator.is_server_profile_applied(
            POOL_OF_SERVER_HARDWARE[1]))

    def test_is_server_profile_applied_false(self, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)

        self.assertFalse(node_creator.is_server_profile_applied(
            POOL_OF_SERVER_HARDWARE[0]))

    def test_list_server_hardware(self, mock_facade):
        mock_facade.filter_server_hardware_available.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        server_hardware_objects = (
            mock_facade.filter_server_hardware_available())

        self.assertEqual(len(POOL_OF_SERVER_HARDWARE),
                         len(server_hardware_objects))

    def test_get_flavor_from_ironic_node(self, mock_facade):
        mock_facade.get_server_hardware.return_value = (
            POOL_OF_SERVER_HARDWARE[0]
        )
        mock_facade.get_server_profile_template.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE[0]
        )
        mock_facade.get_server_hardware_type.return_value = (
            SERVER_HARDWARE_TYPE
        )
        mock_facade.get_enclosure_group.return_value = (
            ENCLOSURE_GROUP
        )
        node = POOL_OF_STUB_IRONIC_NODES[2]

        flavor_creator = create_flavor_cmd.FlavorCreator(mock_facade)
        result_flavor = flavor_creator.get_flavor_from_ironic_node(
            123, node
        )

        flavor = dict()
        flavor['ram_mb'] = node.properties.get("memory_mb")
        flavor['cpus'] = node.properties.get("cpus")
        flavor['disk'] = node.properties.get("local_gb")
        flavor['cpu_arch'] = node.properties.get("cpu_arch")
        flavor['server_hardware_type_uri'] = \
            '/rest/server-hardware/22222222-7777-8888-9999-AAAAAAAAAAA'
        flavor['server_hardware_type_name'] = 'TYPETYPETYPE'
        flavor['server_profile_template_uri'] = \
            '/rest/server-profile-templates/1111112222233333'
        flavor['server_profile_template_name'] = 'TEMPLATETEMPLATETEMPLATE'
        flavor['enclosure_group_name'] = 'ENCLGROUP'
        flavor['enclosure_group_uri'] = \
            '/rest/server-hardware/22222222-TTTT-BBBB-9999-AAAAAAAAAAA'

        self.assertEqual.__self__.maxDiff = None
        self.assertEqual(result_flavor,
                         flavor_objs.Flavor(id=12345, info=flavor))

    def test_get_server_hardware_id_from_node(self, mock_facade):
        ironic_node = POOL_OF_STUB_IRONIC_NODES[1]
        sh_id = common.get_server_hardware_id_from_node(ironic_node)

        self.assertEqual(sh_id, "22222")
