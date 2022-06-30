# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from time import sleep
from requests import post
import pytest
from hamcrest import assert_that, equal_to

from wazo_test_helpers import until
from wazo_amid.facade import EventHandlerFacade
from .helpers.base import APIIntegrationTest, APIAssetLaunchingTestCase

FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}
AMI_SOCKET = 'ami_socket'
BUS_PUBLISHER = 'bus_publisher'
STATUS = 'status'
OK = 'ok'
FAIL = 'fail'
BASE = 'base'


@pytest.mark.usefixtures(BASE)
class TestStatusAMISocket(APIIntegrationTest):

    def test_status_ami_socket(self):
        result = self.amid.status()
        assert_that(
            result[AMI_SOCKET][STATUS], equal_to(OK)
        )

        with self.ami_stopped():
            result = self.amid.status()
            assert_that(
                result[AMI_SOCKET][STATUS], equal_to(FAIL)
            )

        sleep(EventHandlerFacade.RECONNECTION_DELAY + 1)

        result = self.amid.status()
        assert_that(
            result[AMI_SOCKET][STATUS], equal_to(OK)
        )


@pytest.mark.usefixtures(BASE)
class TestStatusRabbitMQ(APIIntegrationTest):

    def test_status_ami_rabbitmq(self):
        post(
            APIAssetLaunchingTestCase.make_send_event_ami_url(),
            json=FAKE_EVENT
        )

        def assert_status_ok():
            result = self.amid.status()
            assert_that(
                result[BUS_PUBLISHER][STATUS], equal_to(OK)
            )

        until.assert_(assert_status_ok, tries=10, interval=1)

        with self.rabbitmq_stopped():
            post(
                APIAssetLaunchingTestCase.make_send_event_ami_url(),
                json=FAKE_EVENT
            )

            result = self.amid.status()
            assert_that(
                result[BUS_PUBLISHER][STATUS], equal_to(FAIL)
            )

        post(
            APIAssetLaunchingTestCase.make_send_event_ami_url(),
            json=FAKE_EVENT
        )
        until.assert_(
            assert_status_ok, tries=10, interval=1
        )
