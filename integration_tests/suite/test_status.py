# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from time import sleep
from typing import Any

import pytest
import requests
from hamcrest import assert_that, calling, equal_to, has_property
from requests.exceptions import HTTPError
from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises

from .helpers.base import APIIntegrationTest

FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}

DEFAULT_RECONNECTION_DELAY = 5


@pytest.mark.usefixtures('base')
class TestStatusAMISocket(APIIntegrationTest):
    def test_status_ami_socket(self) -> None:
        result = self.amid.status()
        assert_that(result['ami_socket']['status'], equal_to('ok'))

        with self.ami_stopped():
            result = self.amid.status()
            assert_that(result['ami_socket']['status'], equal_to('fail'))

        sleep(DEFAULT_RECONNECTION_DELAY + 1)

        result = self.amid.status()
        assert_that(result['ami_socket']['status'], equal_to('ok'))


@pytest.mark.usefixtures('base')
class TestStatusRabbitMQ(APIIntegrationTest):
    def test_status_ami_rabbitmq(self) -> None:
        requests.post(self.asset_cls.make_send_event_ami_url(), json=FAKE_EVENT)

        def assert_status_ok() -> None:
            result = self.amid.status()
            assert_that(result['bus_publisher']['status'], equal_to('ok'))

        until.assert_(assert_status_ok, timeout=10)

        with self.rabbitmq_stopped():
            requests.post(self.asset_cls.make_send_event_ami_url(), json=FAKE_EVENT)

            result = self.amid.status()
            assert_that(result['bus_publisher']['status'], equal_to('fail'))

        requests.post(self.asset_cls.make_send_event_ami_url(), json=FAKE_EVENT)
        until.assert_(assert_status_ok, timeout=64)


@pytest.mark.usefixtures('base')
class TestStatusAuthentication(APIIntegrationTest):
    def _assert_unauthorized(self, url: str, *args: Any) -> None:
        assert_that(
            calling(url).with_args(*args),
            raises(HTTPError).matching(
                has_property('response', has_property('status_code', 401))
            ),
        )

    def test_no_token_gives_401(self) -> None:
        self.amid.set_token(None)
        url = self.amid.status
        self._assert_unauthorized(url)

    def test_invalid_token_gives_401(self) -> None:
        self.amid.set_token('invalid-acl-token')
        url = self.amid.status
        self._assert_unauthorized(url)
