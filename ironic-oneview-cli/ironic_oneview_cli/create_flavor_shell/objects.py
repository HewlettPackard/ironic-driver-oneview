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

import six


class Flavor(object):
    def __init__(self, id, info):
        self.id = id
        self._info = info
        self._add_details(info)

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                pass

    def extra_specs(self):
        extra_specs = {}

        extra_specs['cpu_arch'] = self.cpu_arch

        if hasattr(self, 'server_profile_template_uri'):
            extra_specs['capabilities:server_profile_template_uri'] = (
                self.server_profile_template_uri)
        if hasattr(self, 'server_hardware_type_uri'):
            extra_specs['capabilities:server_hardware_type_uri'] = (
                self.server_hardware_type_uri)
        if getattr(self, 'enclosure_group_uri'):
            extra_specs['capabilities:enclosure_group_uri'] = (
                self.enclosure_group_uri)
        return extra_specs

    def __repr__(self):
        return "<Flavor %s>" % self._info

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        for (k, v) in six.iteritems(self._info):
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __setitem__(self, id):
        self.id = id


class ServerProfile(object):
    def __init__(self, info):
        self._info = info
        self._add_details(info)

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                pass

    def __repr__(self):
        return "<ServerProfile %s>" % self._info
