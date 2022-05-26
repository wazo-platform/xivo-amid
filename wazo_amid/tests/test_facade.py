# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import unittest
from unittest.mock import (
    ANY,
    call,
    Mock,
    patch,
    sentinel,
)

from hamcrest import assert_that, contains, equal_to

from wazo_amid.ami.client import AMIClient, AMIConnectionError
from wazo_amid.bus.client import BusClient
from wazo_amid.facade import EventHandlerFacade

RECONNECTION_DELAY = 5


class testEventHandlerFacade(unittest.TestCase):
    @patch('threading.Event')
    @patch('collections.deque')
    def setUp(self, deque_mock, event_mock):
        self.deque_mock = deque_mock
        self.queue = self.deque_mock.return_value = Mock()

        self.event_mock = event_mock
        self.event_set = False

        def is_set_fn():
            return self.event_set

        def set_fn():
            self.event_set = True

        self.event_wait = Mock()
        self.event_mock.return_value = Mock(
            set=set_fn, is_set=is_set_fn, wait=self.event_wait
        )

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

        self.ami_client_mock.disconnect.assert_called_once_with(reason=ANY)

    def test_given_ami_connection_error_when_run_then_ami_reconnect(self):
        self.ami_client_mock.connect_and_login.side_effect = [
            AMIConnectionError(),
            None,
        ]

        self.assertRaises(Exception, self.facade.run)

        self.event_wait.assert_called_once_with(timeout=RECONNECTION_DELAY)
        assert_that(self.ami_client_mock.disconnect.call_count, equal_to(2))
        assert_that(self.ami_client_mock.connect_and_login.call_count, equal_to(2))

    def test_given_ami_connection_error_when_run_then_new_messages_processed(self):
        self.ami_client_mock.connect_and_login.side_effect = [
            AMIConnectionError(),
            None,
        ]

        self.ami_client_mock.parse_next_messages.side_effect = [
            [sentinel.message],
            Exception(),
        ]

        self.assertRaises(Exception, self.facade.run)

        assert_that(self.bus_client_mock.publish.call_count, equal_to(1))
        self.bus_client_mock.publish.assert_any_call(sentinel.message)

    def test_given_multiple_messages_fetched_when_run_then_all_messages_orderly_processed(
        self,
    ):
        self.ami_client_mock.parse_next_messages.side_effect = [
            [sentinel.first_message],
            [sentinel.second_message],
            Exception(),
        ]
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

    def test_when_stop_then_ami_client_stop_is_called(self):
        self.facade.stop()

        self.ami_client_mock.stop.assert_called_once_with()
