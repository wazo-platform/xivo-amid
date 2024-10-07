# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import os
from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING, TypedDict

import marshmallow
from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.middleware.proxy_fix import ProxyFix
from xivo import http_helpers, plugin_helpers, rest_api_helpers, wsgi
from xivo.flask.auth_verifier import AuthVerifierFlask
from xivo.http_helpers import ReverseProxied

from wazo_amid.plugin_helpers.ajam import AJAMClient

from .exceptions import ValidationError

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import ParamSpec, TypeVar

    from xivo.status import StatusAggregator

    from .config import AmidConfigDict, RestApiConfigDict

    P = ParamSpec('P')
    R = TypeVar('R')


VERSION = 1.0

app = Flask('wazo_amid')
logger = logging.getLogger(__name__)
api = Api(prefix=f'/{VERSION}')
auth_verifier = AuthVerifierFlask()
wsgi_server: wsgi.WSGIServer = None


class PluginDependencies(TypedDict):
    api: Api
    ajam_client: AJAMClient
    config: AmidConfigDict
    status_aggregator: StatusAggregator


def configure(
    global_config: AmidConfigDict, status_aggregator: StatusAggregator
) -> None:
    http_helpers.add_logger(app, logger)
    app.before_request(http_helpers.log_before_request)
    app.after_request(http_helpers.log_request)
    app.config.update(global_config)
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = timedelta(minutes=5)

    cors_config = dict(global_config['rest_api']['cors'])
    enabled = cors_config.pop('enabled', False)
    if enabled:
        CORS(app, **cors_config)

    load_resources(global_config, status_aggregator)
    api.init_app(app)


def load_resources(
    global_config: AmidConfigDict, status_aggregator: StatusAggregator
) -> None:
    plugin_helpers.load(
        namespace='wazo_amid.plugins',
        names=global_config['enabled_plugins'],
        dependencies={
            'api': api,
            'ajam_client': AJAMClient(**global_config['ajam']),
            'config': global_config,
            'status_aggregator': status_aggregator,
        },
    )


def run(config: RestApiConfigDict) -> None:
    bind_addr = (config['listen'], config['port'])

    wsgi_app = ReverseProxied(ProxyFix(wsgi.WSGIPathInfoDispatcher({'/': app})))
    global wsgi_server
    wsgi_server = wsgi.WSGIServer(
        bind_addr=bind_addr,
        wsgi_app=wsgi_app,
        numthreads=config['max_threads'],
    )
    if config['certificate'] and config['private_key']:
        logger.warning(
            'Using service SSL configuration is deprecated. Please use NGINX instead.'
        )
        wsgi_server.ssl_adapter = http_helpers.ssl_adapter(
            config['certificate'], config['private_key']
        )

    logger.debug(
        'WSGIServer starting... uid: %s, listen: %s:%s',
        os.getuid(),
        bind_addr[0],
        bind_addr[1],
    )
    for route in http_helpers.list_routes(app):
        logger.debug(route)

    wsgi_server.start()


def stop() -> None:
    if wsgi_server:
        wsgi_server.stop()


def handle_validation_exception(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except marshmallow.ValidationError as e:
            raise ValidationError(e.messages)

    return wrapper


class ErrorCatchingResource(Resource):
    method_decorators = [
        handle_validation_exception,
        rest_api_helpers.handle_api_exception,
    ] + Resource.method_decorators


class AuthResource(ErrorCatchingResource):
    method_decorators = [
        auth_verifier.verify_tenant,
        auth_verifier.verify_token,
    ] + ErrorCatchingResource.method_decorators
