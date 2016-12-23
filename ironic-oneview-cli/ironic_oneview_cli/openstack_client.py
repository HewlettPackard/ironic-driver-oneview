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

from ironicclient import client as ironic_client
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as nova_client

IRONIC_API_VERSION = 1
NOVA_API_VERSION = 2


def get_ironic_client(args):
    cli_kwargs = {
        'ironic_url': args.ironic_url,
        'os_username': args.os_username,
        'os_password': args.os_password,
        'os_auth_url': args.os_auth_url,
        'os_project_id': args.os_project_id,
        'os_project_name': args.os_project_name,
        'os_tenant_name': args.os_tenant_name,
        'os_region_name': args.os_region_name,
        'os_service_type': args.os_service_type,
        'os_endpoint_type': args.os_endpoint_type,
        'insecure': args.insecure,
        'os_cacert': args.os_cacert,
        'os_cert': args.os_cert,
        'os_ironic_api_version': args.ironic_api_version,
        'os_project_domain_id': args.os_project_domain_id,
        'os_project_domain_name': args.os_project_domain_name,
        'os_user_domain_id': args.os_user_domain_id,
        'os_user_domain_name': args.os_user_domain_name
    }

    return ironic_client.get_client(IRONIC_API_VERSION, **cli_kwargs)


def get_nova_client(args):
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=args.os_auth_url,
        username=args.os_username,
        password=args.os_password,
        user_domain_id=args.os_user_domain_id,
        user_domain_name=args.os_user_domain_name,
        project_id=args.os_project_id or args.os_tenant_id,
        project_name=args.os_project_name or args.os_tenant_name,
        project_domain_id=args.os_project_domain_id,
        project_domain_name=args.os_project_domain_name
    )

    verify = True

    if args.insecure:
        verify = False

    elif args.os_cacert:
        verify = args.os_cacert

    sess = session.Session(auth=auth, verify=verify, cert=args.os_cert)
    nova = nova_client.Client(NOVA_API_VERSION, session=sess)

    return nova
