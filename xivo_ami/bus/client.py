# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import socket
import time

from amqp.exceptions import AMQPError
from kombu import Connection, Exchange, Producer

from xivo_bus import Marshaler
from xivo_bus import Publisher
from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


class BusUnreachable(Exception):
    def __init__(self, bus_config):
        bus_url = 'amqp://{username}:******@{host}:{port}//'.format(**bus_config)
        super(BusUnreachable, self).__init__('Message bus unreachable on {}... stopping'.format(bus_url))
        self.bus_config = bus_config


class BusClient(object):

    def __init__(self, config):
        self._publisher = self._new_publisher_or_timeout(config)

    def _new_publisher_or_timeout(self, config):
        connection_tries = config['bus']['startup_connection_tries']
        connection_delay = config['bus']['startup_connection_delay']
        for _ in xrange(connection_tries):
            try:
                return self._new_publisher(config)
            except (AMQPError, socket.error) as e:
                logger.info('Error connecting to message bus (%s), retrying in %s seconds...', e, connection_delay)
                time.sleep(connection_delay)
                continue
        raise BusUnreachable(config['bus'])

    def _new_publisher(self, config):
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        bus_connection = Connection(bus_url)
        bus_exchange = Exchange(config['bus']['exchange_name'],
                                type=config['bus']['exchange_type'])
        bus_producer = Producer(bus_connection, exchange=bus_exchange, auto_declare=True)
        bus_marshaler = Marshaler(config['uuid'])
        return Publisher(bus_producer, bus_marshaler)

    def publish(self, message):
        ami_event = AMIEvent(message.name, message.headers)
        self._publisher.publish(ami_event)
