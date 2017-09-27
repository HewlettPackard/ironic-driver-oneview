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


def do_genrc(args):
    """Generate the Ironic OneView CLI sample file."""
    print("#!/usr/bin/env bash")
    print("\n# Ironic OneView CLI")

    # OneView

    print("\n# OneView HPE Authentication URL.")
    print("# Only the domain, without https:// or http://.")
    print("#export OV_AUTH_URL=")

    print("\n# OneView HPE username.")
    print("#export OV_USERNAME=")

    print("\n# Pass the OneView HPE password when executed.")
    print("echo \"Please enter your HP OneView password: \"")
    print("read -sr OV_PASSWORD_INPUT")
    print("export OV_PASSWORD=$OV_PASSWORD_INPUT")

    # OpenStack

    print("\n# Assume inspection is used for OneView nodes in Ironic.\n"
          "# As a consequence, the CLI will enroll nodes without\n"
          "# hardware properties.")
    print("#export OS_INSPECTION_ENABLED=False")

    print("\n# Ironic deploy kernel image uuid.")
    print("#export OS_IRONIC_DEPLOY_KERNEL_UUID=")

    print("\n# Ironic deploy ramdisk image uuid.")
    print("#export OS_IRONIC_DEPLOY_RAMDISK_UUID=")

    print(
        "\n# OneView Ironic driver for node creation. \n"
        "# Classic Drivers will be deprecated on Queens. \n"
        "# Allowed values: agent_pxe_oneview, iscsi_pxe_oneview, fake_oneview")
    print("#export OS_IRONIC_NODE_DRIVER=agent_pxe_oneview")

    print(
        "\n# OpenStack Ironic Driver for node creation. \n"
        "# Allowed values: oneview")
    print("#export OS_DRIVER=oneview")

    print(
        "\n# OpenStack Ironic Power interface for node creation. \n"
        "# Allowed values: oneview")
    print("#export OS_POWER_INTERFACE=oneview")

    print(
        "\n# OpenStack Ironic Management interface for node creation. \n"
        "# Allowed values: oneview")
    print("#export OS_MANAGEMENT_INTERFACE=oneview")

    print(
        "\n# OpenStack Ironic Inspect interface for node creation. \n"
        "# Allowed values: oneview")
    print("#export OS_INSPECT_INTERFACE=oneview")

    print(
        "\n# OpenStack Ironic Deploy interface for node creation. \n"
        "# Allowed values: oneview-direct, oneview-iscsi")
    print("#export OS_DEPLOY_INTERFACE=oneview-direct")
