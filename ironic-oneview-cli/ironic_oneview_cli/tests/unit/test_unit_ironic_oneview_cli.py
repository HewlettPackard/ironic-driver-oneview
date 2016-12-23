# Copyright 2016 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Universidade Federal de Campina Grande
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

from ironic_oneview_cli.create_flavor_shell import (
    commands as create_flavor_cmd)
from ironic_oneview_cli.create_flavor_shell import (
    objects as flavor_objs)
from ironic_oneview_cli.create_node_shell import (
    commands as create_node_cmd)
from ironic_oneview_cli import facade
from ironic_oneview_cli.migrate_node_shell import (
    commands as migrate_node_cmd)
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
        driver='fake_oneview',
        driver_info={'user': 'foo',
                     'dynamic_allocation': True,
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
        driver='fake_oneview',
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
                     'dynamic_allocation': False,
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
    )
]

STUB_ENCLOSURE_GROUP = stubs.StubEnclosureGroup(
    name='ENCLGROUP',
    uuid='22222222-TTTT-BBBB-9999-AAAAAAAAAAA',
    uri='/rest/server-hardware/22222222-TTTT-BBBB-9999-AAAAAAAAAAA',
)

STUB_SERVER_HARDWARE_TYPE = stubs.StubServerHardwareType(
    name='TYPETYPETYPE',
    uuid='22222222-7777-8888-9999-AAAAAAAAAAA',
    uri='/rest/server-hardware/22222222-7777-8888-9999-AAAAAAAAAAA',
)

POOL_OF_STUB_SERVER_HARDWARE = [
    stubs.StubServerHardware(
        name='AAAAA',
        uuid='11111111-7777-8888-9999-000000000000',
        uri='/rest/server-hardware/11111',
        power_state='Off',
        server_profile_uri='1111-2222-3333',
        server_hardware_type_uri='/rest/server-hardware-types/111112222233333',
        enclosure_group_uri='/rest/enclosure-groups/1111112222233333',
        status='OK',
        state='Unknown',
        state_reason='',
        enclosure_uri='/rest/enclosures/1111112222233333',
        processor_count=12,
        processor_core_count=12,
        memory_mb=16384,
        port_map=[],
        mp_host_info={}
    ),
    stubs.StubServerHardware(
        name='AAAAA',
        uuid='22222222-7777-8888-9999-000000000000',
        uri='/rest/server-hardware/22222',
        power_state='Off',
        server_profile_uri='',
        server_hardware_type_uri='/rest/server-hardware-types/111111222233333',
        enclosure_group_uri='/rest/enclosure-groups/1111112222233333',
        status='OK',
        state='Unknown',
        state_reason='',
        enclosure_uri='/rest/enclosures/1111112222233333',
        processor_count=12,
        processor_core_count=12,
        memory_mb=16384,
        port_map=[],
        mp_host_info={}
    )
]

