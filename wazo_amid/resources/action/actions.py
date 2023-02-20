# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests

from flask import request

from wazo_amid.ami import parser
from wazo_amid.rest_api import AuthResource
from wazo_amid.auth import required_acl, required_master_tenant
from wazo_amid.plugin_helpers.ajam import AJAMClient, AJAMUnreachable

from .schema import command_schema

VERSION = 1.0

logger = logging.getLogger(__name__)


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


def _parse_ami_command(command_result):
    return parser.parse_command_response(command_result)
