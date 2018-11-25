# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import requests

from contextlib import contextmanager
from flask import request

from xivo_ami.ami import parser
from xivo_ami.exceptions import APIException
from xivo_ami.rest_api import AuthResource, required_acl

from .schema import command_schema

LOGOFF_PARAMS = {'action': 'logoff'}
VERSION = 1.0

logger = logging.getLogger(__name__)


class AJAMUnreachable(APIException):

    def __init__(self, ajam_url, error):
        super(AJAMUnreachable, self).__init__(
            status_code=503,
            message='AJAM server unreachable',
            error_id='ajam-unreachable',
            details={
                'ajam_url': ajam_url,
                'original_error': str(error),
            }
        )


class UnsupportedAction(APIException):

    def __init__(self, action):
        super(UnsupportedAction, self).__init__(
            status_code=501,
            message='Action incompatible with xivo-amid',
            error_id='incompatible-action',
            details={
                'action': action
            }
        )


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

    @required_acl('amid.action.{action}.create')
    def post(self, action):
        if action.lower() in ('queues', 'command'):
            raise UnsupportedAction(action)

        extra_args = request.get_json(force=True, silent=True) or {}

        try:
            with _ajam_session(self.ajam_url, self.login_params, self.verify) as session:
                response = session.get(self.ajam_url, params=_ajam_params(action, extra_args))
        except requests.RequestException as e:
            raise AJAMUnreachable(self.ajam_url, e)

        return _parse_ami(response.content), 200


class Command(AuthResource):

    @classmethod
    def configure(cls, config):
        cls.ajam_url = 'https://{host}:{port}/rawman'.format(**config['ajam'])
        cls.login_params = {
            'action': 'login',
            'username': config['ajam']['username'],
            'secret': config['ajam']['password'],
        }
        cls.verify = config['ajam']['verify_certificate']

    @required_acl('amid.action.Command.create')
    def post(self):
        extra_args = command_schema.load(request.get_json(force=True)).data
        try:
            with _ajam_session(self.ajam_url, self.login_params, self.verify) as session:
                response = session.get(self.ajam_url, params=_ajam_params('Command', extra_args))
        except requests.RequestException as e:
            raise AJAMUnreachable(self.ajam_url, e)

        response_lines = _parse_ami_command(response.content)
        return {'response': response_lines}, 200


def _ajam_params(action, ami_args):
    result = [('action', action)]
    for extra_arg_key, extra_arg_value in ami_args.items():
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


def _parse_ami_command(command_result):
    return parser.parse_command_response(command_result)


@contextmanager
def _ajam_session(ajam_url, login_params, verify):
    with requests.Session() as session:
        session.get(ajam_url, params=login_params, verify=verify)
        yield session
        session.get(ajam_url, params=LOGOFF_PARAMS, verify=verify)
