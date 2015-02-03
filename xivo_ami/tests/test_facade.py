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

import collections
from hamcrest import assert_that, contains, equal_to
from mock import call, Mock, patch, sentinel
import unittest

from xivo_ami.ami.client import AMIClient, AMIConnectionError
from xivo_ami.bus.client import BusClient
from xivo_ami.facade import EventHandlerFacade

RECONNECTION_DELAY = 5


class testEventHandlerFacade(unittest.TestCase):

    @patch('collections.deque')
    def setUp(self, deque_mock):
        self.deque_mock = deque_mock
        self.queue = self.deque_mock.return_value = Mock()

        self.bus_client_mock = Mock(BusClient)

        self.ami_client_mock = Mock(AMIClient)
        self.ami_client_mock.parse_next_messages.side_effect = [Exception()]

        self.facade = EventHandlerFacade(self.ami_client_mock, self.bus_client_mock)

    def test_when_run_then_ami_client_connect_and_login(self):
        self.assertRaises(Exception, self.facade.run)

        self.ami_client_mock.connect_and_login.assert_called_once_with()

    def test_given_unexpected_error_when_run_then_stop(self):
        self.ami_client_mock.connect_and_login.side_effect = Exception()

        self.assertRaises(Exception, self.facade.run)

        self.ami_client_mock.disconnect.assert_called_once_with()

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

        self.ami_client_mock.parse_next_messages.side_effect = [[sentinel.message], Exception()]

        self.assertRaises(Exception, self.facade.run)

        assert_that(self.bus_client_mock.publish.call_count, equal_to(1))
        self.bus_client_mock.publish.assert_any_call(sentinel.message)

    def test_given_multiple_messages_fetched_when_run_then_all_messages_orderly_processed(self):
        self.ami_client_mock.parse_next_messages.side_effect = [[sentinel.first_message],
                                                                [sentinel.second_message],
                                                                Exception()]
        expected_calls = [call(sentinel.first_message), call(sentinel.second_message)]

        self.assertRaises(Exception, self.facade.run)

        assert_that(self.ami_client_mock.parse_next_messages.call_count, equal_to(3))
        mock_calls = self.bus_client_mock.publish.mock_calls
        assert_that(mock_calls, contains(*expected_calls))

    def test_given_events_in_queue_when_process_messages_then_queue_is_emptied(self):
        queue = collections.deque()
        queue.append(sentinel.event1)
        queue.append(sentinel.event2)

        self.facade._process_messages(queue)

        self.assertFalse(queue)
