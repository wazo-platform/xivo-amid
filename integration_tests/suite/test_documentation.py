# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import requests
import pprint

from hamcrest import assert_that, empty

from .base import BaseIntegrationTest


class TestDocumentation(BaseIntegrationTest):

    asset = 'documentation'

    def test_documentation_errors(self):
        api_url = 'https://amid:9491/1.0/api/api.yml'
        self.validate_api(api_url)

    def validate_api(self, url):
        port = self.service_port(8080, 'swagger-validator')
        validator_url = u'http://localhost:{port}/debug'.format(port=port)
        response = requests.get(validator_url, params={'url': url})
        assert_that(response.json(), empty(), pprint.pformat(response.json()))
