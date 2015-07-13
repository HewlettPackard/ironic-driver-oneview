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

from oslo_config import cfg
from oslo_config import types
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class IronicConfClient:

    def __init__(self):
        self._CONF = self._get_ironic_conf()


    def _get_ironic_conf(self):
        opts = [
        cfg.StrOpt('default_deploy_kernel_id',
                   help='Deploy Kernel to be used by default'),
        cfg.StrOpt('default_deploy_ramdisk_id',
                   help='Deploy Ramdisk to be used by default'),
        cfg.StrOpt('default_sync_driver',
                   help='Sync Driver to be used by default'),
        cfg.StrOpt('auth_uri',
                   help='Keystone uri'),
        ]
        CONF = cfg.CONF
        try:
            CONF.register_opts(opts, group='ironic')
            CONF(default_config_files=['sync.conf'])
        except cfg.DuplicateOptError:
            LOG.warning('Duplicated configuration on oslo. Is Ironic running?')
        return CONF.ironic


    def get_default_deploy_kernel_id(self):
        return self._CONF.default_deploy_kernel_id


    def get_default_deploy_ramdisk_id(self):
        return self._CONF.default_deploy_ramdisk_id


    def get_default_sync_driver(self):
        return self._CONF.default_sync_driver


class KeystoneConfClient:

    def __init__(self):
        self._CONF = self._get_keystone_conf()


    def _get_keystone_conf(self):
        opts = [
        cfg.StrOpt('admin_tenant_name',
                   help='Keystone tenant to be used'),
        cfg.StrOpt('admin_password',
                   help='Keystone password to be used'),
        cfg.StrOpt('admin_user',
                   help='Keystone user to be used'),
        cfg.StrOpt('auth_uri',
                   help='Keystone uri'),
        ]
        CONF = cfg.CONF
        try:
            CONF.register_opts(opts, group='keystone_authtoken')
            CONF(default_config_files=['sync.conf'])
        except cfg.DuplicateOptError:
            LOG.warning('Duplicated configuration on oslo. Is Ironic running?')
        return CONF.keystone_authtoken


    def get_admin_tenant_name(self):
        return self._CONF.admin_tenant_name


    def get_admin_password(self):
        return self._CONF.admin_password


    def get_admin_user(self):
        return self._CONF.admin_user


    def get_auth_uri(self):
        return self._CONF.auth_uri


class NovaConfClient:

    def __init__(self):
        self._CONF = self._get_nova_conf()


    def _get_nova_conf(self):
        opts = [
        cfg.StrOpt('username',
                   help='Nova username to be used'),
        cfg.StrOpt('user_pass',
                   help='Nova password to be used'),
        cfg.StrOpt('user_tenant',
                   help='Nova tenant to be used'),
        ]
        CONF = cfg.CONF
        try:
            CONF.register_opts(opts, group='nova')
            CONF(default_config_files=['sync.conf'])
        except cfg.DuplicateOptError:
            LOG.warning('Duplicated configuration on oslo. Is Ironic running?')
        return CONF.nova


    def get_username(self):
        return self._CONF.username


    def get_user_pass(self):
        return self._CONF.user_pass


    def get_user_tenant(self):
        return self._CONF.user_tenant


class OneViewConfClient:

    def __init__(self):
        self._CONF = self._get_oneview_conf()


    def _get_oneview_conf(self):
        opts = [
        cfg.StrOpt('manager_url',
                   help='URL where OneView is available'),
        cfg.StrOpt('username',
                   help='OneView username to be used'),
        cfg.StrOpt('password',
                   help='OneView password to be used'),
        cfg.Opt('allow_insecure_connections',
                type=types.Boolean(),
                default=False,
                help='Option to allow insecure conection with OneView'),
        cfg.StrOpt('tls_cacert_file',
                   default=None,
                   help='Path to CA certificate'),
        ]
        CONF = cfg.CONF
        CONF.register_opts(opts, group='oneview')
        CONF(default_config_files=['sync.conf'])
        return CONF.oneview


    def get_manager_url(self):
        return self._CONF.manager_url


    def get_username(self):
        return self._CONF.username


    def get_password(self):
        return self._CONF.password


    def get_allow_insecure_connections(self):
        return self._CONF.allow_insecure_connections


    def get_tls_cacert_file(self):
        return self._CONF.tls_cacert_file


    def get_hostname(self):
        return self.get_manager_url().split('//')[1]


class RabbitMQConfClient:

    def __init__(self):
        self._CONF = self._get_rabbit_conf()


    def _get_rabbit_conf(self):
        opts = [
        cfg.StrOpt('ca_filename',
                   default='oneview_ca.pem',
                   help='OneView CA file'),
        cfg.StrOpt('certificate_filename',
                   default='oneview_certificate.pem',
                   help='OneView certificate file'),
        cfg.StrOpt('key_filename',
                   default='oneview_key.pem',
                   help='OneView private key file'),
        ]
        CONF = cfg.CONF
        CONF.register_opts(opts, group='rabbitmq')
        CONF(default_config_files=['sync.conf'])
        return CONF.rabbitmq


    def get_ca_filename(self):
        return self._CONF.ca_filename


    def get_cert_filename(self):
        return self._CONF.certificate_filename


    def get_key_filename(self):
        return self._CONF.key_filename


class ConfClient:

    def __init__(self):
        self.oneview = OneViewConfClient()
        self.nova = NovaConfClient()
        self.keystone = KeystoneConfClient()
        self.ironic = IronicConfClient()
        self.rabbitmq = RabbitMQConfClient()
