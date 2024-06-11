# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import json
from hamcrest import assert_that, equal_to, has_entry
import requests
from .helpers.base import APIIntegrationTest, APIAssetLaunchingTestCase

FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}

DEFAULT_RECONNECTION_DELAY = 5

VERSION = '1.0'


@pytest.mark.usefixtures('base')
class TestConfigAPI(APIIntegrationTest):
    def test_config_response(self) -> None:
        result = self.amid.config()
        assert_that(result['debug'], equal_to(True))

    def test_update_config(self) -> None:
        debug_true_config = json.dumps(
            [
                {
                    'op': 'replace',
                    'path': '/debug',
                    'value': 'True',
                }
            ]
        )

        debug_false_config = json.dumps(
            [
                {
                    'op': 'replace',
                    'path': '/debug',
                    'value': 'False',
                }
            ]
        )
     
        port = APIAssetLaunchingTestCase.service_port(9491, 'amid')
        api_url = 'http://127.0.0.1:{port}/{version}/config'.format(
            port=port, version=VERSION
        )
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': 'valid-token-multitenant',
        }

        debug_true_patched_config = requests.patch(
            api_url, data=debug_true_config, headers=headers, verify=False
        ).json()
        debug_true_config = requests.get(api_url, headers=headers, verify=False).json()
        assert_that(debug_true_patched_config, equal_to(debug_true_config))
        assert_that(debug_true_config, has_entry('debug', True))

        debug_false_patched_config = requests.patch(
            api_url, data=debug_false_config, headers=headers, verify=False
        ).json()
        debug_false_config = requests.get(api_url, headers=headers, verify=False).json()
        assert_that(debug_false_patched_config, equal_to(debug_false_config))
        assert_that(debug_false_config, has_entry('debug', False))
