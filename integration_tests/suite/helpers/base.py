# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import requests
import unittest

from contextlib import contextmanager
from kombu import Exchange
from hamcrest import assert_that, equal_to
from wazo_amid_client import Client as AmidClient
from wazo_test_helpers.asset_launching_test_case import (
    AssetLaunchingTestCase,
    NoSuchPort,
    NoSuchService,
    WrongClient,
)
from wazo_test_helpers.bus import BusClient

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')

VALID_TOKEN = 'valid-token-multitenant'
TOKEN_SUB_TENANT = 'valid-token-sub-tenant'
SERVICE_RABBITMQ = 'rabbitmq'
SERVICE_ASTERISK_AMI = 'asterisk-ami'
SERVICE_ASTERISK_AJAM = 'asterisk-ajam'
SERVICE_AUTH = 'auth'
SERVICE_AMID = 'amid'


class APIAssetLaunchingTestCase(AssetLaunchingTestCase):
    assets_root = ASSETS_ROOT
    asset = 'base'
    service = SERVICE_AMID

    @classmethod
    def make_amid(cls, token=VALID_TOKEN):
        try:
            port = cls.service_port(9491, SERVICE_AMID)
        except NoSuchService:
            return WrongClient(SERVICE_AMID)
        return AmidClient(
            '127.0.0.1',
            port=port,
            prefix=None,
            https=False,
            token=token,
        )

    @classmethod
    def make_bus(cls):
        try:
            port = cls.service_port(5672, SERVICE_RABBITMQ)
        except NoSuchService:
            return WrongClient(SERVICE_RABBITMQ)
        bus = BusClient.from_connection_fields(
            host='127.0.0.1',
            port=port,
            exchange_name='wazo-headers',
            exchange_type='headers',
        )
        upstream = Exchange('xivo', 'topic')
        bus.downstream_exchange_declare('wazo-headers', 'headers', upstream)
        return bus

    @classmethod
    def make_ajam_base_url(cls):
        try:
            ajam_port = cls.service_port(5039, SERVICE_ASTERISK_AJAM)
        except (NoSuchPort, NoSuchService):
            ajam_port = None
        return f'http://127.0.0.1:{ajam_port}'

    @classmethod
    def make_send_event_ami_url(cls):
        try:
            send_event_ami_port = cls.service_port(8123, SERVICE_ASTERISK_AMI)
        except (NoSuchPort, NoSuchService):
            send_event_ami_port = None
        return f'http://127.0.0.1:{send_event_ami_port}/send_event'


class APIIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reset_clients()

    def setUp(self):
        super().setUp()
        self.amid.set_token(VALID_TOKEN)

    @classmethod
    def reset_clients(cls):
        cls.amid = APIAssetLaunchingTestCase.make_amid()
        cls.ajam_base_url = APIAssetLaunchingTestCase.make_ajam_base_url()

    @classmethod
    def ajam_url(cls, *parts):
        path = '/'.join(parts)
        return f'{cls.ajam_base_url}/{path}'

    @classmethod
    def amid_status(cls):
        return APIAssetLaunchingTestCase.service_status(SERVICE_AMID)

    @classmethod
    def amid_logs(cls):
        return APIAssetLaunchingTestCase.service_logs(SERVICE_AMID)

    @classmethod
    @contextmanager
    def auth_stopped(cls):
        APIAssetLaunchingTestCase.stop_service(SERVICE_AUTH)
        try:
            yield
        finally:
            APIAssetLaunchingTestCase.start_service(SERVICE_AUTH)
            cls.reset_clients()

    @classmethod
    @contextmanager
    def ajam_stopped(cls):
        APIAssetLaunchingTestCase.stop_service(SERVICE_ASTERISK_AJAM)
        try:
            yield
        finally:
            APIAssetLaunchingTestCase.start_service(SERVICE_ASTERISK_AJAM)
            cls.reset_clients()

    @classmethod
    @contextmanager
    def ami_stopped(cls):
        APIAssetLaunchingTestCase.stop_service(SERVICE_ASTERISK_AMI)
        try:
            yield
        finally:
            APIAssetLaunchingTestCase.start_service(SERVICE_ASTERISK_AMI)

    @classmethod
    @contextmanager
    def rabbitmq_stopped(cls):
        APIAssetLaunchingTestCase.stop_service(SERVICE_RABBITMQ)
        try:
            yield
        finally:
            APIAssetLaunchingTestCase.start_service(SERVICE_RABBITMQ)

    @classmethod
    def ajam_requests(cls):
        response = requests.get(cls.ajam_url('_requests'))
        assert_that(response.status_code, equal_to(200))
        return response.json()
