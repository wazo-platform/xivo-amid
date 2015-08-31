# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from .base import BaseIntegrationTest

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to
from hamcrest import has_entries
from hamcrest import matches_regexp


class TestListPersonal(BaseIntegrationTest):

    asset = 'http_only'

    def test_that_action_ping_returns_pong(self):
        result = self.action('Ping')

        assert_that(result, contains(has_entries({
            'Response': 'Success',
            'Ping': 'Pong',
            'Timestamp': matches_regexp('.*')
        })))


class TestAuthentication(BaseIntegrationTest):

    asset = 'http_only'

    def test_that_actions_is_authenticated(self):
        result = self.get_action_result('Ping', token='invalid')

        assert_that(result.status_code, equal_to(401))
