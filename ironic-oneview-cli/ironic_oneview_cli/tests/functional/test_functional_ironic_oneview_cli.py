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

import argparse
import mock
import unittest

from ironic_oneview_cli.create_flavor_shell import (
    commands as create_flavor_cmd)
from ironic_oneview_cli.create_node_shell import (
    commands as create_node_cmd)
from ironic_oneview_cli.delete_node_shell import (
    commands as delete_node_cmd)
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
                     'password': 'bar',
                     'dynamic_allocation': True},
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
        name='fake-node-2',
        extra={}
    ),
    stubs.StubIronicNode(
        id=3,
        uuid='33333333-4444-8888-9999-000000000000',
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
                     'password': 'bar',
                     'dynamic_allocation': False},
        properties={'memory_mb': 32768,
                    'cpu_arch': 'x86_64',
                    'local_gb': 120,
                    'cpus': 8,
                    'capabilities':
                        "server_hardware_type_uri:"
                        "/rest/server-hardware-types/1111112222233333,"
                        "enclosure_group_uri:"
                        "/rest/enclosure-groups/1111112222233333,"
                        "server_profile_template_uri:"
                        "/rest/server-profile-templates/1111112222233333"
                    },
        instance_uuid='1111-2222-3333-4444-5555',
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
        uuid='33333333-4444-8888-9999-11111111111',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        maintenance_reason='Migrating to dynamic allocation',
        provision_state='enroll',
        ports=[
            {'id': 345,
             'uuid': '11111111-2222-3333-4444-555555555555',
             'node_uuid': '66666666-7777-8888-9999-000000000000',
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}
        ],
        driver='fake_oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/22222",
                     'user': 'foo',
                     'password': 'bar',
                     'dynamic_allocation': True},
        properties={'memory_mb': 32768,
                    'cpu_arch': 'x86_64',
                    'local_gb': 120,
                    'cpus': 8,
                    'capabilities':
                        "server_hardware_type_uri:"
                        "/rest/server-hardware-types/1111112222233333,"
                        "enclosure_group_uri:"
                        "/rest/enclosure-groups/1111112222233333,"
                        "server_profile_template_uri:"
                        "/rest/server-profile-templates/1111112222233333"
                    },
        instance_uuid='1111-2222-3333-4444-5555',
        name='fake-node-3',
        extra={}
    ),
    stubs.StubIronicNode(
        id=6,
        uuid='33333333-4444-8888-9999-22222222222',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        maintenance_reason='',
        provision_state='enroll',
        ports=[
            {'id': 345,
             'uuid': '11111111-2222-3333-4444-555555555555',
             'node_uuid': '66666666-7777-8888-9999-000000000000',
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}
        ],
        driver='fake_oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/22222",
                     'user': 'foo',
                     'password': 'bar',
                     'dynamic_allocation': True},
        properties={'memory_mb': 32768,
                    'cpu_arch': 'x86_64',
                    'local_gb': 120,
                    'cpus': 8,
                    'capabilities':
                        "server_hardware_type_uri:"
                        "/rest/server-hardware-types/1111112222233333,"
                        "enclosure_group_uri:"
                        "/rest/enclosure-groups/1111112222233333,"
                        "server_profile_template_uri:"
                        "/rest/server-profile-templates/1111112222233333"
                    },
        instance_uuid='1111-2222-3333-4444-5555',
        name='fake-node-3',
        extra={}
    ),
    stubs.StubIronicNode(
        id=7,
        uuid='33333333-4444-8888-9999-22222222222',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        maintenance_reason='',
        provision_state='enroll',
        ports=[
            {'id': 345,
             'uuid': '11111111-2222-3333-4444-555555555555',
             'node_uuid': '66666666-7777-8888-9999-000000000000',
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}
        ],
        driver='fake_oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/11111",
                     'user': 'foo',
                     'password': 'bar',
                     'dynamic_allocation': False},
        properties={'memory_mb': 32768,
                    'cpu_arch': 'x86_64',
                    'local_gb': 120,
                    'cpus': 8,
                    'capabilities':
                        "server_hardware_type_uri:"
                        "/rest/server-hardware-types/1111112222233333,"
                        "enclosure_group_uri:"
                        "/rest/enclosure-groups/1111112222233333,"
                        "server_profile_template_uri:"
                        "/rest/server-profile-templates/1111112222233333"
                    },
        name='fake-node-3',
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
        server_profile_uri='',
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
        name='BBBBB',
        uuid='22222222-7777-8888-9999-000000000000',
        uri='/rest/server-hardware/22222',
        power_state='Off',
        server_profile_uri='/rest/server-profile/1111-2222',
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
    ),
    stubs.StubServerHardware(
        name='CCCCC',
        uuid='33333333-7777-8888-9999-000000000000',
        uri='/rest/server-hardware/33333',
        power_state='Off',
        server_profile_uri='',
        server_hardware_type_uri='/rest/server-hardware-types/111111222223333',
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
        name='RackServer',
        uuid='33333333-7777-8888-9999-111111',
        uri='/rest/server-hardware/44444',
        power_state='Off',
        server_profile_uri='',
        server_hardware_type_uri='/rest/server-hardware-types/111111222223333',
        enclosure_group_uri=None,
        status='OK',
        state='Unknown',
        state_reason='',
        enclosure_uri=None,
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
        memory_mb=1024,
        ram_mb=1024,
        vcpus=1,
        cpus=1,
        cpu_arch='x64',
        disk=100,
        root_gb=100,
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


STUB_PARAMETERS = stubs.StubParameters(
    os_ironic_node_driver='fake_oneview',
    os_ironic_deploy_kernel_uuid='11111-22222-33333-44444-55555',
    os_ironic_deploy_ramdisk_uuid='55555-44444-33333-22222-11111'
)


@mock.patch('ironic_oneview_cli.openstack_client.get_ironic_client')
@mock.patch('ironic_oneview_cli.common.client.ClientV2')
class FunctionalTestIronicOneviewCli(unittest.TestCase):

    def setUp(self):
        self.args = argparse.Namespace(
            ov_auth_url='https://my-oneview',
            ov_username='ov-user',
            ov_password='secret',
            ov_cacert='',
            ov_max_polling_attempts=12,
            ov_audit=False,
            ov_audit_input='',
            ov_audit_output='',
            os_auth_url='http://something',
            os_username='my_name',
            os_password='secret',
            os_project_id='my_tenant_id',
            os_project_name='my_tenant',
            os_user_domain_id='default',
            os_user_domain_name='Default',
            os_project_domain_id='default',
            os_project_domain_name='Default',
            os_tenant_name='my_tenant',
            insecure=True,
            os_cacert='',
            os_cert='',
            os_inspection_enabled=False,
            os_ironic_node_driver=STUB_PARAMETERS.os_ironic_node_driver,
            os_ironic_deploy_kernel_uuid=(
                STUB_PARAMETERS.os_ironic_deploy_kernel_uuid
            ),
            os_ironic_deploy_ramdisk_uuid=(
                STUB_PARAMETERS.os_ironic_deploy_ramdisk_uuid
            ),
            all=False,
            server_profile_template_name=None,
            use_oneview_ml2_driver=False,
            number=None,
            nodes=None
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_no_args(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_STUB_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_with_oneview_ml2_driver(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        self.args.use_oneview_ml2_driver = True

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_STUB_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['network_interface'] = 'neutron'

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_rack_servers(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )
        spt_index = 0
        sh_index = 3
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_STUB_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['properties']['capabilities'] = (
            'server_hardware_type_uri:%s,'
            'server_profile_template_uri:%s' % (
                selected_sh.server_hardware_type_uri,
                selected_spt.uri
            )
        )

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_inspection_enabled(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        self.args.os_inspection_enabled = True

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_STUB_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['properties'] = {
            'capabilities': 'server_hardware_type_uri:%s,'
                            'server_profile_template_uri:%s,'
                            'enclosure_group_uri:%s' % (
                                selected_sh.server_hardware_type_uri,
                                selected_spt.uri,
                                selected_sh.enclosure_group_uri
                            )
        }

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_number_argument(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        self.args.number = 2

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )

        spt_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
        ]

        create_node_cmd.do_node_create(self.args)

        ironic_client = mock_ironic_client.return_value
        self.assertEqual(
            self.args.number, ironic_client.node.create.call_count
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_spt_argument(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )

        self.args.server_profile_template_name = (
            'TEMPLATETEMPLATETEMPLATE'
        )

        sh_index = 0
        spt_index = 0
        mock_input.side_effect = [
            str(sh_index + 1),
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_STUB_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[spt_index]

        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    def test_node_creation_spt_and_number_arguments(
        self, mock_oneview_client, mock_ironic_client
    ):
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.list.return_value = (
            POOL_OF_STUB_SERVER_HARDWARE
        )
        oneview_client.server_profile_template.list.return_value = (
            POOL_OF_STUB_SERVER_PROFILE_TEMPLATE
        )

        self.args.server_profile_template_name = (
            'TEMPLATETEMPLATETEMPLATE'
        )
        self.args.number = 3

        create_node_cmd.do_node_create(self.args)

        sh_index = 0
        spt_index = 0
        selected_sh = POOL_OF_STUB_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_STUB_SERVER_PROFILE_TEMPLATE[spt_index]

        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_any_call(
            **attrs
        )
        self.assertEqual(
            self.args.number, ironic_client.node.create.call_count
        )

    @mock.patch('ironic_oneview_cli.common.input')
    @mock.patch('ironic_oneview_cli.openstack_client.get_nova_client')
    def test_flavor_creation(self, mock_nova_client, mock_input,
                             mock_oneview_client, mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.list.return_value = (
            POOL_OF_STUB_IRONIC_NODES
        )

        # Nodes 0 and 1 doesn't have the required attributes, will not be shown
        node_selected = POOL_OF_STUB_IRONIC_NODES[2]
        flavor_name = 'my-flavor'
        mock_input.side_effect = ['1', flavor_name, 'n']
        create_flavor_cmd.do_flavor_create(self.args)

        attrs = {
            'name': flavor_name,
            'ram': node_selected.properties.get('memory_mb'),
            'vcpus': node_selected.properties.get('cpus'),
            'disk': node_selected.properties.get('local_gb')
        }

        nova_client = mock_nova_client.return_value
        nova_client.flavors.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_migration(self, mock_input,
                            mock_oneview_client,
                            mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.list.return_value = (
            POOL_OF_STUB_IRONIC_NODES[1],
            POOL_OF_STUB_IRONIC_NODES[2]
        )
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = \
            POOL_OF_STUB_SERVER_HARDWARE[1]

        mock_input.side_effect = ['1', 'n']

        update_patch_test = [{'op': 'add',
                              'path': '/driver_info/dynamic_allocation',
                              'value': True}]

        migrate_node_cmd.do_migrate_to_dynamic(self.args)

        self.assertEqual(2, ironic_client.node.set_maintenance.call_count)

        ironic_client.node.update.assert_called_with(
            POOL_OF_STUB_IRONIC_NODES[1].uuid,
            update_patch_test
        )

    def test_node_migration_all(self, mock_oneview_client, mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.list.return_value = (
            POOL_OF_STUB_IRONIC_NODES[1],
            POOL_OF_STUB_IRONIC_NODES[2]
        )
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = \
            POOL_OF_STUB_SERVER_HARDWARE[1]

        update_patch_test = [{'op': 'add',
                              'path': '/driver_info/dynamic_allocation',
                              'value': True}]

        sp_patch_test = [{'op': 'add',
                          'path': '/driver_info/'
                                  'applied_server_profile_uri',
                          'value': '/rest/server-profile/1111-2222'}]
        self.args.all = True

        migrate_node_cmd.do_migrate_to_dynamic(self.args)

        self.assertEqual(2, ironic_client.node.set_maintenance.call_count)

        oneview_client.server_profile.delete.assert_called_with(
            '1111-2222'
        )

        ironic_client.node.update.assert_any_call(
            POOL_OF_STUB_IRONIC_NODES[1].uuid,
            update_patch_test
        )

        ironic_client.node.update.assert_any_call(
            POOL_OF_STUB_IRONIC_NODES[2].uuid,
            sp_patch_test + update_patch_test
        )

    def test_node_migration_specific(self,
                                     mock_oneview_client,
                                     mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = (
            POOL_OF_STUB_IRONIC_NODES[2]
        )
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = \
            POOL_OF_STUB_SERVER_HARDWARE[1]

        update_patch_test = [{'op': 'add',
                              'path': '/driver_info/dynamic_allocation',
                              'value': True}]

        sp_patch_test = [{'op': 'add',
                          'path': '/driver_info/'
                                  'applied_server_profile_uri',
                          'value': '/rest/server-profile/1111-2222'}]

        self.args.nodes = '33333333-4444-8888-9999-000000000000'

        migrate_node_cmd.do_migrate_to_dynamic(self.args)

        ironic_client.node.set_maintenance.assert_not_called()

        ironic_client.node.update.assert_called_with(
            POOL_OF_STUB_IRONIC_NODES[2].uuid,
            sp_patch_test + update_patch_test
        )

    def test_migration_dyalloc_and_maintenance_reason_not_none(
            self,
            mock_oneview_client,
            mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = (
            POOL_OF_STUB_IRONIC_NODES[4]
        )

        self.args.nodes = '33333333-4444-8888-9999-11111111111'

        migrate_node_cmd.do_migrate_to_dynamic(self.args)

        ironic_client.node.update.assert_not_called()

        ironic_client.node.set_maintenance.assert_called_with(
            POOL_OF_STUB_IRONIC_NODES[4].uuid,
            False,
            maint_reason=''
        )

    def test_migration_dyalloc_and_maintenance_reason_none(
            self,
            mock_oneview_client,
            mock_ironic_client):

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = (
            POOL_OF_STUB_IRONIC_NODES[5]
        )

        self.args.nodes = '33333333-4444-8888-9999-22222222222'

        migrate_node_cmd.do_migrate_to_dynamic(self.args)

        ironic_client.node.update.assert_not_called()

        ironic_client.node.set_maintenance.assert_not_called()

    def test_migrate_with_server_profile_deleted(
            self,
            mock_oneview_client,
            mock_ironic_client):

        node = POOL_OF_STUB_IRONIC_NODES[6]
        server_profile_uri = '/rest/server-profile/1111-2222'
        node.server_profile_uri = server_profile_uri
        POOL_OF_STUB_IRONIC_NODES[6] = node

        update_patch_test = [{'op': 'add',
                              'path': '/driver_info/dynamic_allocation',
                              'value': True}]

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = (
            POOL_OF_STUB_IRONIC_NODES[6]
        )
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = \
            POOL_OF_STUB_SERVER_HARDWARE[0]

        self.args.nodes = '33333333-4444-8888-9999-22222222222'

        migrate_node_cmd.do_migrate_to_dynamic(self.args)

        oneview_client.server_profile.delete.assert_called_with(
            None
        )

        self.assertRaises(ValueError)

        ironic_client.node.update.assert_called_with(
            POOL_OF_STUB_IRONIC_NODES[6].uuid,
            update_patch_test
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_delete_node(self, mock_input,
                         mock_oneview_client, mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.list.return_value = POOL_OF_STUB_IRONIC_NODES

        self.args.all = True
        mock_input.side_effect = ['y']

        delete_node_cmd.do_node_delete(self.args)

        self.assertEqual(7, ironic_client.node.delete.call_count)

    def _create_attrs_for_node(self, server_hardware, server_profile_template):
        attrs = {
            'driver': STUB_PARAMETERS.os_ironic_node_driver,
            'driver_info': {
                'dynamic_allocation': True,
                'use_oneview_ml2_driver': self.args.use_oneview_ml2_driver,
                'deploy_kernel': STUB_PARAMETERS.os_ironic_deploy_kernel_uuid,
                'deploy_ramdisk':
                    STUB_PARAMETERS.os_ironic_deploy_ramdisk_uuid,
                'server_hardware_uri':
                    server_hardware.uri,
            },
            'properties': {
                'cpus': server_hardware.cpus,
                'memory_mb': server_hardware.memory_mb,
                'local_gb': server_hardware.local_gb,
                'cpu_arch': server_hardware.cpu_arch,
                'capabilities':
                    'server_hardware_type_uri:%s,'
                    'server_profile_template_uri:%s,'
                    'enclosure_group_uri:%s' % (
                        server_hardware.server_hardware_type_uri,
                        server_profile_template.uri,
                        server_hardware.enclosure_group_uri
                    )
            }
        }

        return attrs