POOL_OF_STUB_SERVER_PROFILE_TEMPLATE = [
    stubs.StubServerProfileTemplate(
        uri='/rest/server-profile-templates/1111112222233333',
        name='TEMPLATETEMPLATETEMPLATE',
        server_hardware_type_uri='/rest/server-hardware-types/111112222233333',
        enclosure_group_uri='/rest/enclosure-groups/1111112222233333',
        connections=[],
        boot={}
    )
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
        node_creator = create_node_cmd.NodeCreator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        oneview_nodes = node_creator.get_oneview_nodes()

        self.assertEqual(4, len(ironic_nodes))
        self.assertEqual(3, len(list(oneview_nodes)))

    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_is_enrolled_on_ironic(self, mock_ironic_node_list, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        server_hardware = POOL_OF_STUB_SERVER_HARDWARE[1]

        self.assertTrue(node_creator.is_enrolled_on_ironic(server_hardware))

    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_is_enrolled_on_ironic_false(
        self, mock_ironic_node_list, mock_facade
    ):
        node_creator = create_node_cmd.NodeCreator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        server_hardware = POOL_OF_STUB_SERVER_HARDWARE[0]

        self.assertFalse(node_creator.is_enrolled_on_ironic(server_hardware))

    def test_is_server_profile_applied(self, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)

        self.assertTrue(node_creator.is_server_profile_applied(
            POOL_OF_STUB_SERVER_HARDWARE[0]))

    def test_is_server_profile_applied_false(self, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)

        self.assertFalse(node_creator.is_server_profile_applied(
            POOL_OF_STUB_SERVER_HARDWARE[1]))

    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_list_server_hardware(self, mock_ironic_node_list, mock_facade):
        node_creator = create_node_cmd.NodeCreator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list
        mock_facade.list_server_hardware_available.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )

        server_hardware_objects = node_creator.list_server_hardware()

        self.assertEqual(2, len(server_hardware_objects))

    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_list_pre_allocation_nodes(
        self, mock_facade, mock_ironic_node_list
    ):
        node_migrator = migrate_node_cmd.NodeMigrator(mock_facade)
        ironic_nodes = POOL_OF_STUB_IRONIC_NODES
        mock_ironic_node_list.return_value = ironic_nodes
        mock_facade.get_ironic_node_list = mock_ironic_node_list

        pre_allocation_nodes = node_migrator.list_pre_allocation_nodes()

        self.assertEqual(2, len(list(pre_allocation_nodes)))

    @mock.patch.object(facade.Facade, 'node_update')
    @mock.patch.object(facade.Facade, 'node_set_maintenance')
    @mock.patch.object(facade.Facade, 'delete_server_profile')
    def test_migrate_idle_node(
        self, mock_delete_server_profile, mock_set_maintenance,
        mock_node_update, mock_facade
    ):
        node_migrator = migrate_node_cmd.NodeMigrator(mock_facade)

        mock_facade.node_set_maintenance = mock_set_maintenance
        mock_facade.node_update = mock_node_update
        mock_facade.delete_server_profile = mock_delete_server_profile

        node = POOL_OF_STUB_IRONIC_NODES[0]
        node.server_profile_uri = \
            POOL_OF_STUB_SERVER_HARDWARE[0].server_profile_uri
        patch_test = [{'op': 'add',
                       'path': '/driver_info/dynamic_allocation',
                       'value': True}]

        node_migrator.migrate_idle_node(node)

        mock_delete_server_profile.assert_called_with(
            node.server_profile_uri
        )
        mock_node_update.assert_called_with(
            node.uuid, patch_test
        )
        self.assertEqual(2, mock_set_maintenance.call_count)

    @mock.patch.object(facade.Facade, 'node_update')
    def test_migrate_node_with_instance(self, mock_node_update, mock_facade):
        node_migrator = migrate_node_cmd.NodeMigrator(mock_facade)
        mock_facade.node_update = mock_node_update

        node = POOL_OF_STUB_IRONIC_NODES[1]
        node.server_profile_uri = \
            POOL_OF_STUB_SERVER_HARDWARE[0].server_profile_uri

        patch_test_dynamic = [{'op': 'add',
                               'path': '/driver_info/dynamic_allocation',
                               'value': True}]
        patch_test_sp_applied = [{'op': 'add',
                                  'path': '/driver_info/'
                                          'applied_server_profile_uri',
                                  'value':
                                          '1111-2222-3333'}]

        node_migrator.migrate_node_with_instance(node)

        mock_node_update.assert_called_with(
            node.uuid, patch_test_sp_applied + patch_test_dynamic
        )

    def test_get_flavor_from_ironic_node(self, mock_facade):
        mock_facade.get_server_hardware.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE[0]
        )
        mock_facade.get_server_profile_template.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[0]
        )
        mock_facade.get_server_hardware_type.return_value = (
            STUB_SERVER_HARDWARE_TYPE
        )
        mock_facade.get_enclosure_group.return_value = (
            STUB_ENCLOSURE_GROUP
        )
        node = POOL_OF_STUB_IRONIC_NODES[2]

        flavor_creator = create_flavor_cmd.FlavorCreator(mock_facade)
        result_flavor = flavor_creator.get_flavor_from_ironic_node(
            12345, node
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


if __name__ == '__main__':
    unittest.main()
