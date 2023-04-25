# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import pytest
import requests
import yaml

from openapi_spec_validator import validate_spec, openapi_v2_spec_validator

from .helpers.base import APIIntegrationTest, APIAssetLaunchingTestCase

logger = logging.getLogger('openapi_spec_validator')
logger.setLevel(logging.INFO)


@pytest.mark.usefixtures('base')
class TestDocumentation(APIIntegrationTest):
    def test_documentation_errors(self):
        port = APIAssetLaunchingTestCase.service_port(9491, 'amid')
        api_url = f'http://127.0.0.1:{port}/1.0/api/api.yml'
        api = requests.get(api_url)
        validate_spec(yaml.safe_load(api.text), validator=openapi_v2_spec_validator)
