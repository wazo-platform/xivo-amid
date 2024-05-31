# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from hamcrest import assert_that, equal_to
from wazo_amid_client.exceptions import AmidError

from .helpers.base import APIIntegrationTest

FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}

DEFAULT_RECONNECTION_DELAY = 5

@pytest.mark.usefixtures('base')
class TestConfigAPI(APIIntegrationTest):
    def test_config_response(self) -> None:
        result = self.amid.config()
        assert_that(result['debug'], equal_to(True))