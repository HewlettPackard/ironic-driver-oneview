# Copyright (2015-2017) Hewlett Packard Enterprise Development LP
# Copyright (2015-2017) Universidade Federal de Campina Grande
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
from ironic_oneview_cli.create_port_shell import (
    commands as port_create_cmd)
from ironic_oneview_cli.delete_node_shell import (
    commands as delete_node_cmd)
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
                     'password': 'bar'},
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
                     'password': 'bar'},
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
        name='fake-node-5',
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
                     'password': 'bar'},
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
        name='fake-node-6',
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
                     'password': 'bar'},
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
        name='fake-node-7',
        extra={}
    ),
    stubs.StubIronicNode(
        id=8,
        uuid='44444444-5555-6666-7777-88888888888',
        chassis_uuid='aaaaaaaa-1111-bbbb-2222-cccccccccccc',
        maintenance=False,
        maintenance_reason='',
        provision_state='enroll',
        ports=[],
        driver='fake_oneview',
        driver_info={'server_hardware_uri': "/rest/server-hardware/22222",
                     "use_oneview_ml2_driver": True,
                     'user': 'foo',
                     'password': 'bar'},
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
        name='fake-node-8',
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
        'portMap': {
            'deviceSlots': [{
                'physicalPorts': [{
                    'type': 'Ethernet',
                    'virtualPorts': [{
                        'portFunction': 'a',
                        'mac': 'aa:bb:cc:dd:ee:ff'
                    }]
                }]
            }]
        },
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
    os_driver='fake_oneview',
    os_power_interface='fake_oneview',
    os_management_interface='fake_oneview',
    os_inspect_interface='fake_oneview',
    os_deploy_interface='fake_oneview',
    os_ironic_deploy_kernel_uuid='11111-22222-33333-44444-55555',
    os_ironic_deploy_ramdisk_uuid='55555-44444-33333-22222-11111'
)


