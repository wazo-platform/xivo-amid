# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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
import subprocess
import unittest

from hamcrest import assert_that
from hamcrest import equal_to

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets')
CA_CERT = os.path.join(ASSETS_ROOT, '_common', 'ssl', 'localhost', 'server.crt')

VALID_TOKEN = 'valid-token'


class BaseIntegrationTest(unittest.TestCase):

    @staticmethod
    def _run_cmd(cmd):
        process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = process.communicate()
        logger.info(out)
        return out

    @classmethod
    def setUpClass(cls):
        cls.container_name = cls.asset
        asset_path = os.path.join(ASSETS_ROOT, cls.asset)
        cls.cur_dir = os.getcwd()
        os.chdir(asset_path)
        cls._run_cmd('docker-compose rm --force')
        cls._run_cmd('docker-compose run --rm sync')

    @classmethod
    def tearDownClass(cls):
        cls._run_cmd('docker-compose kill')
        os.chdir(cls.cur_dir)

    @classmethod
    def amid_status(cls):
        amid_id = cls._run_cmd('docker-compose ps -q amid').strip()
        status = cls._run_cmd('docker inspect {container}'.format(container=amid_id))
        return json.loads(status)

    @classmethod
    def amid_logs(cls):
        amid_id = cls._run_cmd('docker-compose ps -q amid').strip()
        status = cls._run_cmd('docker logs {container}'.format(container=amid_id))
        return status

    @classmethod
    def ajam_requests(cls):
        url = u'https://localhost:5040/_requests'
        response = requests.get(url, verify=False)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    @classmethod
    def post_action_result(cls, action, params=None, token=None):
        url = u'https://localhost:9491/1.0/action/{action}'
        result = requests.post(url.format(action=action),
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
        url = u'https://localhost:9491/1.0/action/Command'
        result = requests.post(url,
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
