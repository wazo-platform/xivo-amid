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

import socket
import unittest
from functools import wraps
from hamcrest import assert_that, contains, equal_to
from mock import Mock, patch, sentinel

from xivo_ami.ami.client import AMIClient, AMIConnectionError


class patch_return_value(object):
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
        self.ami_client = AMIClient(self.hostname, self.username, self.password)

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

    @patch('xivo_ami.ami.parser.parse_msg', return_value=sentinel.msg_parsed)
    @patch_return_value('socket.socket')  # must be the last decorator
    def test_when_parse_next_messages_then_return_received_data_formatted(self, mock_socket, mock_parse):
        mock_socket.recv.return_value = "data\r\n\r\n"
        self.ami_client.connect_and_login()

        result = self.ami_client.parse_next_messages()

        mock_parse.assert_called_once_with('data')
        assert_that(result, contains(sentinel.msg_parsed))

    @patch('xivo_ami.ami.parser.parse_msg', side_effect=[sentinel.msg_parsed1, sentinel.msg_parsed2])
    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_incomplete_message_when_parse_next_messages_then_return_received_data_formatted(self, mock_socket, mock_parse):
        self.ami_client.connect_and_login()

        mock_socket.recv.return_value = 'incomplete'
        self.ami_client.parse_next_messages()
        mock_socket.recv.return_value = 'complete\r\n\r\ndata\r\n\r\n'
        result = self.ami_client.parse_next_messages()

        mock_parse.assert_any_call('incompletecomplete')
        mock_parse.assert_any_call('data')
        assert_that(mock_parse.call_count, equal_to(2))
        assert_that(result, contains(sentinel.msg_parsed1, sentinel.msg_parsed2))

    @patch('xivo_ami.ami.parser.parse_msg', side_effect=Exception)
    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_exception_during_parsing_when_parse_next_messages_then_skip_formatted_data(self, mock_socket, mock_parse):
        self.ami_client.connect_and_login()
        mock_socket.recv.return_value = 'invalid data\r\n\r\n'

        result = self.ami_client.parse_next_messages()

        assert_that(result, contains())

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_recv_socket_error_when_parse_next_message_then_raise_amiconnectionerror(self, mock_socket):
        self.ami_client.connect_and_login()
        mock_socket.recv.side_effect = socket.error

        self.assertRaises(AMIConnectionError, self.ami_client.parse_next_messages)

    @patch_return_value('socket.socket')  # must be the last decorator
    def test_given_socket_recv_nothing_when_parse_next_message_then_raise_amiconnectionerror(self, mock_socket):
        self.ami_client.connect_and_login()
        mock_socket.recv.return_value = ''

        self.assertRaises(AMIConnectionError, self.ami_client.parse_next_messages)
