# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import socket
import unittest

from functools import wraps
from hamcrest import (
    assert_that,
    empty,
    equal_to,
    instance_of,
)
from mock import Mock, patch
from mock import sentinel

from wazo_amid.ami.client import AMIClient, AMIConnectionError


class patch_return_value:
    def __init__(self, patched, *mock_args, **mock_kwargs):
        self.patched = patched
        self.mock_args = mock_args
        self.mock_kwargs = mock_kwargs

    def __call__(self, wrapped):
        @wraps(wrapped)
        def wrapper(*wrapped_args, **wrapped_kwargs):
            with patch(self.patched) as patched:
                patched.return_value = Mock(*self.mock_args,
                                            **self.mock_kwargs)
                wrapped_args = list(wrapped_args)
                wrapped_args.insert(1, patched.return_value)  # insert after self
                wrapped(*wrapped_args, **wrapped_kwargs)
        return wrapper


class TestAMIClient(unittest.TestCase):

    def setUp(self):
        self.hostname = 'example.org'
        self.username = 'username'
        self.password = 'password'
        self.port = sentinel.port
        self.ami_client = AMIClient(self.hostname, self.username, self.password, self.port)

    @patch('socket.socket')
    def test_when_connect_socket_then_socket_created(self, mock_socket_constructor):
        self.ami_client.connect_and_login()

        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

    @patch('socket.socket')
    def test_when_connect_and_login_twice_then_only_one_socket_is_created(self, mock_socket_constructor):
        self.ami_client.connect_and_login()
        self.ami_client.connect_and_login()

        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

    @patch_return_value('socket.socket')
    def test_when_connect_and_login_then_login_data_sent_to_socket(self, mock_socket):
        lines = ['Action: Login',
                 'Username: %s' % self.username,
                 'Secret: %s' % self.password,
                 '\r\n']
        expected_data = '\r\n'.join(lines).encode('UTF-8')

        self.ami_client.connect_and_login()

        mock_socket.sendall.assert_called_once_with(expected_data)

    @patch_return_value('socket.socket')
    def test_given_recv_socket_error_when_connect_and_login_then_amiconnectionerror_raised(self, mock_socket):
        mock_socket.sendall.side_effect = socket.error

        self.assertRaises(AMIConnectionError, self.ami_client.connect_and_login)

    @patch_return_value('socket.socket')
    def test_given_send_socket_error_when_connect_and_login_then_amiconnectionerror_raised(self, mock_socket):
        mock_socket.recv.side_effect = socket.error

        self.assertRaises(AMIConnectionError, self.ami_client.connect_and_login)

    def test_given_not_connected_when_disconnect_then_no_error(self):
        self.ami_client.disconnect()

    @patch_return_value('socket.socket')
    def test_given_connected_when_disconnect_then_socket_closed(self, mock_socket):
        self.ami_client.connect_and_login()

        self.ami_client.disconnect()

        mock_socket.close.assert_called_once_with()

    @patch_return_value('socket.socket')
    def test_given_connected_when_disconnect_twice_then_socket_closed_only_once(self, mock_socket):
        self.ami_client.connect_and_login()

        self.ami_client.disconnect()
        self.ami_client.disconnect()

        mock_socket.close.assert_called_once_with()

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_complete_message_when_parse_next_messages_then_return_messages_queue(self, mock_socket):
        data = b'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'
        mock_socket.recv.return_value = data
        self.ami_client.connect_and_login()

        messages = self.ami_client.parse_next_messages()

        assert_that(len(messages), equal_to(1))
        self.assertEqual('foo', messages[0].name)

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_incomplete_message_when_parse_next_messages_then_return_empty_queue(self, mock_socket):
        self.ami_client.connect_and_login()
        mock_socket.recv.return_value = b'incomplete'

        messages = self.ami_client.parse_next_messages()

        assert_that(len(messages), equal_to(0))

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_remaining_message_when_parse_next_messages_then_return_messages_queue(self, mock_socket):
        self.ami_client.connect_and_login()
        self.ami_client._buffer = b'Event: '
        mock_socket.recv.return_value = b'complete\r\n\r\ndata\r\n\r\n'

        messages = self.ami_client.parse_next_messages()

        assert_that(len(messages), equal_to(1))
        self.assertEqual('complete', messages[0].name)

    @patch_return_value('socket.socket')
    def test_given_non_utf8_message_when_parse_next_messages_then_return_str_messages(self, mock_socket):
        self.ami_client.connect_and_login()
        mock_socket.recv.return_value = b'Event: complete\r\ndata: \xE9\r\n\r\n'

        messages = self.ami_client.parse_next_messages()

        assert_that(messages[0].headers['data'], instance_of(str))

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_recv_socket_error_when_parse_next_messages_then_raise_amiconnectionerror(self, mock_socket):
        self.ami_client.connect_and_login()
        mock_socket.recv.side_effect = socket.error

        self.assertRaises(AMIConnectionError, self.ami_client.parse_next_messages)

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_socket_recv_nothing_when_parse_next_message_then_raise_amiconnectionerror(self, mock_socket):
        self.ami_client.connect_and_login()
        mock_socket.recv.return_value = b''

        self.assertRaises(AMIConnectionError, self.ami_client.parse_next_messages)

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_stopping_and_socket_recv_nothing_when_parse_next_message_then_return_nothing(self, mock_socket):
        self.ami_client.connect_and_login()
        self.ami_client.stopping = True

        mock_socket.recv.return_value = b''

        assert_that(self.ami_client.parse_next_messages(), empty())

    @patch_return_value('socket.socket')
    def test_when_stop_then_socket_shutdown(self, mock_socket):
        self.ami_client.connect_and_login()

        self.ami_client.stop()

        mock_socket.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        mock_socket.close.assert_called_once_with()
