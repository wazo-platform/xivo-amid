# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

import requests
from hamcrest import assert_that, has_entries
from wazo_test_helpers import until
from wazo_test_helpers.wait_strategy import WaitStrategy


class EverythingOkWaitStrategy(WaitStrategy):
    def wait(self, integration_test: Any) -> None:
        def is_ready() -> None:
            try:
                status = integration_test.amid.status()
            except requests.RequestException:
                status = {}
            assert_that(
                status,
                has_entries(
                    {
                        'rest_api': has_entries(status='ok'),
                        'ami_socket': has_entries(status='ok'),
                        'service_token': has_entries(status='ok'),
                    }
                ),
            )

        until.assert_(is_ready, tries=60)
