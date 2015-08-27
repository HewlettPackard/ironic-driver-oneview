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

"""
OneView Driver and supporting meta-classes.
"""

from ironic.drivers import base
from ironic.drivers.modules.oneview import deploy
from ironic.drivers.modules.oneview import management
from ironic.drivers.modules.oneview import oneview_client
from ironic.drivers.modules.oneview import power
from ironic.drivers.modules import pxe


class OneViewDriver(base.BaseDriver):
    """PXE + OneView driver.

    NOTE: This driver is meant only for testing environments.

    This driver implements the `core` functionality, combining
    :class:`ironic.drivers.ov.OVPower` for power on/off and reboot of virtual
    machines, with :class:`ironic.driver.pxe.PXE` for image
    deployment. Implementations are in those respective classes; this class is
    merely the glue between them.
    """

    def __init__(self):
        self.power = power.OneViewPower()
        self.deploy = deploy.OneViewDeploy()
        self.management = management.OneViewManagement()
        self.vendor = pxe.VendorPassthru()
        oneview_client.check_oneview_status()
        oneview_client.verify_oneview_version()


class FakeOneViewDriver(base.BaseDriver):
    """Fake OneView driver."""

    def __init__(self):
        self.power = power.OneViewPower()
        self.deploy = deploy.FakeOneViewDeploy()
        self.management = management.OneViewManagement()
        oneview_client.check_oneview_status()
        oneview_client.verify_oneview_version()
