# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import pytest
import requests
import yaml

from openapi_spec_validator import validate_v2_spec

from .helpers.base import APIIntegrationTest, APIAssetLaunchingTestCase

logger = logging.getLogger('openapi_spec_validator')
logger.setLevel(logging.INFO)


@pytest.mark.usefixtures('base')
class TestDocumentation(APIIntegrationTest):
    def test_documentation_errors(self):
        port = APIAssetLaunchingTestCase.service_port(9491, 'amid')
        api_url = 'http://127.0.0.1:{port}/1.0/api/api.yml'.format(port=port)
        api = requests.get(api_url)
        validate_v2_spec(yaml.safe_load(api.text))
