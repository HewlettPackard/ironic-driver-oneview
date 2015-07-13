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

import rabbitmq_client
import service_manager

from oslo_log import log as logging


LOG = logging.getLogger(__name__)
REASON = "It has a server profile in OneView"

drivers = {"pxe_oneview", "fake_oneview"}


def _get_new_ov_server_hardwares():
    new_server_hardwares = []
    nodes = service_manager.get_ironic_client().node.list(detail=True)

    for server_hardware in service_manager.get_ov_server_hardware_list():
        if not _is_ov_server_hardware_in_ironic(
            server_hardware=server_hardware, nodes=nodes):
            new_server_hardwares.append(server_hardware)

    return new_server_hardwares


def _get_old_ov_server_hardwares():
    old_server_hardwares = []
    nodes = service_manager.get_ironic_client().node.list(detail=True)

    for server_hardware in service_manager.get_ov_server_hardware_list():
        if _is_ov_server_hardware_in_ironic(
            server_hardware=server_hardware, nodes=nodes):
            old_server_hardwares.append(server_hardware)

    return old_server_hardwares


def _is_ov_server_hardware_in_ironic(server_hardware, nodes=None):
    if nodes is None:
        nodes = service_manager.get_ironic_client().node.list(detail=True)
    for node in nodes:
        node_server_hardware_uri = node.extra.get("server_hardware_uri")
        if node_server_hardware_uri == server_hardware.get("uri"):
            LOG.info("Server Hardware %(server_hardware_name)s has a "
                     "corresponding node in Ironic",
                     {'server_hardware_name': server_hardware.get("name")})
            return True

    return False


def _is_ironic_node_represented_in_oneview(node_server_hardware_uri):
    LOG.info('Checking if server hardware %(server_hardware)s is in '
                 'OneView', {'server_hardware': node_server_hardware_uri})
    server_hardwares = service_manager.get_ov_server_hardware_list()

    for sh in server_hardwares:
        server_hardware_uri = sh.get("uri")
        if server_hardware_uri == node_server_hardware_uri:
            LOG.info('Server hardware %(server_hardware)s in OneView',
                         {'server_hardware': node_server_hardware_uri})
            return True

    LOG.info('Server hardware %(server_hardware)s not in OneView',
                 {'server_hardware': node_server_hardware_uri})
    return False


def create_ironic_node(server_hardware_info):
    LOG.info('Creating node in Ironic reflecting server hardware '
             '%(server_hardware)s',
             {'server_hardware': server_hardware_info})

    sync_conf = service_manager.get_config_options()
    kwargs_node = {
                   # TODO: name should be hostname safe (WHYYY?)
                   # 'name': server_hardware_info.get('name')
                   # Uncomment as soon as final design decision from
                   # Ironic is released
                   'driver': sync_conf.ironic.default_sync_driver,
                   'driver_info': {'deploy_kernel':
                                   sync_conf.ironic.default_deploy_kernel_id,
                                   'deploy_ramdisk':
                                   sync_conf.ironic.default_deploy_ramdisk_id},
                   'properties': {'cpus': server_hardware_info.get('cpus'),
                                  'memory_mb': server_hardware_info.get(
                                                   'memory_mb'),
                                  'local_gb': server_hardware_info.get(
                                                   'local_gb'),
                                  'cpu_arch': server_hardware_info.get(
                                                   'cpu_arch'),
                                  'capabilities': 'server_hardware_type_uri:'
                                                  '%s,enclosure_group_uri:%s,'
                                                  'server_profile_template'
                                                  '_uri:%s' %
                                                  (server_hardware_info.get(
                                                   'server_hardware_type_uri'),
                                                   server_hardware_info.get(
                                                   'enclosure_group_uri'),
                                                   'None')},
                   'extra': {'server_hardware_uri': server_hardware_info.get(
                                                    'server_hardware_uri')},
                  }
    ironic_client = service_manager.get_ironic_client()
    node = ironic_client.node.create(**kwargs_node)
    LOG.info('Creating port for Node %(node_uuid)s using mac %(mac)s',
             {'node_uuid': node.uuid,
              'mac': server_hardware_info.get('mac')})
    ironic_client.port.create(node_uuid=node.uuid,
                              address=server_hardware_info.get('mac'))
    return node


def create_ironic_nodes():
    new_server_hardwares = _get_new_ov_server_hardwares()

    for server_hardware in new_server_hardwares:
        server_hardware_info = service_manager.parse_server_hardware_to_dict(
                                   server_hardware)
        create_server_hardware_as_ironic_node(server_hardware_info)
    ironic_client = service_manager.get_ironic_client()
    old_server_hardwares = _get_old_ov_server_hardwares()
    nodes = ironic_client.node.list()

    for server_hardware in old_server_hardwares:
        is_hardware_available = server_hardware_info.get(
                                    'server_profile_uri') is not None
        if is_hardware_available:
            update_ironic_node_maintenance_state(server_hardware, nodes)


