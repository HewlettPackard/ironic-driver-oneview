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

from ironic.common import exception
from ironic.common.i18n import _
from ironic.drivers.modules.oneview import oneview_client

REQUIRED_ON_PROPERTIES = {
    'server_hardware_type_uri': _("Server Hardware Type URI Required."),
}

REQUIRED_ON_INSTANCE_INFO = {
    'server_profile_template_uri': _("Server Profile Template URI to clone "
                                     "from. Required."),
}

REQUIRED_ON_EXTRAS = {
    'server_hardware_uri': _("Server Hardware URI. Required."),
}

OPTIONAL_ON_PROPERTIES = {
    'enclosure_group_uri': _("Enclosure Group URI.")
}

COMMON_PROPERTIES = {}
COMMON_PROPERTIES.update(REQUIRED_ON_PROPERTIES)
COMMON_PROPERTIES.update(REQUIRED_ON_EXTRAS)
COMMON_PROPERTIES.update(OPTIONAL_ON_PROPERTIES)


def node_has_server_profile(driver_info):
    server_hardware = oneview_client.get_server_hardware(driver_info)
    server_profile_uri = server_hardware.get("serverProfileUri")
    return server_profile_uri is not None


def parse_driver_info(node):
    properties = _verify_node_properties(node)
    extra = _verify_node_extra(node)

    instance_info = node.instance_info.get('capabilities', '')
    try:
        instance_info_dict = json.loads(instance_info)
        server_profile_template_uri = instance_info_dict.get(
            "server_profile_template_uri"
        )
        server_profile_template_uri = server_profile_template_uri.replace(
            "s!=", ""
        )
        server_profile_template_uri = server_profile_template_uri.strip()
    except ValueError:
        server_profile_template_uri = ''

    properties_dict = _capabilities_to_dict(properties)

    driver_info = {
        'server_hardware_uri':
            extra.get("server_hardware_uri"),
        'server_hardware_type_uri':
            properties_dict.get('server_hardware_type_uri', None),
        'enclosure_group_uri':
            properties_dict.get('enclosure_group_uri', None),
        'server_profile_template_uri': server_profile_template_uri,
    }

    return driver_info


def _verify_node_properties(node):
    properties = node.properties.get('capabilities', '')
    for key in REQUIRED_ON_PROPERTIES:
        if key not in properties:
            raise exception.MissingParameterValue(
                _("Missing the following OneView data in node's "
                  "properties/capabilities: %s.") % key
            )

    return properties


def _verify_node_extra(node):
    extra = node.extra or {}
    for key in REQUIRED_ON_EXTRAS:
        if not extra.get(key):
            raise exception.MissingParameterValue(
                _("Missing the following OneView data in node's extra: %s.")
                % key
            )

    return extra


def _capabilities_to_dict(capabilities):
    capabilities_dict = {}
    if capabilities:
        try:
            for capability in capabilities.split(','):
                key, value = capability.split(':')
                capabilities_dict[key] = value
        except ValueError:
            raise exception.InvalidParameterValue(
                _("Malformed capabilities value: %s") % capability
            )

    return capabilities_dict
