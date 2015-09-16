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

import json
import logging
import os
import requests
import time

from cherrypy import wsgiserver
from datetime import timedelta
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_restful import Api
from werkzeug.contrib.fixers import ProxyFix

from xivo import http_helpers
from xivo_ami.ami import parser
from xivo_ami.auth import AuthResource
from xivo_ami.swagger.resource import SwaggerResource

VERSION = 1.0

app = Flask('xivo_amid')
logger = logging.getLogger(__name__)
api = Api(prefix='/{}'.format(VERSION))


def configure(global_config):
    Actions.configure(global_config)

    http_helpers.add_logger(app, logger)
    app.after_request(http_helpers.log_request)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = timedelta(minutes=5)

    cors_config = dict(global_config['rest_api']['cors'])
    enabled = cors_config.pop('enabled', False)
    if enabled:
        CORS(app, **cors_config)

    api.add_resource(Actions, '/action/<action>')
    SwaggerResource.add_resource(api)
    api.init_app(app)

    app.config['auth'] = global_config['auth']


def run(config):
    bind_addr = (config['listen'], config['port'])

    _check_file_readable(config['certificate'])
    _check_file_readable(config['private_key'])
    wsgi_app = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(bind_addr=bind_addr, wsgi_app=wsgi_app)
    server.ssl_adapter = http_helpers.ssl_adapter(config['certificate'],
                                                  config['private_key'],
                                                  config.get('ciphers'))

    logger.debug('WSGIServer starting... uid: %s, listen: %s:%s', os.getuid(), bind_addr[0], bind_addr[1])
    for route in http_helpers.list_routes(app):
        logger.debug(route)

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


def _check_file_readable(file_path):
    with open(file_path, 'r'):
        pass


class Actions(AuthResource):

    @classmethod
    def configure(cls, config):
        cls.ajam_url = 'https://{host}:{port}/rawman'.format(**config['ajam'])
        cls.login_params = {
            'action': 'login',
            'username': config['ajam']['username'],
            'secret': config['ajam']['password'],
        }
        cls.verify = config['ajam']['verify_certificate']

    def post(self, action):
        if action.lower() in ('queues', 'command'):
            error = {
                'reason': ['The action {action} is not compatible with xivo-amid'.format(action=action)],
                'timestamp': [time.time()],
                'status_code': 501,
            }
            return error, 501

        extra_args = json.loads(request.data) if request.data else {}

        with requests.Session() as session:
            try:
                session.get(self.ajam_url, params=self.login_params, verify=self.verify)

                response = session.get(self.ajam_url, params=_ajam_params(action, extra_args))
            except requests.RequestException as e:
                message = 'Could not connect to AJAM server on {url}: {error}'.format(url=self.ajam_url, error=e)
                logger.exception(message)
                return {
                    'reason': [message],
                    'timestamp': [time.time()],
                    'status_code': 503,
                }, 503

        return _parse_ami(response.content), 200


def _ajam_params(action, ami_args):
    result = [('action', action)]
    for extra_arg_key, extra_arg_value in ami_args.iteritems():
        if isinstance(extra_arg_value, list):
            result.extend([(extra_arg_key, value) for value in extra_arg_value])
        else:
            result.append((extra_arg_key, extra_arg_value))

    return result


def _parse_ami(buffer_):
    result = []

    def aux(event_name, action_id, message):
        result.append(message)

    parser.parse_buffer(buffer_, aux, aux)

    return result
