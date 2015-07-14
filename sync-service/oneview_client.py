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

import json
import os
import time

import requests

import config_client
import oneview_uri

from ironic.common.i18n import _LE
from ironic.common.i18n import _LI
from ironic.common import states

from oslo_config import cfg
from oslo_config import types
from oslo_log import log as logging

from sync_exceptions import OneViewConnectionError


LOG = logging.getLogger(__name__)

ONEVIEW_POWER_ON = 'On'
ONEVIEW_POWER_OFF = 'Off'


class OneViewRequestAPI:

    def __init__(self):
        self.token = None
        self.oneview_conf = config_client.ConfClient().oneview


    def _get_verify_connection_option(self):
        verify_status = False
        user_cacert = self.oneview_conf.get_tls_cacert_file()
        if self.oneview_conf.get_allow_insecure_connections() is False:
            if(user_cacert is None):
                verify_status = True
            else:
                verify_status = user_cacert
        return verify_status


    def _is_token_valid(self):
        return self.token is not None


    def _try_execute_request(self, url, request_type, body, headers,
                             verify_status):
        try:
            return requests.request(request_type, url, data=json.dumps(body),
                                    headers=headers, verify=verify_status)
        except requests.RequestException as ex:
            LOG.error(_LE("Can't connect to OneView: %s")
                      % (str(ex.message).split(':')[-1]))
            LOG.error(("Can't connect to OneView: %s")
                      % (str(ex.message).split(':')[-1]))
            raise OneViewConnectionError(
                "Can't connect to OneView: %s" % str(ex.message))


    def _new_token(self):
        LOG.info(_LI("Using OneView credentials specified in synch.conf"))
        LOG.info(("Using OneView credentials specified in synch.conf"))
        url = '%s%s' % (self.oneview_conf.get_manager_url(),
                        oneview_uri.AUTHENTICATION_URL)
        body = {
            'password': self.oneview_conf.get_password(),
            'userName': self.oneview_conf.get_username()
        }
        headers = {'content-type': 'application/json'}
        verify_status = self._get_verify_connection_option()
        if verify_status is False:
            LOG.warn('Using insecure connection')
        json_response = None
        repeat = True
        while repeat:
            r = self._try_execute_request(url, 'POST', body, headers,
                                      verify_status)
            # NOTE: Workaround to fix JsonDecode problems
            try:
                json_response = r.json()
                repeat = self._check_request_status(r)
            except:
                repeat = True
        return json_response.get('sessionID')


    def _update_token(self):
        if not self._is_token_valid():
            self.token = self._new_token()


    def _check_request_status(self, response):
        repeat = False
        status = response.status_code
        response_json = response.json()
        if status in (409,):
            ignored_conflicts = {'RABBITMQ_CLIENTCERT_CONFLICT'}
            if (response_json.get('errorCode') in ignored_conflicts):
                repeat = False
            else:
                repeat = True
            LOG.debug("Conflict contacting OneView: ", response_json)
        elif status in (404, 500):
            LOG.error(_LE("Error contacting OneView: "), response_json)
            LOG.error(("Error contacting OneView: "), response_json)
        elif status not in (200, 202):
            LOG.warn("Status not recognized:", status, response_json)
        return repeat


    def prepare_and_do_request(self, uri, body={}, request_type='GET'):
        self._update_token()
        headers = {
           'content-type': 'application/json',
           'X-Api-Version': '120',
           'Auth': self.token
        }
        url = '%s%s' % (self.oneview_conf.get_manager_url(), uri)
        verify_status = self._get_verify_connection_option()
        json_response = None
        repeat = True
        while repeat:
            r = self._try_execute_request(url, request_type, body, headers,
                                          verify_status)
            # NOTE: Workaround to fix JsonDecode problems
            try:
                json_response = r.json()
                repeat = self._check_request_status(r)
            except Exception as ex:
                repeat = True
        return json_response


class OneViewCertificateAPI(OneViewRequestAPI):

    def get_certificate(self):
        return self.prepare_and_do_request(
            oneview_uri.CERTIFICATE_AND_KEY_URI).get('base64SSLCertData')


    def get_key(self):
        return self.prepare_and_do_request(
            oneview_uri.CERTIFICATE_AND_KEY_URI).get('base64SSLKeyData')


    def get_ca(self):
        return self.prepare_and_do_request(oneview_uri.CA_URI)


    def post_certificate(self):
        body = {'type': 'RabbitMqClientCertV2', 'commonName': 'default'}

        return self.prepare_and_do_request(oneview_uri.CERTIFICATE_RABBIT_MQ,
                                           body=body, request_type='POST')


class OneViewServerHardwareAPI(OneViewRequestAPI):

    def get_server_hardware(self, uri):
        return self.prepare_and_do_request(uri)


    def get_server_hardware_list(self):
        uri = "/rest/server-hardware?start=0&count=-1"
        server_hardwares = self.prepare_and_do_request(uri)
        return server_hardwares.get("members")


    def get_node_power_state(self, server_hardware_uri):
        power_state = self.prepare_and_do_request(uri=server_hardware_uri,
                      request_type='GET').get('powerState')
        if power_state == 'On' or power_state == 'PoweringOff':
            return states.POWER_ON
        elif power_state == 'Off' or power_state == 'PoweringOn':
            return states.POWER_OFF
        elif power_state == 'Resetting':
            return states.REBOOT
        else:
            return states.ERROR


    def parse_server_hardware_to_dict(self, server_hardware):
        port_map = server_hardware.get('portMap')
        try:
            physical_ports = port_map.get('deviceSlots')[0].get(
                                'physicalPorts')
            mac_address = physical_ports[0].get('mac')
        except Exception:
            raise Exception("Server hardware primary physical NIC not found.")
        vcpus = (server_hardware["processorCoreCount"] *
                 server_hardware["processorCount"])
        return {'name': server_hardware["name"],
                'cpus': vcpus,
                'memory_mb': server_hardware["memoryMb"],
                'local_gb': 120,
                'server_hardware_uri': server_hardware["uri"],
                'server_hardware_type_uri':
                    server_hardware["serverHardwareTypeUri"],
                'enclosure_group_uri': server_hardware['serverGroupUri'],
                'cpu_arch': 'x86_64',
                'mac': mac_address,
                'server_profile_uri': server_hardware.get('serverProfileUri')
                }


class OneViewClient:
    def __init__(self):
        self.certificate_api = OneViewCertificateAPI()
        self.server_hardware_api = OneViewServerHardwareAPI()
