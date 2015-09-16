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
import requests

from flask import current_app
from flask import request
from functools import wraps

from xivo_auth_client import Client
from xivo_ami.core.exceptions import APIException

logger = logging.getLogger(__name__)


class Unauthorized(APIException):

    def __init__(self, token):
        super(Unauthorized, self).__init__(
            status_code=401,
            message='Unauthorized',
            error_id='unauthorized',
            details={
                'invalid_token': token
            }
        )


class AuthServerUnreachable(APIException):

    def __init__(self, host, port, error):
        super(AuthServerUnreachable, self).__init__(
            status_code=503,
            message='Authentication server unreachable',
            error_id='authentication-server-unreachable',
            details={
                'auth_server_host': host,
                'auth_server_port': port,
                'original_error': str(error),
            }
        )


def verify_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-Auth-Token', '')

        try:
            token_is_valid = client().token.is_valid(token)
        except requests.RequestException as e:
            raise AuthServerUnreachable(
                current_app.config['auth']['host'],
                current_app.config['auth']['port'],
                e
            )

        if token_is_valid:
            return func(*args, **kwargs)

        raise Unauthorized(token)
    return wrapper


def client():
    auth_host = current_app.config['auth']['host']
    auth_port = current_app.config['auth']['port']
    return Client(auth_host, auth_port)
