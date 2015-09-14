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

import logging
import textwrap
import sys

from flask import Flask
from flask import jsonify
from flask import request
from OpenSSL import SSL

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

port = int(sys.argv[1])

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('/usr/local/share/asterisk-ajam-ssl/server.key')
context.use_certificate_file('/usr/local/share/asterisk-ajam-ssl/server.crt')

_db = {}
_requests = []


def _db_get(family, key):
    return _db['{family}/{key}'.format(family=family, key=key)]


def _db_put(family, key, value):
    _db['{family}/{key}'.format(family=family, key=key)] = value


def response(body):
    return textwrap.dedent(body).replace('\n', '\r\n')


@app.before_request
def log_request():
    if not request.path.startswith('/_requests'):
        path = request.path
        log = {'method': request.method,
               'path': path,
               'query': request.args.items(multi=True),
               'body': request.data,
               'headers': dict(request.headers)}
        _requests.append(log)


@app.route('/_requests', methods=['GET'])
def list_requests():
    return jsonify(requests=_requests)


@app.route('/rawman')
def rawman():
    action = request.args['action'].lower()
    try:
        return actions[action]()
    except Exception as e:
        logging.exception(e)
        raise


def login():
    return response('''\
        Response: Success
        Message: Authentication accepted

        '''), 200


def ping():
    return response('''\
        Response: Success
        Ping: Pong
        Timestamp: 1234567890.123456

        '''), 200


def queuestatus():
    return response('''\
        Response: Success
        EventList: start
        Message: Queue status will follow

        Event: QueueParams
        Queue: my_queue
        Max: 0
        Strategy: ringall
        Calls: 0
        Holdtime: 0
        TalkTime: 0
        Completed: 0
        Abandoned: 0
        ServiceLevel: 0
        ServicelevelPerf: 0.0
        Weight: 0

        Event: QueueStatusComplete
        EventList: Complete
        ListItems: 1

        '''), 200


def dbget():
    args = request.args
    family = args['Family']
    key = args['Key']
    return response('''\
        Response: Success
        Message: Result will follow
        EventList: start

        Event: DBGetResponse
        Family: {family}
        Key: {key}
        Val: {value}

        EventList: Complete
        Event: DBGetComplete
        ListItems: 1

        ''').format(family=family.encode('utf-8'),
                    key=key.encode('utf-8'),
                    value=_db_get(family, key).encode('utf-8')), 200


def dbput():
    args = request.args
    _db_put(args['Family'], args['Key'], args['Val'])
    return response('''\
        Response: Success
        Message: Updated database successfully

        '''), 200


def originate():
    return response('''\
        Response: Success
        Message: Originate successfully queued

        '''), 200


actions = {
    'dbget': dbget,
    'dbput': dbput,
    'login': login,
    'ping': ping,
    'queuestatus': queuestatus,
    'originate': originate,
}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=True)
