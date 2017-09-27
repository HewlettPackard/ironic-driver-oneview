# Copyright (2015-2017) Hewlett Packard Enterprise Development LP
# Copyright (2015-2017) Universidade Federal de Campina Grande
# Copyright 2012 Red Hat, Inc.
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

import os
import prettytable
import six

from builtins import input
from oslo_utils import encodeutils
from oslo_utils import importutils
from six.moves.urllib import parse

hpclient = importutils.try_import('hpOneView.oneview_client')

# NOTE(fellypefca): Classic Drivers will be deprecated on Openstack Queens
SUPPORTED_DRIVERS = ['agent_pxe_oneview', 'iscsi_pxe_oneview', 'fake_oneview']
SUPPORTED_HARDWARE_TYPES = ['oneview']


def get_hponeview_client(args):
    """Generate an instance of the hpOneView client.

    Generates an instance of the hpOneView client using the hpOneView library.

    :returns: an instance of the OneView client
    """
    return hpclient.OneViewClient({"ip": args.ov_auth_url,
                                   "credentials": {
                                       "userName": args.ov_username,
                                       "password": args.ov_password}})


def get_uuid_from_uri(uri):
    if uri:
        return uri.split("/")[-1]


def arg(*args, **kwargs):
    """Decorator for CLI args.

    Example:

    >>> @arg("name", help="Name of the new entity")
    ... def entity_create(args):
    ...     pass
    """
    def _decorator(func):
        add_arg(func, *args, **kwargs)
        return func
    return _decorator


def add_arg(func, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""
    if not hasattr(func, 'arguments'):
        func.arguments = []

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in func.arguments:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.arguments.insert(0, (args, kwargs))


def env(*args, **kwargs):
    """Return the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


def _print_list(objs, fields, formatters=None, sortby_index=0,
                mixed_case_fields=None, field_labels=None):
    """Print a list or objects as a table, one row per object.

    :param objs: iterable of :class:`Resource`
    :param fields: attributes that correspond to columns, in order
    :param formatters: `dict` of callables for field formatting
    :param sortby_index: index of the field for sorting table rows
    :param mixed_case_fields: fields corresponding to object attributes that
        have mixed case names (e.g., 'serverId')
    :param field_labels: Labels to use in the heading of the table, default to
        fields.
    """
    formatters = formatters or {}
    mixed_case_fields = mixed_case_fields or []
    field_labels = field_labels or fields
    if len(field_labels) != len(fields):
        raise ValueError(("Field labels list %(labels)s has different number "
                          "of elements than fields list %(fields)s"),
                         {'labels': field_labels, 'fields': fields})

    if sortby_index is None:
        kwargs = {}
    else:
        kwargs = {'sortby': field_labels[sortby_index]}
    pt = prettytable.PrettyTable(field_labels)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                data = o.get(field_name)
                row.append(data)
        pt.add_row(row)

    if six.PY3:
        print(encodeutils.safe_encode(pt.get_string(**kwargs)).decode())
    else:
        print(encodeutils.safe_encode(pt.get_string(**kwargs)))


def print_prompt(object_list, header_list, input_message=None,
                 field_labels=None):
    _print_list(
        object_list,
        header_list,
        mixed_case_fields=[],
        field_labels=field_labels
    )
    if input_message is not None:
        input_value = input(input_message)
        return input_value


def assign_elements_with_new_id(element_list):
    counter = 1
    for element in element_list:
        element['id'] = counter
        counter += 1


def get_element_by_id(element_list, element_id):
    try:
        for element in element_list:
            if element['id'] == int(element_id):
                return element
    except Exception:
        return


def get_element_by_name(element_list, element_name):
    try:
        for element in element_list:
            if element['name'] == element_name:
                return element
    except Exception:
        return


def is_entry_invalid(entries, objects_list):
    if not entries:
        return True
    for entry in entries:
        element = get_element_by_id(objects_list, entry)
        if element is None:
            return True
    return False


def set_flavor_name(flavor):
    flavor_name_template = "%sMB-RAM_%s_%s_%s" % (flavor.get('ram_mb'),
                                                  flavor.get('cpus'),
                                                  flavor.get('cpu_arch'),
                                                  flavor.get('disk'))
    flavor_name = input(
        "Insert a name for the Flavor. [%(default_name)s]> " %
        {'default_name': flavor_name_template}
    )

    if not flavor_name:
        return flavor_name_template
    return flavor_name


def get_attribute_from_dict(dictionary, keyword, default_value=''):
    """Get value from a dictionary if the dictionary exists.

    :param dictionary: 'dict' with the elements
    :param keyword: attributes that correspond to a key in the dict
    :param default_value: The default value returned if the dictionary does not
        exist or if the keyword does not exist.
    :returns: The value to keyword or the default value.
    """
    if dictionary:
        return dictionary.get(keyword, default_value)
    else:
        return default_value


def approve_command_prompt(message):
    response = input(message)
    return response.lower() == 'y'


def get_oneview_nodes(ironic_nodes):
    """Get the nodes which drivers are compatible with OneView.

    :param ironic_nodes: A list of Ironic Nodes
    :returns: A list of Ironic Nodes with OneView compatible Drivers and
              Hardware types only.
    """
    return filter(lambda x: x.driver in SUPPORTED_DRIVERS +
                  SUPPORTED_HARDWARE_TYPES, ironic_nodes)


def get_server_hardware_id_from_node(ironic_node):
    """Get the Server Hardware id from a ironic_node

    :param ironic_node: A Ironic Node
    :return: The Server hardware id
    """
    server_hardware_uri = ironic_node.driver_info.get(
        'server_hardware_uri')
    return get_uuid_from_uri(server_hardware_uri)


def get_ilo_access(remote_console):
    """Get the needed information to access ilo.

    Get the host_ip and a token of an iLO remote console instance which can be
    used to perform operations on that controller.

    The Remote Console url has the following format:
    hplocons://addr=1.2.3.4&sessionkey=a79659e3b3b7c8209c901ac3509a6719

    :param: remote_console: OneView Remote Console object with a
            remoteConsoleUrl
    :returns: A tuple with the Host IP and Token to access ilo, for
              example: ('1.2.3.4', 'a79659e3b3b7c8209c901ac3509a6719')
    """
    url = remote_console.get('remoteConsoleUrl')
    url_parse = parse.urlparse(url)
    host_ip = parse.parse_qs(url_parse.netloc).get('addr')[0]
    token = parse.parse_qs(url_parse.netloc).get('sessionkey')[0]
    return host_ip, token