def create_server_hardware_as_ironic_node(server_hardware_info):
    if (service_manager.is_nova_flavor_available(server_hardware_info)):
        LOG.debug('There is a flavor available for server hardware '
                  '%(server_hardware)s',
                  {'server_hardware': server_hardware_info.get('name')})

        node = create_ironic_node(
            server_hardware_info=server_hardware_info
        )

        LOG.debug('Node %(node)s created', {'node': node})

        service_manager.update_ironic_node_state(
            node, server_hardware_info.get('server_hardware_uri')
        )
        is_server_hardware_available = server_hardware_info.get(
            'server_profile_uri') is not None
        if is_server_hardware_available:
            LOG.debug('Server hardware %(server_hardware)s has a '
                      'server profile',
                      {'server_hardware': server_hardware_info.get('name')})
            LOG.info('Setting server hardware %(server_hardware)s to '
                     'maintenance mode',
                     {'server_hardware': server_hardware_info.get('name')})
            service_manager.get_ironic_client().node.set_maintenance(
                node.uuid, "true", maint_reason=REASON
            )


def update_ironic_node_maintenance_state(server_hardware_info,
                                         ironic_node_list=None):
    if ironic_node_list is None:
        ironic_node_list = service_manager.get_ironic_node_list()
    for node in ironic_node_list:
        ironic_complete_node = service_manager.get_ironic_node(node.uuid)

        LOG.debug('Got node %(node_uuid)s from Ironic',
                 {'node_uuid': node.uuid})

        is_oneview_node = ironic_complete_node.driver in drivers
        if (is_oneview_node and
            (ironic_complete_node.extra["server_hardware_uri"] ==
            server_hardware_info.get("server_hardware_uri"))):
            LOG.info('Setting node %(node_uuid)s to maintenance '
                     'mode', {'node_uuid': node.uuid})

            has_server_profile_assigned = str(
                server_hardware_info.get(
                    'server_profile_uri') is not None).lower()
            if (ironic_complete_node.instance_uuid is None):
                try:
                    service_manager.node_set_maintenance(
                        node.uuid, has_server_profile_assigned,
                        maint_reason=REASON
                    )
                except Exception as ex:
                    LOG.error('Node locked by OneView: %s' % ex.message)


def delete_ironic_node(server_hardware_uri):
    nodes = service_manager.get_ironic_client().node.list(detail=True)
    for node in nodes:
        LOG.debug('Node %(node_uuid)s using driver %(driver)s',
                      {'node_uuid': node.uuid, 'driver': node.driver})
        if node.driver in drivers:
            node_server_hardware_uri = node.extra.get("server_hardware_uri")
            if (server_hardware_uri == node_server_hardware_uri):
                service_manager.get_ironic_client().node.delete(node.uuid)


def get_ironic_node_by_server_hardware_uri(server_hardware_uri):
    nodes = service_manager.get_ironic_client().node.list(detail=True)
    for node in nodes:
        LOG.debug('Node %(node_uuid)s using driver %(driver)s',
                      {'node_uuid': node.uuid, 'driver': node.driver})
        if node.driver in drivers:
            node_server_hardware_uri = node.extra.get("server_hardware_uri")
            if (server_hardware_uri == node_server_hardware_uri):
                return node
    return None


def update_ironic_nodes_maintenance_state():
    old_server_hardwares = _get_old_ov_server_hardwares()
    for server_hardware in old_server_hardwares:
        server_hardware_info = service_manager.parse_server_hardware_to_dict(
                                    server_hardware)
        update_ironic_node_maintenance_state(server_hardware_info)


def sync_ironic_nodes():
    routing_key = "scmb.server-hardware.Updated.#"
    rabbitmq = rabbitmq_client.RabbitClient()
    rabbitmq.subscribe_to_queue(routing_key, callback_test)
    pass


def callback_test(ch, method, properties, body):
    body = json.loads(body)
    new_state = body.get('newState')
    prior_state = body.get('data').get('priorState')
    change_type = body.get('changeType')
    resource_uri = body.get('resource').get('uri')
    if new_state == 'Adding' and prior_state == 'Adding':
       LOG.info('ADDED %s ' % resource_uri)
       server_hardware = service_manager.get_server_hardware(resource_uri)
       server_hardware_info = service_manager.parse_server_hardware_to_dict(
                                  server_hardware)
       server_hardware_node = get_ironic_node_by_server_hardware_uri(
                                  resource_uri)
       if server_hardware_node is None:
           try:
               create_server_hardware_as_ironic_node(server_hardware_info)
           except Exception as ex:
               LOG.error(ex.message)
    elif new_state == 'Removing' and prior_state == 'Removing':
       LOG.info('REMOVED %s ' % resource_uri)
       delete_ironic_node(resource_uri)
    elif new_state == 'ProfileApplied' and prior_state == 'ProfileApplied':
       LOG.info('ServerProfile APPLIED to %s' % resource_uri)
       server_hardware = service_manager.get_server_hardware(resource_uri)
       server_hardware_info = service_manager.parse_server_hardware_to_dict(
                                  server_hardware)
       update_ironic_node_maintenance_state(server_hardware_info)
    elif new_state == 'NoProfileApplied' and prior_state == 'NoProfileApplied':
       LOG.info('ServerProfile REMOVED from %s' % resource_uri)
       server_hardware = service_manager.get_server_hardware(resource_uri)
       server_hardware_info = service_manager.parse_server_hardware_to_dict(
                                 server_hardware)
       update_ironic_node_maintenance_state(server_hardware_info)


if __name__ == '__main__':
    create_ironic_nodes()
    update_ironic_nodes_maintenance_state()
    sync_ironic_nodes()
