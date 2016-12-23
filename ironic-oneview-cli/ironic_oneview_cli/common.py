# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2015 Universidade Federal de Campina Grande
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

from builtins import input
from oslo_utils import encodeutils
from oslo_utils import importutils
import prettytable
import six

client = importutils.try_import('oneview_client.client')
oneview_utils = importutils.try_import('oneview_client.utils')

SUPPORTED_DRIVERS = ['agent_pxe_oneview', 'iscsi_pxe_oneview', 'fake_oneview']


def get_oneview_client(args):
    """Generates an instance of the OneView client.

    Generates an instance of the OneView client using the imported
    oneview_client library.

    :returns: an instance of the OneView client
    """

    args.ov_audit = True if args.ov_audit == 'True' else False
    oneview_client = client.ClientV2(
        manager_url=args.ov_auth_url,
        username=args.ov_username,
        password=args.ov_password,
        allow_insecure_connections=args.insecure,
        tls_cacert_file=args.ov_cacert,
        max_polling_attempts=args.ov_max_polling_attempts,
        audit_enabled=args.ov_audit,
        audit_map_file=args.ov_audit_input,
        audit_output_file=args.ov_audit_output
    )

    return oneview_client


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
    """Returns the first environment variable set.

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
                data = getattr(o, field_name, '')
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
        element.id = counter
        counter += 1


def get_element_by_id(element_list, element_id):
    try:
        for element in element_list:
            if element.id == int(element_id):
                return element
    except Exception:
        return None


def get_element_by_name(element_list, element_name):
    try:
        for element in element_list:
            if element.name == element_name:
                return element
    except Exception:
        return None


def is_entry_invalid(entries, objects_list):
    if not entries:
        return True
    for entry in entries:
        element = get_element_by_id(objects_list, entry)
        if element is None:
            return True
    return False


def set_flavor_name(flavor):
    flavor_name_template = "%sMB-RAM_%s_%s_%s" % (flavor.ram_mb,
                                                  flavor.cpus,
                                                  flavor.cpu_arch,
                                                  flavor.disk)
    flavor_name = input("Insert a name for the Flavor. [%(default_name)s]> " %
                        {'default_name': flavor_name_template})

    if not flavor_name:
        return flavor_name_template
    return flavor_name


def approve_command_prompt(message):
    response = input(message)
    if response.lower() == 'y':
        return True
    return False
