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

from hamcrest import assert_that, equal_to
from mock import Mock
from mock import sentinel
import unittest

from xivo_ami.ami.client import Message
from xivo_ami.config import ConfigXivoAMId
from xivo_ami.bus.client import BusClient, BusConnectionError
from xivo_bus.ctl.producer import BusProducer


class TestBusClient(unittest.TestCase):

    def setUp(self):
        config = {'bus': {'exchange_name': sentinel.exchange,
                          'exchange_type': sentinel.topic,
                          'exchange_durable': sentinel.durable}}
        self.config = ConfigXivoAMId(config)
        self.mock_bus_producer = Mock(BusProducer, connected=False)
        self.bus_client = BusClient(self.mock_bus_producer, self.config.bus)

    def test_when_connect_then_connect_and_declare(self):
        self.bus_client.connect()

        self.mock_bus_producer.connect.assert_called_once_with()
        self.mock_bus_producer.declare_exchange.assert_called_once_with(
            sentinel.exchange,
            sentinel.topic,
            durable=sentinel.durable)

    def test_given_amqperror_when_connect_then_raise_busconnectionerror(self):
        self.mock_bus_producer.connect.side_effect = IOError()

        self.assertRaises(BusConnectionError, self.bus_client.connect)

    def test_given_connected_when_connect_then_nothing(self):
        self.mock_bus_producer.connected = True
        self.bus_client.connect()

        assert_that(self.mock_bus_producer.connect.call_count, equal_to(0))
        assert_that(self.mock_bus_producer.declare_exchange.call_count, equal_to(0))

    def test_when_disconnect_then_close(self):
        self.bus_client.disconnect()

        self.mock_bus_producer.close.assert_called_once_with()

    def test_when_publish_then_publish_event(self):
        name = 'EventName'
        headers = {'foo': 'bar', 'meaning of the universe': '42'}
        message = Message(name, headers)

        self.bus_client.publish(message)

        assert_that(self.mock_bus_producer.publish_event.call_count, equal_to(1))
        resulting_args = self.mock_bus_producer.publish_event.call_args[0]
        resulting_exchange, resulting_key, resulting_event = resulting_args
        assert_that(resulting_event.name, equal_to(name))
        assert_that(resulting_event.variables, equal_to(headers))
        assert_that(resulting_exchange, equal_to(sentinel.exchange))
        assert_that(resulting_key, equal_to('ami.{}'.format(resulting_event.name)))

    def test_given_amqperror_when_publish_then_raise_busconnectionerror(self):
        name = 'EventName'
        headers = {'foo': 'bar', 'meaning of the universe': '42'}
        message = Message(name, headers)
        self.mock_bus_producer.publish_event.side_effect = IOError()

        self.assertRaises(BusConnectionError, self.bus_client.publish, message)
