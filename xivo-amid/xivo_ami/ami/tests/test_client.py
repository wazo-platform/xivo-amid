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

from hamcrest import assert_that, not_none
from mock import Mock, patch
import unittest

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

    def test_given_socket_not_none_when_connect_and_login_then_nothing_happens(self):
        ami_client = self._new_mocked_amiclient(None, [
            'Event: ExtensionStatus',
            ''
        ])

        ami_client._connect_socket = Mock()
        ami_client._login = Mock()

        ami_client.connect_and_login()

        self.assertEqual(ami_client._connect_socket.call_count, 0)
        self.assertEqual(ami_client._login.call_count, 0)

    def test_given_socket_is_none_when_connect_and_login_then_connect_then_login(self):
        self.ami_client._connect_socket = Mock()
        self.ami_client._login = Mock()

        self.ami_client.connect_and_login()

        self.ami_client._connect_socket.assert_called_once_with()
        self.ami_client._login.assert_called_once_with()

    @patch('socket.socket')
    def test_when_connect_socket_then_socket_created(self, socket_mock):
        ami_client = AMIClient(self.hostname, self.username, self.password)
        socket_mock.return_value = Mock()

        ami_client._connect_socket()

        assert_that(ami_client._sock, not_none())

    @patch('socket.socket')
    def test_given_connected_socket_when_login_then_login_data_sent_to_socket(self, socket_mock):
        ami_client = AMIClient(self.hostname, self.username, self.password)
        socket_mock.return_value = Mock()
        ami_client._connect_socket()
        lines = ['Action: Login',
                 'Username: %s' % self.username,
                 'Secret: %s' % self.password,
                 '\r\n'
                 ]
        expected_data = '\r\n'.join(lines).encode('UTF-8')

        self.ami_client._login()

        self.ami_client._sock.sendall.assert_called_once_with(expected_data)

    def test_given_disconnect_when_after_init(self):
        self.ami_client.disconnect()

    def test_given_disconnect_when_disconnect(self):
        self.ami_client.disconnect()

        self.ami_client.disconnect()

    def test_sock_is_none_after_init(self):
        ami_client = AMIClient(self.hostname, self.username, self.password)

        self.assertEqual(None, ami_client._sock)

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
