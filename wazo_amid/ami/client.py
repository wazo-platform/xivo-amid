# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import logging
import socket

from xivo.status import Status

from wazo_amid.ami import parser

logger = logging.getLogger(__name__)

Message = collections.namedtuple('Message', ['name', 'headers'])


class AMIClient:
    _BUFSIZE = 4096

    def __init__(self, host, username, password, port):
        self._hostname = host
        self._username = username
        self._password = password
        self._port = port
        self._sock = None
        self._buffer = b''
        self._event_queue = collections.deque()
        self.stopping = False

    def connect_and_login(self):
        self.stopping = False
        if self._sock is None:
            logger.info(
                'Connecting AMI client to %s:%s', self._hostname, self._port)
            self._connect_socket()
            self._login()
            logger.info(
                'AMI client connected to %s:%s', self._hostname, self._port)

    def disconnect(self, reason=None):
        if self._sock is not None:
            logger.info('Disconnecting AMI client. Reason: %s', reason)
            self._disconnect_socket()

    def parse_next_messages(self):
        self._add_data_to_buffer()
        self._parse_buffer()
        return self._pop_messages()

    def _connect_socket(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self._hostname, self._port))
            # discard the AMI protocol version
            self._sock.recv(self._BUFSIZE)
        except socket.error as e:
            raise AMIConnectionError(e)

    def _login(self):
        data = self._build_login_msg()
        self._send_data_to_socket(data)

    def _build_login_msg(self):
        lines = [
            'Action: Login',
            'Username: %s' % self._username,
            'Secret: %s' % self._password,
            '\r\n',
        ]
        return '\r\n'.join(lines).encode('UTF-8')

    def _disconnect_socket(self):
        self._sock.close()
        self._sock = None
        self._buffer = b''

    def _add_data_to_buffer(self):
        data = self._recv_data_from_socket()
        self._buffer += data

    def event_parser_callback(self, event_name, action_id, headers):
        message = Message(event_name, headers)
        self._event_queue.append(message)

    def _parse_buffer(self):
        self._buffer = parser.parse_buffer(
            self._buffer, self.event_parser_callback, None
        )

    def _pop_messages(self):
        messages = collections.deque()
        messages.extend(self._event_queue)
        self._event_queue.clear()
        return messages

    def _send_data_to_socket(self, data):
        try:
            self._sock.sendall(data)
        except socket.error as e:
            logger.error('Could not write data to socket: %s', e)
            raise AMIConnectionError(e)

    def _recv_data_from_socket(self):
        try:
            data = self._sock.recv(self._BUFSIZE)
        except socket.error as e:
            logger.error('Could not read data from socket: %s', e)
            raise AMIConnectionError(e)
        else:
            if not data and not self.stopping:
                logger.error(
                    'Could not read data from socket: connection closed')
                raise AMIConnectionError('Connection closed from remote')
            return data

    def stop(self):
        if self._sock is not None:
            self.stopping = True
            self._sock.shutdown(socket.SHUT_RDWR)
            self.disconnect(reason='explicit stop')

    def provide_status(self, status):
        status['ami_socket']['status'] = (
            Status.ok if self._sock else Status.fail)


class AMIConnectionError(Exception):
    def __init__(self, original_error=None):
        self.error = original_error
