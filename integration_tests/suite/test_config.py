# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from hamcrest import assert_that, equal_to, has_entry
from .helpers.base import APIIntegrationTest

FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}

DEFAULT_RECONNECTION_DELAY = 5

VERSION = '1.0'


@pytest.mark.usefixtures('base')
class TestConfigAPI(APIIntegrationTest):
    def test_config_response(self) -> None:
        result = self.amid.config()
        assert_that(result['debug'], equal_to(True))

    def test_update_config(self) -> None:
        debug_true_config = [
                {
                    'op': 'replace',
                    'path': '/debug',
                    'value': "True",
                }
            ]

        debug_false_config = [
                {
                    'op': 'replace',
                    'path': '/debug',
                    'value': "False",
                }
            ]

        debug_true_patched_config = self.amid.config.patch(debug_true_config)
        debug_true_config = self.amid.config()
        assert_that(debug_true_patched_config, equal_to(debug_true_config))
        assert_that(debug_true_config, has_entry('debug', True))

        debug_false_patched_config = self.amid.config.patch(debug_false_config)
        debug_false_config = self.amid.config()
        assert_that(debug_false_patched_config, equal_to(debug_false_config))
        assert_that(debug_false_config, has_entry('debug', False))
