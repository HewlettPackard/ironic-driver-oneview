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

import logging

_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_loggers = {}


def _getHandler(filename, formatter):
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    return handler


def getLogger(name, servicename='service'):
    filename = servicename + '.log'
    if name not in _loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        logger.addHandler(_getHandler(filename=filename,
                                      formatter=_formatter))
        _loggers[name] = logger
    return _loggers[name]
