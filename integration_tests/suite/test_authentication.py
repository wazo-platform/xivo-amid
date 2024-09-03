# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
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

from .helpers.base import TOKEN_SUB_TENANT, VALID_TOKEN, APIIntegrationTest


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

        url = self.amid.config
        self._assert_unauthorized(url)

        url = self.amid.config.patch
        self._assert_unauthorized(url, {})

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

        url = self.amid.config
        self._assert_unauthorized(url)

        url = self.amid.config.patch
        self._assert_unauthorized(url, {})

    def test_restrict_when_service_token_not_initialized(self) -> None:
        def _returns_503() -> None:
            assert_that(
                calling(self.amid.action).with_args('ping'),
                raises(AmidError).matching(
                    has_properties(
                        status_code=503,
                        error_id='not-initialized',
                    )
                ),
            )

        config = {'auth': {'username': 'invalid-service'}}
        with self.amid_with_config_file(config):
            until.assert_(_returns_503, timeout=10)

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
