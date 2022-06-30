# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import logging
import sys
from flask import Flask
from flask import request
import socket
import threading
from threading import Thread

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


@app.route('/send_event', methods=['POST'])
def send_event():
    event = request.get_json()
    logging.warning(event)
    s.send_all_clients(event)
    return "ok"


class MockedAsteriskAMI(Thread):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.clients_addresses = {}
        super().__init__()

    def run(self):
        self.listen()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            self.clients_addresses[client] = address
            try:
                threading.Thread(
                    target=self.listen_client,
                    args=(client, address)
                ).start()
            except ValueError as e:
                logging.exception(
                    f"Wrong data received, so client is closed "
                    f"and removed from list of clients")
                client.close()
                del self.clients_addresses[client]

    def listen_client(self, client, address):
        size = 1024
        while True:
            try:
                client.send(
                    'Asterisk Call Manager/1.1\r\n\r\n'.encode()
                )
                data = client.recv(size)
                logging.debug(
                    f'Data received ({data}) from '
                    f'client ({client} - {address})'
                )
                if data:
                    # Set the response to echo back the recieved data
                    response = data
                    if data.decode().startswith("Action: Login"):
                        client.send(
                            'Response: Success\r\n'
                            'Message: Authentication accepted\r\n'
                            '\r\n'.encode())
                    else:
                        client.send(response)
                else:
                    raise ValueError('Empty data')
            except ValueError as e:
                logging.exception(
                    f'Exception while listening data from client')
                raise e

    def send_all_clients(self, msg):
        for c in list(self.clients_addresses.keys()):
            try:
                d = msg['data'].encode()
                logging.info(
                    f'send data ({d}) to connected client ({c})')
                c.send(d)
            except BrokenPipeError as e:
                logging.exception("cannot send")
                del self.clients_addresses[c]


s = None
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fake Asterisk AMI with /send_event endpoint '
                    'to emulate event.'
    )
    parser.add_argument(
        '--http_port',
        type=int,
        required=True,
        help='port for /send_event endpoint'
    )
    parser.add_argument(
        '--ami_port',
        type=int,
        required=True,
        help='port of the AMI socket'
    )
    args = parser.parse_args()
    s = MockedAsteriskAMI('0.0.0.0', args.ami_port)
    s.start()
    app.run(
        host='0.0.0.0',
        port=args.http_port,
        debug=True,
        use_reloader=False
    )
