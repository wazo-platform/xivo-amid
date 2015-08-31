# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
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

import textwrap
import sys

from flask import Flask
from flask import request
from OpenSSL import SSL

app = Flask(__name__)

port = int(sys.argv[1])

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('/usr/local/share/asterisk-ajam-ssl/server.key')
context.use_certificate_file('/usr/local/share/asterisk-ajam-ssl/server.crt')


def response(body):
    return textwrap.dedent(body).replace('\n', '\r\n')


@app.route("/rawman")
def rawman():
    action = request.args['action'].lower()
    return actions[action]()


def login():
    return response('''\
        Response: Success
        Message: Authentication accepted

        '''), 200


@app.route("/1.0/ping")
def ping():
    return response('''\
        Response: Success
        Ping: Pong
        Timestamp: 1234567890.123456

        '''), 200


actions = {
    'login': login,
    'ping': ping
}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=True)
