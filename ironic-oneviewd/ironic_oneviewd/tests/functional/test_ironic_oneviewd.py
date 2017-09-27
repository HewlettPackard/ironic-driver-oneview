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

import copy
import mock
import unittest

from ironic_oneviewd import facade
from ironic_oneviewd.node_manager import manage
from ironic_oneviewd.node_manager.manage import NodeManager


class FakeIronicNode(object):
    def __init__(self, id, uuid, chassis_uuid, provision_state, driver,
                 ports, driver_info={}, driver_internal_info={},
                 name='fake-node', maintenance='False', properties={},
                 extra={}):

        self.id = id
        self.uuid = uuid
        self.chassis_uuid = chassis_uuid
        self.provision_state = provision_state
        self.driver = driver
        self.ports = ports
        self.driver_info = driver_info
        self.driver_internal_info = driver_internal_info
        self.maintenance = maintenance
        self.properties = properties
        self.extra = extra
        self.name = name


class FakeIronicPort(object):
    def __init__(self, id, uuid, node_uuid, address, extra={},
                 local_link_connection='', portgroup_id='',
                 pxe_enabled='False'):

        self.id = id
        self.uuid = uuid
        self.node_uuid = node_uuid
        self.address = address
        self.extra = extra
        self.local_link_connection = local_link_connection
        self.portgroup_id = portgroup_id
        self.pxe_enabled = pxe_enabled


class FakeServerHardware(object):
    def __init__(self, name, uuid, uri, power_state, port_map,
                 server_profile_uri, server_hardware_type_uri,
                 enclosure_group_uri, state, enclosure_uri):

        self.name = name
        self.uuid = uuid
        self.uri = uri
        self.power_state = power_state
        self.port_map = port_map
        self.server_profile_uri = server_profile_uri
        self.server_hardware_type_uri = server_hardware_type_uri
        self.enclosure_group_uri = enclosure_group_uri
        self.state = state
        self.enclosure_uri = enclosure_uri


class FakeServerProfile(object):
    attribute_map = {
        'uri': 'uri',
        'name': 'name',
        'connections': 'connections',
    }


class FakeConfHelper(object):
    def __init__(self, max_workers):
        self.rpc_thread_pool_size = max_workers


class FakeConfClient(object):
    def __init__(self, max_workers):
        self.DEFAULT = FakeConfHelper(max_workers)


POOL_OF_FAKE_IRONIC_NODES = [
    FakeIronicNode(
        id=123,
        uuid='66666666-7777-8888-9999-000000000000',
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
        driver_info={'use_oneview_ml2_driver': True, 'user': 'foo',
                     'password': 'bar',
                     'server_hardware_uri':
                     '/rest/server-hardware-types/111112222233333'},
        properties={'num_cpu': 4},
        name='fake-node-1',
        extra={}
    ),
    FakeIronicNode(
        id=123,
        uuid='66666666-7777-8888-9999-000000000000',
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
        driver_info={
            'user': 'foo', 'password': 'bar'
        },
        properties={'num_cpu': 4},
        name='fake-node-2',
        extra={}
    ),
    FakeIronicNode(
        id=123,
        uuid='66666666-7777-8888-9999-000000000000',
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
        driver_info={'use_oneview_ml2_driver': False, 'user': 'foo',
                     'password': 'bar',
                     'server_hardware_uri':
                     '/rest/server-hardware-types/111112222233333'},
        properties={'num_cpu': 4},
        name='fake-node-3',
        extra={}
    ),
]

POOL_OF_FAKE_IRONIC_PORTS = [
    FakeIronicPort(
        id=987,
        uuid='11111111-2222-3333-4444-555555555555',
        local_link_connection=None,
        node_uuid='66666666-7777-8888-9999-000000000000',
        address='AA:BB:CC:DD:EE:FF',
        extra={}
    )
]

POOL_OF_FAKE_SERVER_HARDWARE = [
    FakeServerHardware(
        name='AAAAA',
        uuid='11111111-7777-8888-9999-000000000000',
        uri='/rest/server-hardware/11111',
        port_map={'deviceSlots': ''},
        power_state='Off',
        server_profile_uri='',
        server_hardware_type_uri='/rest/server-hardware-types/111112222233333',
        enclosure_group_uri='/rest/enclosure-groups/1111112222233333',
        state='Unknown',
        enclosure_uri='/rest/enclosures/1111112222233333',
    )
]