@mock.patch('ironic_oneview_cli.openstack_client.get_ironic_client')
@mock.patch('ironic_oneview_cli.common.hpclient.OneViewClient')
class FunctionalTestIronicOneviewCli(unittest.TestCase):

    def setUp(self):
        self.args = argparse.Namespace(
            ov_auth_url='https://my-oneview',
            ov_username='ov-user',
            ov_password='secret',
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
            os_driver=STUB_PARAMETERS.os_driver,
            os_power_interface=STUB_PARAMETERS.os_power_interface,
            os_management_interface=STUB_PARAMETERS.os_management_interface,
            os_inspect_interface=STUB_PARAMETERS.os_inspect_interface,
            os_deploy_interface=STUB_PARAMETERS.os_deploy_interface,
            os_ironic_deploy_kernel_uuid=(
                STUB_PARAMETERS.os_ironic_deploy_kernel_uuid
            ),
            os_ironic_deploy_ramdisk_uuid=(
                STUB_PARAMETERS.os_ironic_deploy_ramdisk_uuid
            ),

            all=False,
            server_profile_template_name=None,
            use_oneview_ml2_driver=False,
            classic=False,
            number=None,
            nodes=None,
            mac=None
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_no_args(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]
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
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['network_interface'] = 'neutron'

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_with_classic_flag(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        self.args.classic = True

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['driver'] = STUB_PARAMETERS.os_ironic_node_driver

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.common.input')
    def test_node_creation_rack_servers(
        self, mock_input, mock_oneview_client, mock_ironic_client
    ):
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
        )
        spt_index = 0
        sh_index = 3
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['properties']['capabilities'] = (
            'server_hardware_type_uri:%s,'
            'server_profile_template_uri:%s' % (
                selected_sh.get("serverHardwareTypeUri"),
                selected_spt.get('uri')
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
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
        )
        spt_index = 0
        sh_index = 0
        mock_input.side_effect = [
            str(spt_index + 1),
            str(sh_index + 1)
        ]

        create_node_cmd.do_node_create(self.args)

        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]
        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        attrs['properties'] = {
            'capabilities': 'server_hardware_type_uri:%s,'
                            'server_profile_template_uri:%s,'
                            'enclosure_group_uri:%s' % (
                                selected_sh.get("serverHardwareTypeUri"),
                                selected_spt.get("uri"),
                                selected_sh.get("serverGroupUri")
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
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
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
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
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

        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]

        attrs = self._create_attrs_for_node(selected_sh, selected_spt)

        ironic_client = mock_ironic_client.return_value
        ironic_client.node.create.assert_called_with(
            **attrs
        )

    def test_node_creation_spt_and_number_arguments(
        self, mock_oneview_client, mock_ironic_client
    ):
        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get_all.return_value = (
            POOL_OF_SERVER_HARDWARE
        )
        oneview_client.server_profile_templates.get_all.return_value = (
            POOL_OF_SERVER_PROFILE_TEMPLATE
        )
        oneview_client.server_hardware.get.return_value = (
            POOL_OF_SERVER_HARDWARE[1]
        )

        self.args.server_profile_template_name = (
            'TEMPLATETEMPLATETEMPLATE'
        )
        self.args.number = 3

        create_node_cmd.do_node_create(self.args)

        sh_index = 0
        spt_index = 0
        selected_sh = POOL_OF_SERVER_HARDWARE[sh_index]
        selected_spt = POOL_OF_SERVER_PROFILE_TEMPLATE[spt_index]

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
    def test_delete_node(self, mock_input,
                         mock_oneview_client, mock_ironic_client):
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.list.return_value = POOL_OF_STUB_IRONIC_NODES

        self.args.all = True
        mock_input.side_effect = ['y']

        delete_node_cmd.do_node_delete(self.args)

        self.assertEqual(8, ironic_client.node.delete.call_count)

    def test_port_creation_no_args(
        self, mock_oneview_client, mock_ironic_client
    ):
        server_hardware = POOL_OF_SERVER_HARDWARE[1]
        ironic_node = POOL_OF_STUB_IRONIC_NODES[3]

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = server_hardware
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = ironic_node

        self.args.node = ironic_node.uuid
        port_create_cmd.do_port_create(self.args)

        attrs = self._create_attrs_for_port(server_hardware, ironic_node)
        ironic_client.port.create.assert_called_with(
            **attrs
        )

    def test_port_creation_with_mac(
        self, mock_oneview_client, mock_ironic_client
    ):
        server_hardware = POOL_OF_SERVER_HARDWARE[1]
        ironic_node = POOL_OF_STUB_IRONIC_NODES[3]

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = server_hardware
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = ironic_node

        self.args.node = ironic_node.uuid
        self.args.mac = "01:23:45:67:89:ab"
        port_create_cmd.do_port_create(self.args)

        attrs = self._create_attrs_for_port(server_hardware, ironic_node,
                                            self.args.mac)
        ironic_client.port.create.assert_called_with(
            **attrs
        )

    def test_port_creation_with_oneview_ml2_driver(
        self, mock_oneview_client, mock_ironic_client
    ):
        server_hardware = POOL_OF_SERVER_HARDWARE[1]
        ironic_node = POOL_OF_STUB_IRONIC_NODES[7]

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = server_hardware
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = ironic_node

        self.args.node = ironic_node.uuid
        port_create_cmd.do_port_create(self.args)

        attrs = self._create_attrs_for_port(server_hardware, ironic_node)
        ironic_client.port.create.assert_called_with(
            **attrs
        )

    @mock.patch('ironic_oneview_cli.facade.Facade.'
                'get_server_hardware_mac_from_ilo')
    def test_port_creation_rack_server(
        self, mock_mac_from_ilo, mock_oneview_client, mock_ironic_client
    ):
        server_hardware = POOL_OF_SERVER_HARDWARE[0]
        ironic_node = POOL_OF_STUB_IRONIC_NODES[6]
        mac = "aa:bb:cc:dd:ee:ff"

        oneview_client = mock_oneview_client.return_value
        oneview_client.server_hardware.get.return_value = server_hardware
        ironic_client = mock_ironic_client.return_value
        ironic_client.node.get.return_value = ironic_node
        mock_mac_from_ilo.return_value = mac

        self.args.node = ironic_node.uuid
        port_create_cmd.do_port_create(self.args)

        attrs = self._create_attrs_for_port(server_hardware, ironic_node, mac)
        ironic_client.port.create.assert_called_with(
            **attrs
        )

    def _create_attrs_for_port(self, server_hardware, ironic_node, mac=None):
        if not mac:
            device_slot = server_hardware.get("portMap").get("deviceSlots")[0]
            physical_port = device_slot.get("physicalPorts")[0]
            mac = physical_port.get("virtualPorts")[0].get("mac")

        local_link_connection = {}
        if ironic_node.driver_info.get('use_oneview_ml2_driver'):
            server_hardware_uri = ironic_node.driver_info.get(
                "server_hardware_uri")
            server_hardware_id = server_hardware_uri.split("/")[-1]
            switch_info = (
                '{"server_hardware_id": "%(server_hardware_id)s", '
                '"bootable": "%(bootable)s"}') % {
                    'server_hardware_id': server_hardware_id,
                    'bootable': True}
            local_link_connection = {
                "switch_id": "01:23:45:67:89:ab",
                "port_id": "",
                "switch_info": switch_info
            }

        attrs = {
            'address': mac,
            'node_uuid': ironic_node.uuid,
            'portgroup_uuid': None,
            "local_link_connection": local_link_connection,
            'pxe_enabled': True
        }

        return attrs

    def _create_attrs_for_node(self, server_hardware, server_profile_template):
        cpus = (server_hardware.get("processorCount") *
                server_hardware.get("processorCoreCount"))
        attrs = {
            'driver_info': {
                'use_oneview_ml2_driver': self.args.use_oneview_ml2_driver,
                'deploy_kernel': STUB_PARAMETERS.os_ironic_deploy_kernel_uuid,
                'deploy_ramdisk':
                    STUB_PARAMETERS.os_ironic_deploy_ramdisk_uuid,
                'server_hardware_uri':
                    server_hardware.get("uri"),
            },
            'properties': {
                'cpus': cpus,
                'memory_mb': server_hardware.get("memoryMb"),
                'local_gb': server_hardware.get("local_gb"),
                'cpu_arch': server_hardware.get("cpu_arch"),
                'capabilities':
                    'server_hardware_type_uri:%s,'
                    'server_profile_template_uri:%s,'
                    'enclosure_group_uri:%s' % (
                        server_hardware.get("serverHardwareTypeUri"),
                        server_profile_template.get("uri"),
                        server_hardware.get("serverGroupUri")
                    )
            }
        }
        if self.args.classic:
            attrs['driver'] = STUB_PARAMETERS.os_ironic_node_driver
        else:
            attrs['driver'] = STUB_PARAMETERS.os_driver
            attrs['power_interface'] = STUB_PARAMETERS.os_power_interface
            attrs['management_interface'] = (
                STUB_PARAMETERS.os_management_interface
            )
            attrs['inspect_interface'] = STUB_PARAMETERS.os_inspect_interface
            attrs['deploy_interface'] = STUB_PARAMETERS.os_deploy_interface

        return attrs
