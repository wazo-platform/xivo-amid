#!/usr/bin/env python3
# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import sys
import textwrap
from typing import Any, Callable, TypedDict

from flask import Flask, Response, jsonify, request


class RequestDict(TypedDict):
    method: str
    path: str
    query: list[str]
    body: dict[str, str] | list[str | Any]
    headers: dict[str, str]


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

port = int(sys.argv[1])

_db: dict[str, str] = {}
_requests: list[RequestDict] = []


def _db_get(family: str, key: str) -> str:
    return _db[f'{family}/{key}']


def _db_put(family: str, key: str, value: str) -> None:
    _db[f'{family}/{key}'] = value


def response(body: str) -> str:
    return textwrap.dedent(body).replace('\n', '\r\n')


@app.before_request
def log_request() -> None:
    if not request.path.startswith('/_requests'):
        path = request.path
        log: RequestDict = {
            'method': request.method,
            'path': path,
            'query': list(request.args.items(multi=True)),
            'body': request.data.json() if request.is_json else request.data.decode(),
            'headers': dict(request.headers),
        }
        _requests.append(log)


@app.route('/_requests', methods=['GET'])
def list_requests() -> Response:
    return jsonify(requests=_requests)


@app.route('/rawman')
def rawman() -> tuple[str, int]:
    action = request.args['action'].lower()
    try:
        return actions[action]()
    except Exception as e:
        logging.exception(e)
        raise


def login() -> tuple[str, int]:
    return (
        response(
            '''\
        Response: Success
        Message: Authentication accepted

        '''
        ),
        200,
    )


def ping() -> tuple[str, int]:
    return (
        response(
            '''\
        Response: Success
        Ping: Pong
        Timestamp: 1234567890.123456

        '''
        ),
        200,
    )


def queuestatus() -> tuple[str, int]:
    return (
        response(
            '''\
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

        '''
        ),
        200,
    )


def dbget() -> tuple[str, int]:
    args = request.args
    family = args['Family']
    key = args['Key']
    return (
        response(
            f'''\
        Response: Success
        Message: Result will follow
        EventList: start

        Event: DBGetResponse
        Family: {family}
        Key: {key}
        Val: {_db_get(family, key)}

        EventList: Complete
        Event: DBGetComplete
        ListItems: 1

        '''
        ),
        200,
    )


def dbput() -> tuple[str, int]:
    args = request.args
    _db_put(args['Family'], args['Key'], args['Val'])
    return (
        response(
            '''\
        Response: Success
        Message: Updated database successfully

        '''
        ),
        200,
    )


def originate() -> tuple[str, int]:
    return (
        response(
            '''\
        Response: Success
        Message: Originate successfully queued

        '''
        ),
        200,
    )


def command() -> tuple[str, int]:
    return (
        response(
            '''\
        Response: Success
        Message: Command output follows
        Output: Class: default
        Output: 	Mode: files
        Output: 	Directory: /var/lib/wazo/moh/default

        '''
        ),
        200,
    )


actions: dict[str, Callable[[], tuple[str, int]]] = {
    'command': command,
    'dbget': dbget,
    'dbput': dbput,
    'login': login,
    'ping': ping,
    'queuestatus': queuestatus,
    'originate': originate,
}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