class TestIronicOneviewd(unittest.TestCase):
    @mock.patch('ironic_oneviewd.facade.Facade', autospec=True)
    @mock.patch.object(facade.Facade, 'get_ironic_node_list')
    def test_take_node_actions(self, mock_get_ironic_node_list, mock_facade):

        mocked_facade = facade.Facade()
        mock_get_ironic_node_list.return_value = POOL_OF_FAKE_IRONIC_NODES
        mocked_facade.get_ironic_node_list = mock_get_ironic_node_list
        mock_facade.return_value = mocked_facade
        node_manager = NodeManager()
        node_manager.pull_ironic_nodes()
        mock_get_ironic_node_list.assert_called_with()

    @mock.patch('ironic_oneviewd.facade.Facade', autospec=True)
    @mock.patch.object(manage.NodeManager, 'take_enroll_state_actions')
    def test_manage_node_provision_state_with_node_in_enroll(
        self, mock_take_enroll_state_actions, mock_facade
    ):
        fake_node = copy.deepcopy(POOL_OF_FAKE_IRONIC_NODES[0])
        fake_node.provision_state = 'enroll'
        node_manager = NodeManager()
        node_manager.manage_node_provision_state(fake_node)
        mock_take_enroll_state_actions.assert_called_with(fake_node)

    @mock.patch('ironic_oneviewd.facade.Facade', autospec=True)
    @mock.patch.object(manage.NodeManager, 'take_manageable_state_actions')
    def test_manage_node_provision_state_with_node_in_manageable(
        self, mock_take_manageable_state_actions, mock_facade
    ):
        fake_node = copy.deepcopy(POOL_OF_FAKE_IRONIC_NODES[0])
        fake_node.provision_state = 'manageable'
        node_manager = NodeManager()
        node_manager.manage_node_provision_state(fake_node)
        mock_take_manageable_state_actions.assert_called_with(fake_node)

    @mock.patch('ironic_oneviewd.conf.CONF.openstack.inspection_enabled')
    @mock.patch('ironic_oneviewd.facade.Facade', new_callable=mock.MagicMock)
    def test_manage_provision_state_inspection_enabled(
        self, mock_facade, mock_inspection_enabled
    ):
        mock_facade = facade.Facade()
        mock_facade.set_node_provision_state = mock.MagicMock()
        mock_inspection_enabled.return_value = True
        fake_node = copy.deepcopy(POOL_OF_FAKE_IRONIC_NODES[1])
        fake_node.provision_state = 'manageable'
        node_manager = NodeManager()
        node_manager.manage_node_provision_state(fake_node)
        mock_facade.set_node_provision_state.assert_called_with(fake_node,
                                                                'inspect')

    @mock.patch('ironic_oneviewd.facade.Facade', new_callable=mock.MagicMock)
    def test_manage_node_provision_state_with_node_in_inspect_failed(
        self, mock_facade
    ):
        mock_facade = facade.Facade()
        mock_facade.set_node_provision_state = mock.MagicMock()
        fake_node = copy.deepcopy(POOL_OF_FAKE_IRONIC_NODES[1])
        fake_node.provision_state = 'inspect failed'
        fake_node.last_error = ("OneView exception occurred. Error: Node %s is"
                                " already in use by OneView.") % fake_node.id
        node_manager = NodeManager()
        node_manager.manage_node_provision_state(fake_node)
        mock_facade.set_node_provision_state.assert_called_with(fake_node,
                                                                'manage')

    @mock.patch('ironic_oneviewd.facade.Facade.set_node_provision_state',
                autospec=True)
    @mock.patch('ironic_oneviewd.facade.Facade', new_callable=mock.MagicMock)
    def test_all_enroll_actions(self, mock_facade,
                                mock_facade_set_node_provision_state):
        node_manager = NodeManager()

        fake_node = copy.deepcopy(POOL_OF_FAKE_IRONIC_NODES[1])
        fake_node.provision_state = 'enroll'

        node_manager.manage_node_provision_state(fake_node)
        mock_facade_set_node_provision_state.assert_called_with(fake_node,
                                                                'manage')
