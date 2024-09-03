# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import socket
from collections import defaultdict, deque
from typing import NamedTuple

from xivo.status import Status

from wazo_amid.ami import parser

logger = logging.getLogger(__name__)


class Message(NamedTuple):
    name: str
    headers: dict[str, str]


class AMIClient:
    _BUFSIZE = 4096

    def __init__(self, host: str, username: str, password: str, port: int) -> None:
        self._hostname = host
        self._username = username
        self._password = password
        self._port = port
        self._sock: socket.socket | None = None
        self._buffer = b''
        self._event_queue: deque[Message] = deque()
        self.stopping = False

    def connect_and_login(self) -> None:
        self.stopping = False
        if self._sock is None:
            logger.info('Connecting AMI client to %s:%s', self._hostname, self._port)
            self._connect_socket()
            self._login()
            logger.info('AMI client connected to %s:%s', self._hostname, self._port)

    def disconnect(self, reason: Exception | str | None = None) -> None:
        if self._sock is not None:
            logger.info('Disconnecting AMI client. Reason: %s', reason)
            self._disconnect_socket()

    def parse_next_messages(self) -> deque[Message]:
        self._add_data_to_buffer()
        self._parse_buffer()
        return self._pop_messages()

    def _connect_socket(self) -> None:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self._hostname, self._port))
            # discard the AMI protocol version
            self._sock.recv(self._BUFSIZE)
        except OSError as e:
            raise AMIConnectionError(e)

    def _login(self) -> None:
        data = self._build_login_msg()
        self._send_data_to_socket(data)

    def _build_login_msg(self) -> bytes:
        lines = [
            'Action: Login',
            'Username: %s' % self._username,
            'Secret: %s' % self._password,
            '\r\n',
        ]
        return '\r\n'.join(lines).encode('UTF-8')

    def _disconnect_socket(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None
        self._buffer = b''

    def _add_data_to_buffer(self) -> None:
        data = self._recv_data_from_socket()
        self._buffer += data

    def event_parser_callback(
        self, event_name: str, action_id: str | None, headers: dict[str, str]
    ) -> None:
        message = Message(event_name, headers)
        self._event_queue.append(message)

    def _parse_buffer(self) -> None:
        self._buffer = parser.parse_buffer(
            self._buffer, self.event_parser_callback, None
        )

    def _pop_messages(self) -> deque[Message]:
        messages: deque[Message] = deque()
        messages.extend(self._event_queue)
        self._event_queue.clear()
        return messages

    def _send_data_to_socket(self, data: bytes) -> None:
        try:
            self._sock.sendall(data)  # type: ignore
        except OSError as e:
            logger.error('Could not write data to socket: %s', e)
            raise AMIConnectionError(e)

    def _recv_data_from_socket(self) -> bytes:
        try:
            data = self._sock.recv(self._BUFSIZE)  # type: ignore
        except OSError as e:
            logger.error('Could not read data from socket: %s', e)
            raise AMIConnectionError(e)
        else:
            if not data and not self.stopping:
                logger.error('Could not read data from socket: connection closed')
                raise AMIConnectionError('Connection closed from remote')
            return data

    def stop(self) -> None:
        if self._sock is not None:
            self.stopping = True
            self._sock.shutdown(socket.SHUT_RDWR)
            self.disconnect(reason='explicit stop')

    def provide_status(self, status: defaultdict[str, defaultdict[str, str]]) -> None:
        status['ami_socket']['status'] = Status.ok if self._sock else Status.fail


class AMIConnectionError(Exception):
    def __init__(self, original_error: Exception | str | None = None) -> None:
        self.error = original_error
