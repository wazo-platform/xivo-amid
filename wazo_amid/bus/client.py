# Copyright 2012-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import socket
import time

from amqp.exceptions import AMQPError
from kombu import Connection, Exchange, Producer

from xivo_bus import Marshaler
from xivo_bus import LongLivedPublisher
from xivo_bus import PublishingQueue
from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


class BusUnreachable(Exception):
    def __init__(self, bus_config):
        bus_url = 'amqp://{username}:******@{host}:{port}//'.format(**bus_config)
        super().__init__('Message bus unreachable on {}... stopping'.format(bus_url))
        self.bus_config = bus_config


class BusPublisher:
    def __init__(self, config):
        self._config = config
        self._publisher = PublishingQueue(self._new_publisher_or_timeout)

    def run(self):
        self._publisher.run()

    def _new_publisher_or_timeout(self):
        connection_tries = self._config['bus']['startup_connection_tries']
        connection_delay = self._config['bus']['startup_connection_delay']
        for _ in range(connection_tries):
            try:
                return self._new_publisher()
            except (AMQPError, socket.error) as e:
                logger.info(
                    'Error connecting to message bus (%s), retrying in %s seconds...',
                    e,
                    connection_delay,
                )
                time.sleep(connection_delay)
                continue
        raise BusUnreachable(self._config['bus'])

    def _new_publisher(self):
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**self._config['bus'])
        bus_connection = Connection(bus_url)
        bus_exchange = Exchange(
            self._config['bus']['exchange_name'], type=self._config['bus']['exchange_type']
        )
        bus_producer = Producer(
            bus_connection, exchange=bus_exchange, auto_declare=True
        )
        bus_marshaler = Marshaler(self._config['uuid'])
        return LongLivedPublisher(bus_producer, bus_marshaler)

    def publish(self, message):
        ami_event = AMIEvent(message.name, message.headers)
        self._publisher.publish(ami_event)

    def stop(self):
        self._publisher.stop()
