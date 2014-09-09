# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


class BusClient(object):

    def __init__(self, bus_producer, bus_config):
        self._bus_producer = bus_producer
        self._config = bus_config

    def connect(self):
        logger.info('Connecting bus client')
        try:
            self._connect_and_declare_exchange()
        except IOError as e:
            logger.exception(e)
            raise BusConnectionError(e)

    def _connect_and_declare_exchange(self):
        if not self._bus_producer.connected:
            self._bus_producer.connect()
            self._bus_producer.declare_exchange(self._config.exchange_name,
                                                self._config.exchange_type,
                                                durable=self._config.exchange_durable)

    def disconnect(self):
        logger.info('Disconnecting bus client')
        self._bus_producer.close()

    def publish(self, message):
        event = AMIEvent(message.name, message.headers)
        try:
            self._bus_producer.publish_event(self._config.exchange_name, event.name, event)
        except IOError as e:
            logger.exception(e)
            raise BusConnectionError(e)


class BusConnectionError(Exception):
    pass
