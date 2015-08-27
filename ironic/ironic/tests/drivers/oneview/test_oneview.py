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

import mock

from ironic.common import states
from ironic.drivers.modules.oneview import driver_oneview_exceptions
from ironic.drivers.modules.oneview import oneview_client
from ironic.tests.db import base as db_base


# TODO(any): move this variable to db_utils.get_test_oneview_properties()
PROPERTIES_DICT = {"cpu_arch": "x86_64",
                   "cpus": "8",
                   "local_gb": "10",
                   "memory_mb": "4096",
                   "capabilities": "server_hardware_type_uri:fake_sht_uri,"
                                   "enclosure_group_uri:fake_eg_uri"}
# "server_profile_template_uri": 'fake_spt_uri'

EXTRA_DICT = {'server_hardware_uri': 'fake_sh_uri'}
DRIVER_INFO_DICT = {}
INSTANCE_INFO_DICT = {"capabilities":
                      "server_profile_template_uri:fake_spt_uri"}


class OneViewClientTestCase(db_base.DbTestCase):

    def setUp(self):
        super(OneViewClientTestCase, self).setUp()
        self.config(manager_url='https://1.2.3.4', group='oneview')
        self.config(username='user', group='oneview')
        self.config(password='password', group='oneview')

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, 'get_node_power_state', autospec=True)
    def test_set_power_on_server_hardware(self, mock_get_node_power,
                                          mock_prepare_do_request):
        power_on = states.POWER_ON
        mock_get_node_power.return_value = power_on
        mock_prepare_do_request.return_value = {}
        driver_info = {"server_hardware_uri": "/any"}
        target_state = "On"

        current_state = oneview_client.set_node_power_state(driver_info,
                                                            target_state)
        self.assertEqual(current_state, power_on)

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    def test_set_power_on_server_hardware_nonexistent(
            self, mock_prepare_do_request):
        mock_prepare_do_request.return_value = {"error": "resource not found"}
        driver_info = {"server_hardware_uri": "/any_invalid"}
        target_state = states.POWER_ON

        self.assertRaises(
            driver_oneview_exceptions.OneViewResourceNotFoundError,
            oneview_client.set_node_power_state, driver_info, target_state
        )

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, 'get_node_power_state', autospec=True)
    def test_set_power_on_server_hardware_power_status_error(
            self, mock_get_node_power, mock_prepare_do_request):
        power = states.ERROR
        mock_get_node_power.return_value = power
        mock_prepare_do_request.return_value = {"error": "resource not found"}
        driver_info = {"server_hardware_uri": "/any"}
        target_state = "On"

        self.assertRaises(
            driver_oneview_exceptions.OneViewErrorStateSettingPowerState,
            oneview_client.set_node_power_state, driver_info, target_state
        )

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    def test_get_server_hardware_nonexistent(self, mock_prepare_do_request):
        mock_prepare_do_request.return_value = {"error": "resource not found"}

        try:
            oneview_client.get_server_hardware({})
            self.fail()
        except driver_oneview_exceptions.OneViewResourceNotFoundError:
            pass

    @mock.patch.object(oneview_client, 'get_authentication', autospec=True)
    def test_invalid_login_password_credentials(self, mock_get_authentication):
        mock_get_authentication.return_value = None
        try:
            oneview_client.prepare_and_do_request('/any')
            self.fail()
        except driver_oneview_exceptions.OneViewNotAuthorizedException:
            pass

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, 'get_authentication', autospec=True)
    def test_clone_assign_passing_none(self, mock_get_auth,
                                       mock_prepare_do_request):
        driver_info = {}
        server_profile_template_uri = None
        instance_uuid = 'any_uuid'
        mock_get_auth.return_value = "any_token"

        try:
            oneview_client.clone_and_assign(driver_info,
                                            server_profile_template_uri,
                                            instance_uuid)
            self.fail()
        except driver_oneview_exceptions.OneViewServerProfileTemplateError:
            pass

        driver_info = {"server_profile_template_uri": "any_spt"}
        mock_prepare_do_request.return_value = {}

        try:
            oneview_client.clone_and_assign(driver_info,
                                            server_profile_template_uri,
                                            instance_uuid)
            self.fail()
        except driver_oneview_exceptions.OneViewResourceNotFoundError:
            pass

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, 'get_server_hardware', autospec=True)
    @mock.patch.object(oneview_client, 'get_server_profile_template',
                       autospec=True)
    def test_clone_assign_passing_any_spt(self,
                                          mock_get_server_profile_template,
                                          mock_get_server_hardware,
                                          mock_prepare_do_request):
        server_profile_template_uri = "any_spt"
        driver_info = {"server_profile_template_uri": "any_spt"}
        instance_uuid = 'any_uuid'

        mock_prepare_do_request.return_value = {
            "uri": "any_uri",
            "data": "any_data"
        }
        mock_get_server_profile_template.return_value = {
            "type": "ServerProfileV4",
            "uri":
                "/rest/server-profiles/158a22f1-7c45-4d22-8cc4-7408f9d8cfcb",
            "name": "baremetal [8e96c0e0-8818-4158-ae03-cf94a627ffb4]",
            "description": "",
            "serialNumber": None,
            "uuid": None,
            "serverHardwareUri": None,
            "serverHardwareTypeUri":
            "/rest/server-hardware-types/2F25D778-9D58-4588-8D27-FB6643937739",
            "enclosureGroupUri":
                "/rest/enclosure-groups/dd3eaccc-e690-46cf-89fc-3f7d65b6d3b3",
                "enclosureUri": None,
                "enclosureBay": None,
                "affinity": "Bay",
                "associatedServer": None,
                "hideUnusedFlexNics": True,
                "firmware": {
                    "forceInstallFirmware": False,
                    "manageFirmware": False,
                    "firmwareBaselineUri": None
                },
                "macType": "Physical",
                "wwnType": "Physical",
                "serialNumberType": "Physical",
                "category": "server-profiles",
                "created": "20150619T172942.406Z",
                "modified": "20150701T161538.857Z",
                "status": "OK",
                "state": "Normal",
                "inProgress": False,
                "taskUri": "/rest/tasks/98BE6AAB-F524-44D6-9B70-D9EE24572347",
                "connections": [
                    {
                        "id": 1,
                         "name": "devstack-blade5",
                         "functionType": "Ethernet",
                         "deploymentStatus": "Reserved",
                         "networkUri":
                             "/rest/ethernet-networks/89e733fd-7b2b-46d9-a5b0-"
                             "a2eb5b4b47df",
                         "portId": "Flb 1:1-a",
                         "interconnectUri": None,
                         "macType": "Physical",
                         "wwpnType": "Physical",
                         "mac": "6C:3B:E5:BB:C0:B0",
                         "wwnn": None,
                         "wwpn": None,
                         "requestedMbps": "2500",
                         "allocatedMbps": 2500,
                         "maximumMbps": 10000,
                         "boot": {
                                 "priority": "Primary"
                         }
                    }
                ],
                "bootMode": None,
                "boot": {
                    "manageBoot": True,
                    "order": ["PXE", "CD", "Floppy", "USB", "HardDisk"]
                },
                "bios": {
                    "manageBios": False,
                    "overriddenSettings": []
                },
                "localStorage": {
                    "logicalDrives": [],
                    "manageLocalStorage": False,
                    "initialize": False
                },
                "sanStorage": {
                    "volumeAttachments": [],
                    "manageSanStorage": False
                },
                "eTag": "1435767322633/22"
        }
        mock_get_server_hardware.return_value = {
            'serialNumber': 'BRC3092WK1',
            'uri':
                '/rest/server-hardware/39343336-3537-5242-4333-303932574B31',
            'processorType': 'AMD Opteron(tm) Processor 6204',
            'mpIpAddress': '10.5.0.206',
            'category': 'server-hardware',
            'formFactor': 'HalfHeight',
            'serverHardwareTypeUri':
            '/rest/server-hardware-types/2F25D778-9D58-4588-8D27-FB6643937739',
            'uuid': '39343336-3537-5242-4333-303932574B31',
            'assetTag': '[Unknown]',
            'licensingIntent': 'OneView',
            'portMap': {
                'deviceSlots': [{
                    'physicalPorts': [{
                        'interconnectPort': 6,
                        'virtualPorts': [{
                            'wwpn': None,
                            'mac': '6C:3B:E5:BB:C0:B0',
                            'portNumber': 1,
                            'portFunction': 'a',
                            'wwnn': None
                        }, {
                            'wwpn': '10:00:6C:3B:E5:BB:C0:B1',
                            'mac': '6C:3B:E5:BB:C0:B1',
                            'portNumber': 2,
                            'portFunction': 'b',
                            'wwnn': '20:00:6C:3B:E5:BB:C0:B1'
                        }, {
                            'wwpn': None,
                            'mac': '6C:3B:E5:BB:C0:B2',
                            'portNumber': 3,
                            'portFunction': 'c',
                            'wwnn': None
                        }, {
                            'wwpn': None,
                            'mac': '6C:3B:E5:BB:C0:B3',
                            'portNumber': 4,
                            'portFunction': 'd',
                            'wwnn': None
                        }],
                        'mac': '6C:3B:E5:BB:C0:B0',
                        'portNumber': 1,
                        'interconnectUri':
                            '/rest/interconnects/7f9b7f04-c7b2-43c1-b599-5b443'
                            '65ec1c3',
                        'wwn': None,
                        'type': 'Ethernet'
                    }, {
                        'interconnectPort': 6,
                        'virtualPorts': [{
                            'wwpn': None,
                            'mac': '6C:3B:E5:BB:C0:B4',
                            'portNumber': 1,
                            'portFunction': 'a',
                            'wwnn': None
                        }, {
                            'wwpn': '10:00:6C:3B:E5:BB:C0:B5',
                            'mac': '6C:3B:E5:BB:C0:B5',
                            'portNumber': 2,
                            'portFunction': 'b',
                            'wwnn': '20:00:6C:3B:E5:BB:C0:B5'
                        }, {
                            'wwpn': None,
                            'mac': '6C:3B:E5:BB:C0:B6',
                            'portNumber': 3,
                            'portFunction': 'c',
                            'wwnn': None
                        }, {
                            'wwpn': None,
                            'mac': '6C:3B:E5:BB:C0:B7',
                            'portNumber': 4,
                            'portFunction': 'd',
                            'wwnn': None
                        }],
                        'mac': '6C:3B:E5:BB:C0:B4',
                        'portNumber': 2,
                        'interconnectUri':
                            '/rest/interconnects/d4a6afaa-b6bf-483c-b82d-c3d99'
                            'c785eba',
                        'wwn': None,
                        'type': 'Ethernet'
                    }],
                    'deviceName': 'HP FlexFabric 10Gb 2-port 554FLB Adapter',
                    'slotNumber': 1,
                    'location': 'Flb',
                    'oaSlotNumber': 9
                }, {
                    'physicalPorts': [],
                    'deviceName': '',
                    'slotNumber': 1,
                    'location': 'Mezz',
                    'oaSlotNumber': 1
                }, {
                    'physicalPorts': [{
                        'interconnectPort': 6,
                        'virtualPorts': [],
                        'mac': None,
                        'portNumber': 1,
                        'interconnectUri': None,
                        'wwn': '10:00:6C:3B:E5:C1:A5:B2',
                        'type': 'FibreChannel'
                    }, {
                        'interconnectPort': 6,
                        'virtualPorts': [],
                        'mac': None,
                        'portNumber': 2,
                        'interconnectUri': None,
                        'wwn': '10:00:6C:3B:E5:C1:A5:B3',
                        'type': 'FibreChannel'
                    }],
                    'deviceName': 'HP LPe1205A 8Gb FC HBA for BladeSystem',
                    'slotNumber': 2,
                    'location': 'Mezz',
                    'oaSlotNumber': 2
                }
                ]},
                'memoryMb': 16384,
                'state': 'NoProfileApplied',
                'stateReason': 'NotApplicable',
                'mpModel': 'iLO4',
                'serverProfileUri': None,
                'type': 'server-hardware-3',
                'status': 'Disabled',
                'description': None,
                'mpFirmwareVersion': '2.03 Nov 07 2014',
                'virtualSerialNumber': None,
                'eTag': '1436263913638',
                'processorSpeedMhz': 3300,
                'refreshState': 'NotRefreshing',
                'partNumber': '634975-B21',
                'locationUri': '/rest/enclosures/09BRC3203AFD',
                'shortModel': 'BL465c Gen8',
                'serverGroupUri':
                    '/rest/enclosure-groups/dd3eaccc-e690-46cf-89fc-3f7d65b6d3'
                    'b3',
                'powerState': 'Off',
                'name': 'LSD-enl, bay 6',
                'created': '2015-06-18T11:53:35.077Z',
                'powerLock': False,
                'processorCoreCount': 4,
                'modified': '2015-07-07T10:11:53.638Z',
                'processorCount': 2,
                'romVersion': 'A26 09/03/2014',
                'virtualUuid': None,
                'mpDnsName': 'ILOBRC3092WK1',
                'signature': {
                    'personalityChecksum': 1105556948,
                    'serverHwChecksum': 459966055
                },
                'position': 6,
                'model': 'ProLiant BL465c Gen8'
        }

        self.assertRaises(
            driver_oneview_exceptions.OneViewServerProfileCloneError,
            oneview_client.clone_and_assign,
            driver_info,
            server_profile_template_uri,
            instance_uuid
        )

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, '_build_clone_body', autospec=True)
    @mock.patch.object(oneview_client, 'get_server_hardware', autospec=True)
    @mock.patch.object(oneview_client, 'get_server_profile_template',
                       autospec=True)
    def test_clone_assign_time_out(self, mock_get_server_profile_template,
                                   mock_get_server_hardware,
                                   mock_build, mock_prepare_do_request):
        server_profile_template_uri = "any_spt"
        driver_info = {"server_profile_template_uri": "any_spt"}
        instance_uuid = 'any_uuid'

        mock_get_server_profile_template.return_value = {}
        mock_get_server_hardware.return_value = {}
        mock_build.return_value = {}

        mock_prepare_do_request.return_value = {'taskStatus': 'any'}

        self.assertRaises(
            driver_oneview_exceptions.OneViewMaxRetriesExceededError,
            oneview_client.clone_and_assign,
            driver_info,
            server_profile_template_uri,
            instance_uuid,
            max_retries=2
        )

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    def test_get_volume_nonexistent(self, mock_prepare_do_request):
        uri = "nonexistent_uri"
        mock_prepare_do_request.return_value = {
            "errorCode": "RESOURCE_NOT_FOUND",
            "data": None
        }

        self.assertRaises(
            driver_oneview_exceptions.OneViewResourceNotFoundError,
            oneview_client.get_volume_information,
            uri
        )

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, 'get_server_hardware', autospec=True)
    def test_unassign_and_delete_passing_no_server_profile_template(
            self,
            mock_get_server_hardware,
            mock_prepare_and_do_request):
        driver_info = None
        mock_get_server_hardware.return_value = {'serverProfileUri': 'spt_uri'}
        mock_prepare_and_do_request.return_value = {"Task": "Delete"}

        oneview_client.unassign_and_delete(driver_info)

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    def test_set_boot_device_nonexistent_resource_uri(self,
                                                      mock_prepare_do_request):
        driver_info = {}
        new_first_boot_device = "None"
        mock_prepare_do_request.return_value = {
            "errorCode": "RESOURCE_NOT_FOUND",
            "data": None
        }

        self.assertRaises(
            driver_oneview_exceptions.OneViewResourceNotFoundError,
            oneview_client.set_boot_device,
            driver_info,
            new_first_boot_device
        )

    @mock.patch.object(oneview_client, 'get_boot_order', autospec=True)
    def test_set_boot_device_nonexistent_resource_first_boot_device(
            self,
            mock_get_boot_order):
        driver_info = {}
        new_first_boot_device = None
        mock_get_boot_order.return_value = []

        self.assertRaises(
            driver_oneview_exceptions.OneViewBootDeviceInvalidError,
            oneview_client.set_boot_device,
            driver_info,
            new_first_boot_device
        )

    @mock.patch.object(oneview_client, 'prepare_and_do_request', autospec=True)
    @mock.patch.object(oneview_client, 'get_server_hardware', autospec=True)
    @mock.patch.object(oneview_client, 'get_boot_order', autospec=True)
    def test_get_server_profile_from_hardware(self, mock_get_boot_order,
                                              mock_get_server_hardware,
                                              mock_prepare_do_request):
        driver_info = {}
        new_first_boot_device = "any_boot_device"
        mock_get_boot_order.return_value = []
        mock_get_server_hardware.return_value = {}

        self.assertRaises(
            driver_oneview_exceptions.OneViewServerProfileAssociatedError,
            oneview_client.set_boot_device,
            driver_info,
            new_first_boot_device
        )

        mock_get_server_hardware.return_value = {"serverProfileUri": "any_uri"}
        mock_prepare_do_request.return_value = {}

        self.assertRaises(
            driver_oneview_exceptions.OneViewResourceNotFoundError,
            oneview_client.set_boot_device,
            driver_info,
            new_first_boot_device
        )

#     def test_invalid_url_credentials(self):
#         try:
#             oneview_client.prepare_and_do_request("/anyrequest")
#             self.fail()
#         except:
#             pass
