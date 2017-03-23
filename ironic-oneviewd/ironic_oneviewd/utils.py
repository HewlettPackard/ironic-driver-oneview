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

import six

from ironicclient import client as ironic_client

from oslo_log import log as logging
from oslo_utils import importutils

from ironic_oneviewd.conf import CONF
from ironic_oneviewd import exceptions
from ironic_oneviewd.openstack.common._i18n import _

client = importutils.try_import('oneview_client.client')
oneview_states = importutils.try_import('oneview_client.states')
oneview_exceptions = importutils.try_import('oneview_client.exceptions')

REQUIRED_ON_PROPERTIES = {
    'server_hardware_type_uri': _("Server Hardware Type URI Required."),
    'server_profile_template_uri': _("Server Profile Template URI required"),
}

REQUIRED_ON_EXTRAS = {
    'server_hardware_uri': _("Server Hardware URI. Required."),
}

IRONIC_API_VERSION = 1

LOG = logging.getLogger(__name__)


def get_ironic_client():
    """Generates an instance of the Ironic client.

    This method creates an instance of the Ironic client using the OpenStack
    credentials from config file and the imported ironicclient library.

    :returns: an instance of the Ironic client
    """
    daemon_kwargs = {
        'os_username': CONF.openstack.username,
        'os_password': CONF.openstack.password,
        'os_auth_url': CONF.openstack.auth_url,
        'os_region_name': CONF.openstack.region_name,
        'insecure': CONF.openstack.insecure,
        'os_cacert': CONF.openstack.cacert,
        'os_cert': CONF.openstack.cert,
        'os_endpoint_type': CONF.openstack.endpoint_type,
        'os_project_id': CONF.openstack.project_id,
        'os_project_name': CONF.openstack.project_name,
        'os_tenant_id': CONF.openstack.tenant_id,
        'os_tenant_name': CONF.openstack.tenant_name,
        'os_user_domain_id': CONF.openstack.user_domain_id,
        'os_user_domain_name': CONF.openstack.user_domain_name,
        'os_project_domain_id': CONF.openstack.project_domain_id,
        'os_project_domain_name': CONF.openstack.project_domain_name,
        'os_ironic_api_version': '1.22'
    }

    LOG.debug("Using OpenStack credentials specified in the configuration "
              "file to get Ironic Client")

    return ironic_client.get_client(IRONIC_API_VERSION, **daemon_kwargs)


def get_oneview_client():
    """Generates an instance of the OneView client.

    Generates an instance of the OneView client using the imported
    oneview_client library.

    :returns: an instance of the OneView client
    """
    oneview_client = client.Client(
        manager_url=CONF.oneview.manager_url,
        username=CONF.oneview.username,
        password=CONF.oneview.password,
        allow_insecure_connections=CONF.oneview.allow_insecure_connections,
        tls_cacert_file=CONF.oneview.tls_cacert_file,
        max_polling_attempts=CONF.oneview.max_polling_attempts,
        audit_enabled=CONF.oneview.audit_enabled,
        audit_map_file=CONF.oneview.audit_map_file,
        audit_output_file=CONF.oneview.audit_output_file
    )
    return oneview_client


def verify_node_properties(node):
    properties = node.properties.get('capabilities', '')
    for key in REQUIRED_ON_PROPERTIES:
        if key not in properties:
            raise exceptions.MissingParameterValue(
                _("Missing the following OneView data in node's "
                  "properties/capabilities: %s.") % key
            )

    return properties


def verify_node_extra(node):
    extra = node.extra or {}
    for key in REQUIRED_ON_EXTRAS:
        if not extra.get(key):
            raise exceptions.MissingParameterValue(
                _("Missing the following OneView data in node's extra: %s.")
                % key
            )

    return extra


def capabilities_to_dict(capabilities):
    """Parse the capabilities string into a dictionary

    :param capabilities: the node capabilities as a formatted string
    :raises: InvalidParameterValue if capabilities is not an string or has
             a malformed value
    """
    capabilities_dict = {}
    if capabilities:
        if not isinstance(capabilities, six.string_types):
            raise exceptions.InvalidParameterValue(
                _("Value of 'capabilities' must be string. Got %s")
                % type(capabilities))
        try:
            for capability in capabilities.split(','):
                key, value = capability.split(':')
                capabilities_dict[key] = value
        except ValueError:
            raise exceptions.InvalidParameterValue(
                _("Malformed capabilities value: %s") % capability
            )
    return capabilities_dict


def dynamic_allocation_enabled(node):
    flag = node.driver_info.get('dynamic_allocation')
    if flag:
        if str(flag).lower() == 'true':
            return True
        elif str(flag).lower() == 'false':
            return False
        else:
            msg = (("Invalid dynamic_allocation parameter value "
                    "'%(flag)s' in node's %(node_uuid)s driver_info. "
                    "Valid values are booleans true or false.") %
                   {"flag": flag, "node_uuid": node.uuid})
            raise exceptions.InvalidParameterValue(msg)
    return False


def get_node_info_from_node(node):
    capabilities_dict = capabilities_to_dict(
        node.properties.get('capabilities', '')
    )
    driver_info = node.driver_info
    oneview_info = {
        'server_hardware_uri':
            driver_info.get('server_hardware_uri'),
        'server_hardware_type_uri':
            capabilities_dict.get('server_hardware_type_uri'),
        'enclosure_group_uri':
            capabilities_dict.get('enclosure_group_uri'),
        'server_profile_template_uri':
            capabilities_dict.get('server_profile_template_uri') or
            driver_info.get('server_profile_template_uri')
    }
    return oneview_info


def node_has_hardware_propeties(node):
    properties = [node.properties.get("memory_mb"),
                  node.properties.get("cpu_arch"),
                  node.properties.get("local_gb"),
                  node.properties.get("cpus")]
    return all(properties)


def server_profile_template_uri_from_node(node):
    node_capabilities = capabilities_to_dict(
        node.properties.get('capabilities')
    )
    node_server_profile_template_uri = node_capabilities.get(
        'server_profile_template_uri'
    )
    return node_server_profile_template_uri


def server_hardware_uri_from_node(node):
    return node.driver_info.get('server_hardware_uri')


def server_hardware_uuid_from_node(node):
    uri = server_hardware_uri_from_node(node)
    return uuid_from_uri(uri)


def uuid_from_uri(uri):
    return uri.split("/")[-1]
