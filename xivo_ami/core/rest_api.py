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
import os

from cherrypy import wsgiserver
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource
from werkzeug.contrib.fixers import ProxyFix

from xivo import http_helpers
from xivo_ami.core import auth
from xivo_ami.core import exceptions


VERSION = 1.0

app = Flask('xivo_amid')
logger = logging.getLogger(__name__)
api = Api(prefix='/{}'.format(VERSION))


def configure(global_config):

    http_helpers.add_logger(app, logger)
    app.after_request(http_helpers.log_request)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = timedelta(minutes=5)

    cors_config = dict(global_config['rest_api']['cors'])
    enabled = cors_config.pop('enabled', False)
    if enabled:
        CORS(app, **cors_config)

    load_resources(global_config)
    api.init_app(app)

    app.config['auth'] = global_config['auth']


def load_resources(global_config):
    from xivo_ami.resources.action.actions import Actions
    from xivo_ami.resources.api.actions import SwaggerResource

    Actions.configure(global_config)
    api.add_resource(Actions, '/action/<action>')

    SwaggerResource.add_resource(api)


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


class ErrorCatchingResource(Resource):
    method_decorators = [exceptions.handle_api_exception] + Resource.method_decorators


class AuthResource(ErrorCatchingResource):
    method_decorators = [auth.verify_token] + ErrorCatchingResource.method_decorators
