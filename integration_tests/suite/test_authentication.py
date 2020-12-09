# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from hamcrest import assert_that, equal_to

from requests.exceptions import ConnectionError
from xivo_test_helpers import until

from .helpers.base import (
    APIAssetLaunchingTestCase,
    APIIntegrationTest,
    VALID_TOKEN,
    TOKEN_SUB_TENANT,
)


@pytest.mark.usefixtures('base')
class TestAuthentication(APIIntegrationTest):

    def test_no_auth_gives_401(self):
        result = self.post_action_result('ping', token=None)

        assert_that(result.status_code, equal_to(401))

    def test_valid_auth_gives_result(self):
        result = self.post_action_result('ping', token=VALID_TOKEN)

        assert_that(result.status_code, equal_to(200))

    def test_invalid_auth_gives_401(self):
        result = self.post_action_result('ping', token='invalid-token')

        assert_that(result.status_code, equal_to(401))

    def test_restrict_only_master_tenant(self):
        result = self.post_command_result('ping', token=TOKEN_SUB_TENANT)
        assert_that(result.status_code, equal_to(401))

        result = self.post_action_result('ping', token=TOKEN_SUB_TENANT)
        assert_that(result.status_code, equal_to(401))

    def test_restrict_on_with_slow_wazo_auth(self):
        APIAssetLaunchingTestCase.stop_service('amid')
        with self.auth_stopped():
            APIAssetLaunchingTestCase.start_service('amid')
            self.reset_clients()

            def _amid_returns_503():
                try:
                    result = self.post_action_result('ping', token=VALID_TOKEN)
                    assert_that(result.status_code, equal_to(503))
                except ConnectionError:
                    raise AssertionError

            until.assert_(_amid_returns_503, tries=10)

        def _amid_does_not_return_503():
            result = self.post_action_result('ping', token=VALID_TOKEN)
            assert_that(result.status_code, equal_to(200))

        until.assert_(_amid_does_not_return_503, tries=10)

    def test_no_auth_server_gives_503(self):
        with self.auth_stopped():
            result = self.post_action_result('ping', token=VALID_TOKEN)

            assert_that(result.status_code, equal_to(503))
            assert_that(result.json()['details']['auth_server_host'], equal_to('auth'))
            assert_that(result.json()['details']['auth_server_port'], equal_to(9497))
