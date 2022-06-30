# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import socket
import time

from amqp.exceptions import AMQPError
from kombu import Connection, Exchange, Producer

from xivo.status import Status
from xivo_bus import Marshaler
from xivo_bus import LongLivedPublisher
from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


class BusUnreachable(Exception):
    def __init__(self, bus_config):
        bus_url = (
            f"amqp://"
            f"{bus_config['username']}"
            f":******"
            f"@{bus_config['host']}"
            f":{bus_config['port']}//")
        super().__init__(f'Message bus unreachable on {bus_url}... stopping')
        self.bus_config = bus_config


class BusClient:
    def __init__(self, config):
        self._publisher = self._new_publisher_or_timeout(
            config)

    def _new_publisher_or_timeout(self, config):
        connection_tries = config['bus']['startup_connection_tries']
        connection_delay = config['bus']['startup_connection_delay']
        for _ in range(connection_tries):
            try:
                return self._new_publisher(config)
            except (AMQPError, socket.error) as e:
                logger.info(
                    'Error connecting to message bus (%s), '
                    'retrying in %s seconds...',
                    e,
                    connection_delay,
                )
                time.sleep(connection_delay)
                continue
        raise BusUnreachable(config['bus'])

    def _new_publisher(self, config)->LongLivedPublisher:
        bus_url = (
            f"amqp://"
            f"{config['bus']['username']}"
            f":{config['bus']['password']}"
            f"@{config['bus']['host']}"
            f":{config['bus']['port']}//")
        bus_connection = Connection(bus_url)
        bus_exchange = Exchange(
            config['bus']['exchange_name'], type=config['bus']['exchange_type']
        )
        bus_producer = Producer(
            bus_connection, exchange=bus_exchange, auto_declare=True
        )
        bus_marshaler = Marshaler(config['uuid'])
        return LongLivedPublisher(bus_producer, bus_marshaler)

    def publish(self, message):
        ami_event = AMIEvent(message.name, message.headers)
        self._publisher.publish(ami_event)

    def provide_status(self, status):
        status['bus_publisher']['status'] = (
            Status.ok if self._publisher.is_connected() else Status.fail
        )
