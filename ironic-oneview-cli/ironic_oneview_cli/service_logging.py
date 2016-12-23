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


def _getHandler(formatter):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    return handler


def getLogger(name):
    if name not in _loggers:
        set_logger(name)
    return _loggers[name]


def debug_activate_handlers(debug_activate):
    for logger_name, logger in _loggers.iteritems():
        logger.handlers = []
        set_logger(logger_name, debug_activate)


def set_logger(name, debug_activate=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not debug_activate:
        logger.disabled = True
        logger.propagate = False
    else:
        logger.disabled = False
        logger.propagate = True

    logger.addHandler(_getHandler(formatter=_formatter))
    _loggers[name] = logger
