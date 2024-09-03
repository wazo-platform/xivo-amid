#!/usr/bin/env python3
# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import argparse
import logging
import socket
import threading
from http import HTTPStatus
from threading import Thread
from typing import Any

from flask import Flask, request

logging.basicConfig(level=logging.DEBUG)

mock_ami: MockedAsteriskAMI = None  # type: ignore[assignment]
app = Flask(__name__)


@app.route('/send_event', methods=['POST'])
def send_event() -> tuple[str, int]:
    event: dict[str, Any] = request.get_json()
    mock_ami.send_all_clients(event)
    return "", HTTPStatus.OK


class MockedAsteriskAMI(Thread):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.clients_addresses: dict[socket.socket, tuple[str, int]] = {}
        super().__init__()

    def run(self) -> None:
        self.listen()

    def listen(self) -> None:
        self.sock.listen()
        while True:
            client, address = self.sock.accept()
            self.clients_addresses[client] = address
            threading.Thread(target=self.listen_client, args=(client, address)).start()

    def listen_client(self, client: socket.socket, address: str) -> None:
        size = 1024
        client.send(b'Asterisk Call Manager/1.1\r\n\r\n')
        while True:
            data = client.recv(size)
            logging.debug(
                'Data received (%s) from client (%s - %s)', data, client, address
            )
            if data:
                if data.decode().startswith("Action: Login"):
                    client.send(
                        b'Response: Success\r\n'
                        b'Message: Authentication accepted\r\n'
                        b'\r\n'
                    )
                else:
                    client.send(b'Response: Success\r\n\r\n')
            else:
                logging.exception(
                    'Wrong data received, so client is closed '
                    'and removed from list of clients'
                )
                client.close()
                del self.clients_addresses[client]
                break

    def send_all_clients(self, msg: dict[str, Any]) -> None:
        for c in list(self.clients_addresses):
            try:
                d = msg['data'].encode()
                logging.info(f'send data ({d}) to connected client ({c})')
                c.send(d)
            except BrokenPipeError:
                logging.exception('Cannot send')
                del self.clients_addresses[c]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fake Asterisk AMI with /send_event endpoint to emulate event.'
    )
    parser.add_argument(
        '--http_port', type=int, required=True, help='port for /send_event endpoint'
    )
    parser.add_argument(
        '--ami_port', type=int, required=True, help='port of the AMI socket'
    )
    args = parser.parse_args()
    mock_ami = MockedAsteriskAMI('0.0.0.0', args.ami_port)
    mock_ami.start()
    app.run(host='0.0.0.0', port=args.http_port, debug=True, use_reloader=False)
