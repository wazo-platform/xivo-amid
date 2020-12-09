# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import logging
import os
import requests

from wazo_amid_client import Client as AmidClient
from contextlib import contextmanager
from hamcrest import assert_that, equal_to
from xivo_test_helpers.asset_launching_test_case import (
    AssetLaunchingTestCase,
    NoSuchPort,
    NoSuchService,
    WrongClient,
)

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')

VALID_TOKEN = 'valid-token-multitenant'
TOKEN_SUB_TENANT = 'valid-token-sub-tenant'


class APIAssetLaunchingTestCase(AssetLaunchingTestCase):
    assets_root = ASSETS_ROOT
    asset = 'base'
    service = 'amid'

    @classmethod
    def make_amid(cls, token=VALID_TOKEN):
        try:
            port = cls.service_port(9491, 'amid')
        except NoSuchService:
            return WrongClient('amid')
        return AmidClient(
            'localhost',
            port=port,
            prefix=None,
            https=False,
            token=token,
        )

    @classmethod
    def make_ajam_base_url(cls):
        try:
            ajam_port = cls.service_port(5040, 'asterisk-ajam')
        except (NoSuchPort, NoSuchService):
            ajam_port = None
        return 'https://localhost:{port}'.format(port=ajam_port)


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
        return '{base_url}/{path}'.format(
            base_url=cls.ajam_base_url, path='/'.join(parts)
        )

    @classmethod
    def amid_status(cls):
        return APIAssetLaunchingTestCase.service_status('amid')

    @classmethod
    def amid_logs(cls):
        return APIAssetLaunchingTestCase.service_logs('amid')

    @classmethod
    @contextmanager
    def auth_stopped(cls):
        APIAssetLaunchingTestCase.stop_service('auth')
        try:
            yield
        finally:
            APIAssetLaunchingTestCase.start_service('auth')
            cls.reset_clients()

    @classmethod
    @contextmanager
    def ajam_stopped(cls):
        APIAssetLaunchingTestCase.stop_service('asterisk-ajam')
        try:
            yield
        finally:
            APIAssetLaunchingTestCase.start_service('asterisk-ajam')
            cls.reset_clients()

    @classmethod
    def ajam_requests(cls):
        response = requests.get(cls.ajam_url('_requests'), verify=False)
        assert_that(response.status_code, equal_to(200))
        return response.json()
