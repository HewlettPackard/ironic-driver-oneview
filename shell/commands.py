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

import argparse

from ironicclient.openstack.common import cliutils


def _get_flavor_name(flavor):
    FLAVOR_NAME_TEMPLATE = "%s-%sMB-RAM_%s_%s_%s"
    return FLAVOR_NAME_TEMPLATE % (
        flavor.server_profile_template_name,
        flavor.ram_mb,
        flavor.cpus,
        flavor.cpu_arch,
        flavor.disk)


def _get_element_by_id(element_list, element_id):
    for element in element_list:
        if element.id == element_id:
            return element


@cliutils.arg('--detail', dest='detail', action='store_true', default=False,
              help="Show detailed information about the nodes.")
def do_flavor_create(oneviewclient, novaclient, args):
    """
    Show a list with suggested flavors to be created based on OneView's Server
    Profile Templates. The user can then select a flavor to create based on
    it's ID.
    """
    create_another_flavor_flag = True
    flavor_list = oneviewclient.flavor_list()
    flavor_list = list(flavor_list)

    for j in range(1, len(flavor_list)):
        chave = flavor_list[j]
        i = j - 1
        while i >= 0 and int(flavor_list[i].cpus) > int(chave.cpus):
            flavor_list[i + 1] = flavor_list[i]
            i -= 1
        flavor_list[i + 1] = chave

    for i in range(0, len(flavor_list)):
        flavor_list[i].__setitem__(i + 1)

    flavor_list = set(flavor_list)

    while create_another_flavor_flag:
        create_another_flavor_flag = False
        cliutils.print_list(
            flavor_list,
            ['id', 'cpus', 'disk', 'ram_mb', 'server_profile_template_name',
             'server_hardware_type_name', 'enclosure_group_name'],
            sortby_index=1)
        id = raw_input(
            "Insert flavor Id to add in OneView (press 'q' to quit)> ")

        if id == "q":
            break

        flavor = _get_element_by_id(flavor_list, int(id))
        cliutils.print_list(
            [flavor],
            ['cpus', 'disk', 'ram_mb', 'server_profile_template_name',
             'server_hardware_type_name', 'enclosure_group_name'],
            sortby_index=2)
        flavor_name_default = _get_flavor_name(flavor)
        flavor_name = raw_input(
            "Insert the name of the flavor. Leave blank for [" + flavor_name_default +
            "] (press 'q' to quit)> ")

        if flavor_name == "q":
            break

        if len(flavor_name) == 0:
            flavor_name = flavor_name_default
        nova_flavor = novaclient.flavors.create(
            flavor_name, flavor.ram_mb, flavor.cpus, flavor.disk)
        nova_flavor.set_keys(flavor.extra_specs())
        print('Flavor Created!\n')
        response = raw_input('Create a new flavor? (y/n)> ')
        if response in 'Yy':
            create_another_flavor_flag = True
