# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import assert_that
from hamcrest import equal_to
from xivo_test_helpers import asset_launching_test_case

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets')
CA_CERT = os.path.join(ASSETS_ROOT, '_common', 'ssl', 'localhost', 'server.crt')

VALID_TOKEN = 'valid-token'


class BaseIntegrationTest(asset_launching_test_case.AssetLaunchingTestCase):

    assets_root = ASSETS_ROOT
    service = 'amid'

    @classmethod
    def setUpClass(cls):
        super(BaseIntegrationTest, cls).setUpClass()
        try:
            cls._amid_port = cls.service_port(9491, 'amid')
        except asset_launching_test_case.NoSuchPort:
            cls._amid_port = None
        try:
            cls._ajam_port = cls.service_port(5040, 'asterisk-ajam')
        except (asset_launching_test_case.NoSuchPort, asset_launching_test_case.NoSuchService):
            cls._ajam_port = None

    @classmethod
    def amid_url(cls, *parts):
        return 'https://{host}:{port}/1.0/{path}'.format(host='localhost',
                                                         port=cls._amid_port,
                                                         path='/'.join(parts))

    @classmethod
    def ajam_url(cls, *parts):
        return 'https://{host}:{port}/{path}'.format(host='localhost',
                                                     port=cls._ajam_port,
                                                     path='/'.join(parts))

    @classmethod
    def amid_status(cls):
        return cls.service_status('amid')

    @classmethod
    def amid_logs(cls):
        return cls.service_logs('amid')

    @classmethod
    def ajam_requests(cls):
        response = requests.get(cls.ajam_url('_requests'), verify=False)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    @classmethod
    def post_action_result(cls, action, params=None, token=None):
        result = requests.post(cls.amid_url('action', action),
                               data=(json.dumps(params) if params else ''),
                               headers={'X-Auth-Token': token},
                               verify=CA_CERT)
        return result

    @classmethod
    def action(cls, action, params=None, token=VALID_TOKEN):
        response = cls.post_action_result(action, params, token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    @classmethod
    def post_command_result(cls, body, token=None):
        result = requests.post(cls.amid_url('action', 'Command'),
                               json=body,
                               headers={'X-Auth-Token': token},
                               verify=CA_CERT)
        return result

    @classmethod
    def command(cls, command, token=VALID_TOKEN):
        body = {'command': command}
        response = cls.post_command_result(body, token)
        assert_that(response.status_code, equal_to(200))
        return response.json()
