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
import ssl

import pika

import config_client
import oneview_client
import service_logging as logging

from oslo_config import cfg
from oslo_config import types


LOG = logging.getLogger(__name__)

ONEVIEW_MESSAGE_PORT = 5671


class RabbitClient:

    def __init__(self):
        self.oneview_client = oneview_client.OneViewClient()
        self.oneview_config = config_client.ConfClient().oneview
        self.rabbit_config = config_client.ConfClient().rabbitmq
        self._create_certificates()


    def _create_certificates(self):
        ca = self.oneview_client.certificate_api.get_ca()
        file_ca = open(self.rabbit_config.get_ca_filename(), 'w')
        file_ca.write(ca)
        file_ca.close()

        self.oneview_client.certificate_api.post_certificate()

        certificate = self.oneview_client.certificate_api.get_certificate()
        file_cert = open(self.rabbit_config.get_cert_filename(), 'w')
        file_cert.write(certificate)
        file_cert.close()

        key = self.oneview_client.certificate_api.get_key()
        file_key = open(self.rabbit_config.get_key_filename(), 'w')
        file_key.write(key)
        file_key.close()


    def subscribe_to_queue(self, routing_key , callback):
        ssl_options = ({'ca_certs': self.rabbit_config.get_ca_filename(),
                        'certfile': self.rabbit_config.get_cert_filename(),
                        'keyfile': self.rabbit_config.get_key_filename(),
                        'cert_reqs': ssl.CERT_REQUIRED,
                        'server_side': False})

        hostname = self.oneview_config.get_hostname()
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=hostname, port=ONEVIEW_MESSAGE_PORT,
                credentials=pika.credentials.ExternalCredentials(), ssl=True,
                ssl_options=ssl_options))

        EXCHANGE_NAME = "scmb"

        channel = connection.channel()
        result = channel.queue_declare()
        queue_name = result.method.queue


        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name,
            routing_key=routing_key)
        LOG.debug('Queue binded to exchange %(exchange)s and routing '
                  'key %(routing_key)s',
                  {'exchange': EXCHANGE_NAME, 'routing_key': routing_key})

        channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()


def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)


if __name__ == '__main__':
    rabbit = RabbitClient()
    rabbit.subscribe_to_queue("scmb.server-hardware.#", callback)
