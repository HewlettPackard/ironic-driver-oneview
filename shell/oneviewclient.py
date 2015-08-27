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

import requests
import json
from objects import Flavor
from objects import ServerProfile

# urllib3.disable_warnings()

AUTHENTICATION_URL = '%s/rest/login-sessions'
SERVER_PROFILE_LIST_URI = '/rest/server-profiles?start=0&count=-1'
SERVER_HARDWARE_LIST_URI = '/rest/server-hardware?filter="status=Disabled OR status=OK OR status=Warning"'
VOLUMES_URI = '/rest/storage-volumes?start=0&count=-1'


GB_IN_BYTES = 1073741824

def check_request_status(response):
    repeat = False
    status = response.status_code

    if status in (409,):
        raise Exception("Conflict contacting OneView: ", response.json())
        repeat = True
    elif status in (403, 404, 500):
        raise Exception("Error contacting OneView: ", response.json())
    elif status not in (200, 202):
        raise Exception("Status not recognized:", status, response.json())

    return repeat


class OneViewRequest:

    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.token = None

    def _is_token_valid(self):
        return self.token is not None

    def _new_token(self):
        url = AUTHENTICATION_URL % self.address
        body = {'password': self.password,
                'userName': self.username}
        headers = {'content-type': 'application/json'}
        json_response = None
        repeat = True
        while repeat:
            r = requests.post(url, data=json.dumps(body), headers=headers,
                              verify=False)
            check_request_status(r)
            try:
                json_response = r.json()
                repeat = False
            except:
                repeat = True
        # NOTE(sinval): problems with jsondecode on the cloud. Remove it before
        # pushing
        # repeat = self._check_request_status(r)
        # decoded = r.text.decode('utf-8')
        # json_response = json.loads(decoded)
        # print json_response
        print headers
        return json_response.get('sessionID')

    def _update_token(self):
        if not self._is_token_valid():
            self.token = self._new_token()

    def prepare_and_do_request(self, uri, params=None):
        self._update_token()
        headers = {'content-type': 'application/json',
                   'X-Api-Version': '120', 'Auth': self.token}
        url = '%s%s' % (self.address, uri)
        # body = json.dumps(body)
        json_response = None
        repeat = True
        while repeat:
            r = requests.get(url, headers=headers, verify=False, params=params)
            check_request_status(r)
            try:
                json_response = r.json()
                repeat = False
            except:
                repeat = True
        # NOTE(sinval) GAMBIARRA PARA O PROBLEMA DO JSON DECODE
            # repeat = self._check_request_status(r)
        # decoded = r.text.decode('utf-8')
        # json_response = json.loads(decoded)
        # print json_response
        return json_response

    def server_hardware_list(self, server_hardware_type_filter=None):
        params = {'start': 0}
        if server_hardware_type_filter:
            params['serverHardwareTypeUri'] = server_hardware_type_filter
        response = self.prepare_and_do_request(SERVER_HARDWARE_LIST_URI,
                                              params=params)
        return response.get('members')

    def server_profile_list(self):
        response = self.prepare_and_do_request(SERVER_PROFILE_LIST_URI)
        server_profiles = response.get('members')

        return [profile for profile in server_profiles if not profile.get('serverHardwareUri')]

    def get_volumes(self):
        volumes = self.prepare_and_do_request(VOLUMES_URI)
        return volumes


    def get(self, uri):
        return self.prepare_and_do_request(uri)


class OneViewClientException(Exception):
    pass

class Client:

    def __init__(self, address, username, password):
        if not address:
            raise OneViewClientException("Exception: No OV_ADDRESS on env or"
                                         " --ov-address parameter supplied.")
        if not username:
            raise OneViewClientException("Exception: No OV_USERNAME on env or"
                                         " --ov-username  parameter supplied.")
        if not password:
            raise OneViewClientException("Exception: No OV_PASSWORD on env or"
                                         " --ov-password supplied.")

        self.oneview_request = OneViewRequest(address=address,
                                              username=username,
                                              password=password)

    def _server_hardware_list(self, server_hardware_type_filter=None):
        params = {'start': 0}
        if server_hardware_type_filter:
            params['serverHardwareTypeUri'] = server_hardware_type_filter
        return self.oneview_request.prepare_and_do_request(SERVER_HARDWARE_LIST_URI, params=params).get('members')

    def _server_profile_list(self):
        return self.oneview_request.prepare_and_do_request(SERVER_PROFILE_LIST_URI).get('members')

    def _server_profile_template_list(self):
        return [server_profile for server_profile in self._server_profile_list() if server_profile.get('serverHardwareUri') is None]

    def _construct_flavor_extra_specs(self, server_profile, cpu_arch='x86_64'):
        extra_specs = {}
        extra_specs['cpu_arch'] = cpu_arch
        extra_specs['oneview:server_profile_template_uri'] = server_profile.get('uri')
        extra_specs['capabilities:server_hardware_type_uri'] = server_profile.get('serverHardwareTypeUri')

        enclosure_group_uri = server_profile.get("enclosureGroupUri")
        if enclosure_group_uri:
            extra_specs['capabilities:enclosure_group_uri'] = enclosure_group_uri

        return extra_specs

    def _get_disk_size_in_gb(self, volume_uri):
        volume = self.oneview_request.get(volume_uri)
        return int(volume.get("provisionedCapacity")) / GB_IN_BYTES

    def _construct_flavor_disk(self, server_profile):
        volume_attachments = server_profile.get("sanStorage").get("volumeAttachments")
        if volume_attachments:
            volume_attached = volume_attachments[0]
            disk = self._get_disk_size_in_gb(volume_attached.get("volumeUri"))
            return disk
        # Since we don't have a facility to retrieve the local disk size from
        # Oneview, we're returning a pre-defined static value
        return 120

    def _construct_flavor(self, flavor_id, server_profile, server_hardware):
        flavor = {}
        flavor['ram_mb'] = server_hardware['memoryMb']
        flavor['cpus'] = server_hardware['processorCoreCount'] * server_hardware["processorCount"]
        flavor['disk'] = self._construct_flavor_disk(server_profile)
        flavor['cpu_arch'] = 'x86_64'
        flavor['server_profile_template_uri'] = server_profile.get('uri')
        flavor['server_hardware_type_uri'] = server_profile.get('serverHardwareTypeUri')
        flavor['enclosure_group_uri'] = server_profile.get("enclosureGroupUri")
        flavor['server_profile_template_name'] = self.oneview_request.get(server_profile.get('uri')).get('name')
        flavor['server_hardware_type_name'] = self.oneview_request.get(server_profile.get('serverHardwareTypeUri')).get('name')
        flavor['enclosure_group_uri_name'] = self.oneview_request.get(server_profile.get("enclosureGroupUri")).get('name')
        # self._construct_flavor_extra_specs(server_profile)
        return Flavor(id=flavor_id, info=flavor)

    def flavor_list(self):
        flavor_list = []

        flavor_id = 0
        for server_profile in self.oneview_request.server_profile_list():
            if server_profile.get('serverHardwareUri') is not None:
                continue

            for server_hardware in self.oneview_request.server_hardware_list(server_hardware_type_filter=server_profile.get('serverHardwareTypeUri')):
                if server_profile.get('serverHardwareTypeUri') == server_hardware.get('serverHardwareTypeUri')\
                and server_profile.get('enclosureGroupUri') == server_hardware.get("serverGroupUri"):
                    flavor_id += 1
                    flavor_list.append(self._construct_flavor(flavor_id, server_profile, server_hardware))


        return set(flavor_list)

