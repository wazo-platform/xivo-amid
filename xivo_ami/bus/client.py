# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from kombu import Connection, Exchange, Producer

from xivo_bus import Marshaler
from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


class BusClient(object):

    def __init__(self, config):
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        bus_connection = Connection(bus_url)
        bus_exchange = Exchange(config['bus']['exchange_name'],
                                type=config['bus']['exchange_type'])
        bus_producer = Producer(bus_connection, exchange=bus_exchange, auto_declare=True)
        self._send_bus_msg = bus_connection.ensure(bus_producer, bus_producer.publish,
                                                   errback=self._on_bus_publish_error, max_retries=5,
                                                   interval_start=0)
        self._marshaler = Marshaler(config['uuid'])

    def publish(self, message):
        ami_event = AMIEvent(message.name, message.headers)
        msg = self._marshaler.marshal_message(ami_event)
        self._send_bus_msg(msg, routing_key=ami_event.routing_key)

    def _on_bus_publish_error(self, exc, interval):
        logger.error('Error: %s', exc, exc_info=1)
        logger.info('Retry in %s seconds...', interval)
