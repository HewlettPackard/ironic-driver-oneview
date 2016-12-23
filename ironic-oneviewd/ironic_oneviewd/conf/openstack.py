# Copyright 2016 Hewlett Packard Enterprise Development LP.
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

from oslo_config import cfg

CONF = cfg.CONF

opts = [
    cfg.StrOpt('auth_url',
               help='Authentication URL for OpenStack services.'),
    cfg.StrOpt('username',
               help='Name of the OpenStack user.'),
    cfg.StrOpt('password',
               secret=True,
               help='OpenStack user password.'),
    cfg.StrOpt('region_name',
               help='Name of the OpenStack Keystone region.'),
    cfg.BoolOpt('insecure',
                default=False,
                help='Allow insecure SSL (no cert verification).'),
    cfg.StrOpt('cacert',
               help='(Optional) Path to CA certificate bundle file.'),
    cfg.StrOpt('cert',
               help='(Optional) Path to cert file.'),
    cfg.StrOpt('deploy_kernel_id',
               help='Ironic deploy kernel image uuid.'),
    cfg.StrOpt('deploy_ramdisk_id',
               help='Ironic deploy remdisk image uuid.'),
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help='(Optional) OpenStack endpoint type.'),
    cfg.StrOpt('ironic_driver',
               choices=['iscsi_pxe_oneview, agent_pxe_oneview, fake_oneview'],
               help='Ironic OneView driver for node create. '),
    cfg.StrOpt('tenant_id',
               help='ID of the OpenStack tenant. '
                    '(deprecated in favour of project_id)'),
    cfg.StrOpt('tenant_name',
               help='Name of the OpenStack tenant. '
                    '(deprecated in favour of project_name)'),
    cfg.StrOpt('project_id',
               help='ID of the OpenStack project.'),
    cfg.StrOpt('project_name',
               help='Name of the OpenStack project.'),
    cfg.StrOpt('user_domain_id',
               help='ID of a domain the user belongs to.'),
    cfg.StrOpt('user_domain_name',
               help='Name of a domain the user belongs to.'),
    cfg.StrOpt('project_domain_id',
               help='ID of a domain the project belongs to.'),
    cfg.StrOpt('project_domain_name',
               help='ID of a domain the project belongs to.'),
    cfg.BoolOpt('inspection_enabled',
                default=False,
                help='Run inspection on nodes when any hardware property is '
                     'missing.')
]


def register_opts(conf):
    conf.register_opts(opts, group='openstack')
