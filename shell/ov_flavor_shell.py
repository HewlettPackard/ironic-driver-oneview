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
Command-line interface to the OneView Sync.
"""

from __future__ import print_function

import argparse
import getpass
import logging
import sys
import six

from os import environ
from ironicclient.common import utils
from ironicclient.openstack.common import cliutils
from novaclient.client import Client
from oslo_utils import encodeutils

import oneviewclient
import commands



# TODO(Afaranha) Put this information on the client, not the shell.
VERSION = '1.0'

COMMAND_MODULES = [
    commands
]

class OneViewSyncShell(object):
    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='ov-flavor',
            description=__doc__.strip(),
            epilog='See "ov-flavor help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=HelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS,
                            )

        parser.add_argument('--version',
                            action='version',
                            version=VERSION)

        parser.add_argument('--os-tenant-name',
                            default=environ.get('OS_TENANT_NAME'),
                            help='Defaults to env[OS_TENANT_NAME]')

        parser.add_argument('--os-username',
                            default=environ.get('OS_USERNAME'),
                            help='Defaults to env[OS_USERNAME]')

        parser.add_argument('--os-password',
                            default=environ.get('OS_PASSWORD'),
                            help='Defaults to env[OS_PASSWORD]')

        parser.add_argument('--os-auth-url',
                            default=environ.get('OS_AUTH_URL'),
                            help='Defaults to env[OS_AUTH_URL]')

        parser.add_argument('--ov-username',
                            default=environ.get('OV_USERNAME'),
                            help='Defaults to env[OV_USERNAME]')

        parser.add_argument('--ov-password',
                            default=environ.get('OV_PASSWORD'),
                            help='Defaults to env[OV_PASSWORD]')

        parser.add_argument('--ov-address',
                            default=environ.get('OV_ADDRESS'),
                            help='Defaults to env[OV_ADDRESS]')

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()
        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        # submodule = utils.import_versioned_module(version, 'shell')
        enhance_parser(parser, subparsers, self.subcommands)
        utils.define_commands_from_module(subparsers, self, self.subcommands)
        return parser

    def main(self, argv):
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        subcommand_parser = self.get_subcommand_parser(1)
        self.parser = subcommand_parser

        if options.help or not argv:
            self.do_help(options)
            return 0

        args = subcommand_parser.parse_args(argv)
        # Short-circuit and deal with these commands right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0

        client = oneviewclient.Client(address=args.ov_address,
                                      username=args.ov_username,
                                      password=args.ov_password)
        novaclient = Client(2,
                            args.os_username,
                            args.os_password,
                            args.os_tenant_name,
                            args.os_auth_url)

        args.func(client, novaclient, args)

    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError(_("'%s' is not a valid subcommand") %
                                       args.command)
        else:
            self.parser.print_help()

def enhance_parser(parser, subparsers, cmd_mapper):
    for command_module in COMMAND_MODULES:
         utils.define_commands_from_module(subparsers, command_module,
                                           cmd_mapper)

class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)

def main():
    try:
        OneViewSyncShell().main(sys.argv[1:])
    except KeyboardInterrupt:
        print("... terminating ironic client", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(encodeutils.safe_encode(six.text_type(e)), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
