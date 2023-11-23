# Copyright 2022-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import requests

from hamcrest import assert_that, has_items, has_entries
from wazo_test_helpers import until
from wazo_test_helpers.bus import BusClient, BusMessageAccumulator
from .helpers.base import APIIntegrationTest, APIAssetLaunchingTestCase


FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}


@pytest.mark.usefixtures('base')
class TestBusEvents(APIIntegrationTest):
    bus: BusClient

    def setUp(self) -> None:
        super().setUp()
        self.bus = APIAssetLaunchingTestCase.make_bus()

    def test_ami_sends_events_on_bus(self) -> None:
        events = self.bus.accumulator(headers={'name': 'foo'})

        requests.post(
            APIAssetLaunchingTestCase.make_send_event_ami_url(), json=FAKE_EVENT
        )

        def assert_received(bus_accumulator: BusMessageAccumulator) -> None:
            assert_that(
                bus_accumulator.accumulate(with_headers=True),
                has_items(
                    has_entries(
                        message=has_entries(
                            data=has_entries(
                                Event='foo',
                                AnswerToTheUniverse='42',
                            )
                        ),
                        headers=has_entries(
                            name='foo',
                        ),
                    )
                ),
            )

        until.assert_(assert_received, events, tries=10)
