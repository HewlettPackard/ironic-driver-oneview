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


def do_genrc(args):
    """Generate the Ironic OneView CLI sample file."""
    print("#!/usr/bin/env bash")
    print("\n# Ironic OneView CLI")

    # OneView

    print("\n# OneView HPE Authentication URL.")
    print("#export OV_AUTH_URL=")

    print("\n# OneView HPE username.")
    print("#export OV_USERNAME=")

    print("\n# Path to OneView CA certificate bundle file."
          " (only for secure connmections)")
    print("#export OV_CACERT=")

    print("\n# Max connection retries to check change on OneView HPE.")
    print("#export OV_MAX_POLLING_ATTEMPTS=12")

    print("\n# Enable OneView Audit Logging.")
    print("#export OV_AUDIT=False")

    print("\n# Path to map file for OneView audit cases. \n"
          "# Used only when OneView API audit is enabled. \n"
          "# See: https://github.com/openstack/python-oneviewclient")
    print("#export OV_AUDIT_INPUT=")

    print("\n# Path to OneView audit output file. (json format) \n"
          "# Created only when Oneview API audit is enabled.")
    print("#export OV_AUDIT_OUTPUT=")

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
        "# Allowed values: agent_pxe_oneview, iscsi_pxe_oneview, fake_oneview")
    print("#export OS_IRONIC_NODE_DRIVER=agent_pxe_oneview")
