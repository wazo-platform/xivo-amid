# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests

from contextlib import contextmanager
from flask import request

from wazo_amid.ami import parser
from wazo_amid.exceptions import APIException
from wazo_amid.rest_api import AuthResource
from wazo_amid.auth import required_acl, required_master_tenant

from .schema import command_schema

VERSION = 1.0

logger = logging.getLogger(__name__)


class AJAMUnreachable(APIException):
    def __init__(self, ajam_url, error):
        super().__init__(
            status_code=503,
            message='AJAM server unreachable',
            error_id='ajam-unreachable',
            details={'ajam_url': ajam_url, 'original_error': str(error)},
        )


class UnsupportedAction(APIException):
    def __init__(self, action):
        super().__init__(
            status_code=501,
            message='Action incompatible with wazo-amid',
            error_id='incompatible-action',
            details={'action': action},
        )


class AJAMClient:
    logoff_params = {'action': 'logoff'}

    def __init__(
        self,
        host,
        port,
        username=None,
        password=None,
        https=True,
        verify_certificate=True,
    ):
        scheme = 'https' if https else 'http'
        self.url = f'{scheme}://{host}:{port}/rawman'
        self.login_params = {
            'action': 'login',
            'username': username,
            'secret': password,
        }
        self.verify = verify_certificate if https else None

    def get(self, action, ami_args):
        params = self._build_params(action, ami_args)
        with self._session() as session:
            return session.get(self.url, params=params)

    @contextmanager
    def _session(self):
        with requests.Session() as session:
            session.get(self.url, params=self.login_params, verify=self.verify)
            yield session
            session.get(self.url, params=self.logoff_params, verify=self.verify)

    def _build_params(self, action, ami_args):
        result = [('action', action)]
        for extra_arg_key, extra_arg_value in ami_args.items():
            if isinstance(extra_arg_value, list):
                result.extend([(extra_arg_key, value) for value in extra_arg_value])
            else:
                result.append((extra_arg_key, extra_arg_value))

        return result


class Actions(AuthResource):
    @classmethod
    def configure(cls, config):
        cls.ajam_client = AJAMClient(**config['ajam'])

    @required_master_tenant()
    @required_acl('amid.action.{action}.create')
    def post(self, action):
        if action.lower() in ('queues', 'command'):
            raise UnsupportedAction(action)

        extra_args = request.get_json(force=True, silent=True) or {}

        try:
            response = self.ajam_client.get(action, extra_args)
        except requests.RequestException as e:
            raise AJAMUnreachable(self.ajam_client.url, e)

        return _parse_ami(response.content), 200


class Command(AuthResource):
    @classmethod
    def configure(cls, config):
        cls.ajam_client = AJAMClient(**config['ajam'])

    @required_master_tenant()
    @required_acl('amid.action.Command.create')
    def post(self):
        extra_args = command_schema.load(request.get_json(force=True))
        try:
            response = self.ajam_client.get('Command', extra_args)
        except requests.RequestException as e:
            raise AJAMUnreachable(self.ajam_client.url, e)

        response_lines = _parse_ami_command(response.content)
        return {'response': response_lines}, 200


def _parse_ami(buffer_):
    result = []

    def aux(event_name, action_id, message):
        result.append(message)

    parser.parse_buffer(buffer_, aux, aux)

    return result


def _parse_ami_command(command_result):
    return parser.parse_command_response(command_result)
