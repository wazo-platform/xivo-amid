# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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
from mock import Mock, patch, sentinel
import unittest

from xivo_ami.facade import EventHandlerFacade
from xivo_ami.ami.client import AMIClient, AMIConnectionError
from xivo_ami.bus.client import BusClient, BusConnectionError

RECONNECTION_DELAY = 5


class testEventHandlerFacade(unittest.TestCase):

    @patch('collections.deque')
    def setUp(self, deque_mock):
        self.deque_mock = deque_mock
        self.queue = self.deque_mock.return_value = Mock()

        self.bus_client_mock = Mock(BusClient)

        self.ami_client_mock = Mock(AMIClient)
        self.ami_client_mock.parse_next_messages.side_effect = [Exception()]

        self.event_handler_callback = Mock()
        self.facade = EventHandlerFacade(self.ami_client_mock, self.bus_client_mock, self.event_handler_callback)

    def test_when_run_then_ami_client_connect_and_login(self):
        self.assertRaises(Exception, self.facade.run)

        self.ami_client_mock.connect_and_login.assert_called_once_with()

    @patch('time.sleep')
    def test_given_ami_connection_error_when_run_then_ami_reconnect(self, sleep_mock):
        self.ami_client_mock.connect_and_login.side_effect = [AMIConnectionError(), None]

        self.assertRaises(Exception, self.facade.run)

        sleep_mock.assert_called_once_with(RECONNECTION_DELAY)
        assert_that(self.ami_client_mock.disconnect.call_count, equal_to(2))
        assert_that(self.ami_client_mock.connect_and_login.call_count, equal_to(2))

    @patch('time.sleep')
    def test_given_ami_connection_error_when_run_then_new_messages_processed(self, sleep_mock):
        self.ami_client_mock.connect_and_login.side_effect = [AMIConnectionError(), None]

        first_msgs = sentinel.first_msgs
        second_msgs = sentinel.second_msgs
        self.ami_client_mock.parse_next_messages.side_effect = [first_msgs, second_msgs, Exception()]

        self.assertRaises(Exception, self.facade.run)

        assert_that(self.ami_client_mock.disconnect.call_count, equal_to(2))
        sleep_mock.assert_called_once_with(RECONNECTION_DELAY)
        assert_that(self.ami_client_mock.connect_and_login.call_count, equal_to(2))

        assert_that(self.ami_client_mock.parse_next_messages.call_count, equal_to(3))
        assert_that(self.event_handler_callback.call_count, equal_to(2))
        self.event_handler_callback.assert_any_call(second_msgs)
        self.event_handler_callback.assert_any_call(first_msgs)

    @patch('time.sleep')
    def test_given_bus_connection_error_when_run_then_bus_reconnect(self, sleep_mock):
        self.bus_client_mock.connect.side_effect = [BusConnectionError(), None]

        self.assertRaises(Exception, self.facade.run)

        self.bus_client_mock.disconnect.assert_called_once_with()
        sleep_mock.assert_called_once_with(RECONNECTION_DELAY)
        assert_that(self.bus_client_mock.connect.call_count, equal_to(2))

    def test_given_unexpected_error_when_run_then_stop(self):
        self.ami_client_mock.connect_and_login.side_effect = Exception()

        self.assertRaises(Exception, self.facade.run)

        self.ami_client_mock.disconnect.assert_called_once_with()

    def test_given_multiple_messages_fetched_when_run_then_all_messages_processed(self):
        first_msgs = sentinel.first_msgs
        second_msgs = sentinel.second_msgs
        self.ami_client_mock.parse_next_messages.side_effect = [first_msgs, second_msgs, Exception()]

        self.assertRaises(Exception, self.facade.run)

        assert_that(self.ami_client_mock.parse_next_messages.call_count, equal_to(3))
        assert_that(self.event_handler_callback.call_count, equal_to(2))
        self.event_handler_callback.assert_any_call(second_msgs)
        self.event_handler_callback.assert_any_call(first_msgs)
