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

import collections
import logging
import socket
from xivo_ami.ami import parser

logger = logging.getLogger(__name__)


class AMIClient(object):

    _BUFSIZE = 4096
    _TIMEOUT = 100
    _PORT = 5038

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._sock = None
        self._buffer = ''

    def connect_and_login(self):
        logger.info('Connecting socket')
        if self._sock is None:
            self._connect_socket()
            self._login()

    def disconnect(self):
        if self._sock is not None:
            self._disconnect_socket()

    def parse_next_messages(self):
        self._add_data_to_buffer()
        return self._parse_buffer()

    def _connect_socket(self):
        logger.info('Connecting AMI client to %s:%s', self._hostname, self._PORT)
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self._TIMEOUT)
            self._sock.connect((self._hostname, self._PORT))
            # discard the AMI protocol version
            self._sock.recv(self._BUFSIZE)
        except socket.error:
            raise AMIConnectionError()

    def _login(self):
        data = self._build_login_msg()
        self._send_data_to_socket(data)

    def _build_login_msg(self):
        lines = ['Action: Login',
                 'Username: %s' % self._username,
                 'Secret: %s' % self._password,
                 '\r\n'
                 ]
        return '\r\n'.join(lines).encode('UTF-8')

    def _disconnect_socket(self):
        logger.info('Disconnecting AMI client')
        self._sock.close()
        self._sock = None
        self._buffer = ''

    def _add_data_to_buffer(self):
        data = self._recv_data_from_socket()
        self._buffer += data

    def _parse_buffer(self):
        message_queue = collections.deque()
        while True:
            head, sep, self._buffer = self._buffer.partition('\r\n\r\n')
            if not sep:
                self._buffer = head
                break

            try:
                msg = parser.parse_msg(head)
            except Exception as e:
                logger.error('Could not parse message: %s', e)
                continue
            message_queue.append(msg)
        return message_queue

    def _send_data_to_socket(self, data):
        try:
            self._sock.sendall(data)
        except socket.error as e:
            logger.error('Could not write data to socket: %s', e)
            raise AMIConnectionError()

    def _recv_data_from_socket(self):
        try:
            data = self._sock.recv(self._BUFSIZE)
        except socket.error as e:
            logger.error('Could not read data from socket: %s', e)
            raise AMIConnectionError()
        else:
            if not data:
                logger.error('Could not read data from socket: remote connection closed')
                raise AMIConnectionError()
            return data


class AMIConnectionError(Exception):
    pass
