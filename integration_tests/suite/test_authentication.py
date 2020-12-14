# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    empty,
    has_entries,
    has_property,
    has_properties,
    not_,
)


from wazo_amid_client.exceptions import AmidError
from requests.exceptions import HTTPError
from xivo_test_helpers import until
from xivo_test_helpers.hamcrest.raises import raises


from .helpers.base import (
    APIAssetLaunchingTestCase,
    APIIntegrationTest,
    VALID_TOKEN,
    TOKEN_SUB_TENANT,
)


@pytest.mark.usefixtures('base')
class TestAuthentication(APIIntegrationTest):
    def _assert_unauthorized(self, url, *args):
        assert_that(
            calling(url).with_args(*args),
            raises(HTTPError).matching(
                has_property('response', has_property('status_code', 401))
            ),
        )

    def test_no_auth_gives_401(self):
        self.amid.set_token(None)
        url = self.amid.action
        self._assert_unauthorized(url, 'ping')

    def test_valid_auth_gives_result(self):
        self.amid.set_token(VALID_TOKEN)
        result = self.amid.action('ping')
        assert_that(result, not_(empty()))

    def test_invalid_auth_gives_401(self):
        self.amid.set_token('invalid-token')
        url = self.amid.action
        self._assert_unauthorized(url, 'ping')

    def test_restrict_only_master_tenant(self):
        self.amid.set_token(TOKEN_SUB_TENANT)

        url = self.amid.command
        self._assert_unauthorized(url, 'ping')

        url = self.amid.action
        self._assert_unauthorized(url, 'ping')

    def test_restrict_on_with_slow_wazo_auth(self):
        APIAssetLaunchingTestCase.stop_service('amid')
        with self.auth_stopped():
            APIAssetLaunchingTestCase.start_service('amid')
            self.reset_clients()

            def _amid_returns_503():
                assert_that(
                    calling(self.amid.action).with_args('ping'),
                    raises(HTTPError).matching(
                        has_property('response', has_property('status_code', 503))
                    ),
                )

            until.assert_(_amid_returns_503, tries=10)

        def _amid_does_not_return_503():
            assert_that(
                calling(self.amid.action).with_args('ping'),
                not_(raises(HTTPError)),
            )

        until.assert_(_amid_does_not_return_503, tries=10)

    def test_no_auth_server_gives_503(self):
        with self.auth_stopped():
            assert_that(
                calling(self.amid.action).with_args('ping'),
                raises(AmidError).matching(
                    has_properties(
                        status_code=503,
                        details=has_entries(
                            auth_server_host=equal_to('auth'),
                            auth_server_port=equal_to(9497),
                        ),
                    )
                ),
            )
