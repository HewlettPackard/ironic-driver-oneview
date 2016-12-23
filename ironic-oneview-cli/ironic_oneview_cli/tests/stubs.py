# Copyright 2016 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Universidade Federal de Campina Grande
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


class StubIronicNode(object):

    def __init__(self, id, uuid, chassis_uuid, provision_state, driver,
                 ports, instance_uuid=None, driver_info={},
                 driver_internal_info={}, name='fake-node',
                 maintenance='False', maintenance_reason='',
                 properties={}, extra={}):

        self.id = id
        self.uuid = uuid
        self.chassis_uuid = chassis_uuid
        self.provision_state = provision_state
        self.driver = driver
        self.ports = ports
        self.driver_info = driver_info
        self.driver_internal_info = driver_internal_info
        self.maintenance = maintenance
        self.maintenance_reason = maintenance_reason
        self.properties = properties
        self.instance_uuid = instance_uuid
        self.extra = extra
        self.name = name


class StubNovaFlavor(object):

    def __init__(self, id, uuid, memory_mb, ram_mb, vcpus, cpus, cpu_arch,
                 disk, root_gb, ephemeral_gb, flavorid, swap, rxtx_factor,
                 vcpu_weight, disabled, is_public, name='fake-flavor',
                 extra_specs={}, projects=[]):

        self.id = id
        self.uuid = uuid
        self.name = name
        self.memory_mb = memory_mb
        self.ram_mb = ram_mb  # remove before python-oneviewclient
        self.vcpus = vcpus
        self.cpus = cpus  # remove before python-oneviewclient
        self.cpu_arch = cpu_arch  # remove before python-oneviewclient
        self.disk = disk  # remove before python-oneviewclient
        self.root_gb = root_gb
        self.ephemeral_gb = ephemeral_gb
        self.flavorid = flavorid
        self.swap = swap
        self.rxtx_factor = rxtx_factor
        self.vcpu_weight = vcpu_weight
        self.disabled = disabled
        self.is_public = is_public
        self.extra_specs = extra_specs
        self.projects = projects


class StubEnclosureGroup(object):

    def __init__(self, uri, uuid, name):

        self.uri = uri
        self.uuid = uuid
        self.name = name


class StubServerHardware(object):

    def __init__(self, name, uuid, uri, power_state, server_profile_uri,
                 server_hardware_type_uri, enclosure_group_uri, status, state,
                 state_reason, enclosure_uri, processor_count,
                 processor_core_count, memory_mb, port_map, mp_host_info):

        self.name = name
        self.uuid = uuid
        self.uri = uri
        self.power_state = power_state
        self.server_profile_uri = server_profile_uri
        self.server_hardware_type_uri = server_hardware_type_uri
        self.enclosure_group_uri = enclosure_group_uri
        self.status = status
        self.state = state
        self.state_reason = state_reason
        self.enclosure_uri = enclosure_uri
        self.cpus = processor_count * processor_core_count
        self.memory_mb = memory_mb
        self.port_map = port_map
        self.mp_host_info = mp_host_info


class StubServerHardwareType(object):

    def __init__(self, uri, uuid, name):

        self.uri = uri
        self.uuid = uuid
        self.name = name


class StubServerProfileTemplate(object):

    def __init__(self, uri, name, server_hardware_type_uri,
                 enclosure_group_uri, connections, boot):

        self.uri = uri
        self.name = name
        self.server_hardware_type_uri = server_hardware_type_uri
        self.enclosure_group_uri = enclosure_group_uri
        self.connections = connections
        self.boot = boot


class StubParameters(object):

    def __init__(self,
                 os_ironic_node_driver,
                 os_ironic_deploy_kernel_uuid,
                 os_ironic_deploy_ramdisk_uuid):

        self.os_ironic_node_driver = os_ironic_node_driver
        self.os_ironic_deploy_kernel_uuid = os_ironic_deploy_kernel_uuid
        self.os_ironic_deploy_ramdisk_uuid = os_ironic_deploy_ramdisk_uuid
