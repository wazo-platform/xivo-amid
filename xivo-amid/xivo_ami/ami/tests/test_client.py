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
from hamcrest import assert_that, not_none
from mock import Mock, patch

from xivo_ami.ami.client import AMIClient


class TestAMIClient(unittest.TestCase):

    def setUp(self):
        self.hostname = 'example.org'
        self.username = 'username'
        self.password = 'password'
        self.ami_client = AMIClient(self.hostname, self.username, self.password)
        self.sock = Mock()
        self.ami_client._sock = self.sock

    def _new_mocked_amiclient(self, action_id, lines):
        ami_client = AMIClient(self.hostname, self.username, self.password)
        ami_client._sock = Mock()
        ami_client._sock.recv.return_value = '\r\n'.join(lines) + '\r\n'
        return ami_client

    @patch('socket.socket')
    def test_when_connect_socket_then_socket_created(self, socket_mock):
        ami_client = AMIClient(self.hostname, self.username, self.password)
        socket_mock.return_value = Mock()

        ami_client._connect_socket()

        assert_that(ami_client._sock, not_none())

    @patch('socket.socket')
    def test_when_connect_and_login_twice_then_only_one_socket_is_created(self, mock_socket_constructor):
        ami_client = AMIClient(self.hostname, self.username, self.password)

        ami_client.connect_and_login()
        ami_client.connect_and_login()

        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

    @patch('socket.socket')
    def when_connect_and_login_then_login_data_sent_to_socket(self, mock_socket_constructor):
        ami_client = AMIClient(self.hostname, self.username, self.password)
        mock_socket = mock_socket_constructor.return_value
        lines = ['Action: Login',
                 'Username: %s' % self.username,
                 'Secret: %s' % self.password,
                 '\r\n']
        expected_data = '\r\n'.join(lines).encode('UTF-8')

        ami_client.connect_and_login()

        mock_socket.sendall.assert_called_once_with(expected_data)

    def test_given_not_connected_when_disconnect_then_no_error(self):
        ami_client = AMIClient(self.hostname, self.username, self.password)

        ami_client.disconnect()

    @patch('socket.socket')
    def test_given_connected_when_disconnect_then_socket_closed(self, mock_socket_constructor):
        mock_socket = mock_socket_constructor.return_value
        ami_client = AMIClient(self.hostname, self.username, self.password)
        ami_client.connect_and_login()

        ami_client.disconnect()

        mock_socket.close.assert_called_once_with()

    @patch('socket.socket')
    def test_given_connected_when_disconnect_twice_then_socket_closed_only_once(self, mock_socket_constructor):
        mock_socket = mock_socket_constructor.return_value
        ami_client = AMIClient(self.hostname, self.username, self.password)
        ami_client.connect_and_login()

        ami_client.disconnect()
        ami_client.disconnect()

        mock_socket.close.assert_called_once_with()

    def test_given_no_msg_on_queue_when_parse_next_messages_then_add_data_and_parse_msgs(self):
        self.ami_client._add_data_to_buffer = Mock()
        self.ami_client._parse_buffer = Mock()

        self.ami_client.parse_next_messages()

        self.ami_client._add_data_to_buffer.assert_called_once_with()
        self.ami_client._parse_buffer.assert_called_once_with()

    def test_given_data_on_socket_when_add_data_to_buffer_then_buffer_filled(self):
        ami_client = self._new_mocked_amiclient(None, [
            'Event: ExtensionStatus',
            ''
        ])

        ami_client._add_data_to_buffer()

        self.assertEqual('Event: ExtensionStatus\r\n\r\n', ami_client._buffer)

    def test_given_non_empty_buffer_when_parse_buffer_then_msgs_added_to_queue(self):
        self.ami_client._buffer = 'Event: ExtensionStatus\r\n\r\n'
        queue = self.ami_client._parse_buffer()

        self.assertEqual(1, len(queue))
        self.assertEqual('ExtensionStatus', queue[0].name)
