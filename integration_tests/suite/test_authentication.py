# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Any

import pytest
from hamcrest import (
    assert_that,
    calling,
    empty,
    equal_to,
    has_entries,
    has_properties,
    has_property,
    not_,
)
from requests.exceptions import HTTPError
from wazo_amid_client.exceptions import AmidError
from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises

from .helpers.base import (
    TOKEN_SUB_TENANT,
    VALID_TOKEN,
    APIAssetLaunchingTestCase,
    APIIntegrationTest,
)


@pytest.mark.usefixtures('base')
class TestAuthentication(APIIntegrationTest):
    def _assert_unauthorized(self, url: str, *args: Any) -> None:
        assert_that(
            calling(url).with_args(*args),
            raises(HTTPError).matching(
                has_property('response', has_property('status_code', 401))
            ),
        )

    def test_no_auth_gives_401(self) -> None:
        self.amid.set_token(None)
        url = self.amid.action
        self._assert_unauthorized(url, 'ping')

    def test_valid_auth_gives_result(self) -> None:
        self.amid.set_token(VALID_TOKEN)
        result = self.amid.action('ping')
        assert_that(result, not_(empty()))

    def test_invalid_auth_gives_401(self) -> None:
        self.amid.set_token('invalid-token')
        url = self.amid.action
        self._assert_unauthorized(url, 'ping')

    def test_restrict_only_master_tenant(self) -> None:
        self.amid.set_token(TOKEN_SUB_TENANT)

        url = self.amid.command
        self._assert_unauthorized(url, 'ping')

        url = self.amid.action
        self._assert_unauthorized(url, 'ping')

    def test_restrict_on_with_slow_wazo_auth(self) -> None:
        APIAssetLaunchingTestCase.stop_service('amid')
        with self.auth_stopped():
            APIAssetLaunchingTestCase.start_service('amid')
            self.reset_clients()

            def _amid_returns_503() -> None:
                assert_that(
                    calling(self.amid.action).with_args('ping'),
                    raises(AmidError).matching(
                        has_properties(
                            status_code=503,
                            error_id='not-initialized',
                        )
                    ),
                )

            until.assert_(_amid_returns_503, timeout=10)

        def _amid_does_not_return_503() -> None:
            assert_that(
                calling(self.amid.action).with_args('ping'),
                not_(raises(HTTPError)),
            )

        until.assert_(_amid_does_not_return_503, timeout=10)

    def test_no_auth_server_gives_503(self) -> None:
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
