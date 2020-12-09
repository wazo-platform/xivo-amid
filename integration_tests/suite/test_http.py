# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import random
import string

from hamcrest import (
    assert_that,
    contains,
    contains_string,
    equal_to,
    has_entry,
    has_entries,
    has_item,
    matches_regexp,
)
from .helpers.base import (
    APIIntegrationTest,
    VALID_TOKEN,
)


@pytest.mark.usefixtures('base')
class TestHTTPAction(APIIntegrationTest):
    def test_that_action_ping_returns_pong(self):
        result = self.action('Ping')

        assert_that(
            result,
            contains(
                has_entries(
                    {
                        'Response': 'Success',
                        'Ping': 'Pong',
                        'Timestamp': matches_regexp('.*'),
                    }
                )
            ),
        )

    def test_that_malformatted_actions_are_refused(self):
        # the format of Queues response is suited for display, not parsing
        result = self.post_action_result('Queues', token=VALID_TOKEN)
        assert_that(result.status_code, equal_to(501))

    def test_that_action_with_events_returns_events(self):
        result = self.action('QueueStatus')

        assert_that(
            result,
            contains(
                has_entries(
                    {
                        'Response': 'Success',
                        'EventList': 'start',
                        'Message': 'Queue status will follow',
                    }
                ),
                has_entries(
                    {
                        'Event': 'QueueParams',
                        'Queue': 'my_queue',
                        'Max': '0',
                        'Strategy': 'ringall',
                        'Calls': '0',
                        'Holdtime': '0',
                        'TalkTime': '0',
                        'Completed': '0',
                        'Abandoned': '0',
                        'ServiceLevel': '0',
                        'ServicelevelPerf': '0.0',
                        'Weight': '0',
                    }
                ),
                has_entries(
                    {
                        'Event': 'QueueStatusComplete',
                        'EventList': 'Complete',
                        'ListItems': '1',
                    }
                ),
            ),
        )

    def test_that_action_with_parameters_sends_parameters(self):
        key = ''.join(random.choice(string.ascii_letters) for _ in range(10))

        self.action('DBPut', {'Family': key, 'Key': key, 'Val': key})
        result = self.action('DBGet', {'Family': key, 'Key': key})

        assert_that(
            result,
            has_item(
                has_entries(
                    {'Event': 'DBGetResponse', 'Family': key, 'Key': key, 'Val': key}
                )
            ),
        )

    def test_that_action_can_send_and_receive_non_ascii(self):
        family = 'my-family'
        key = 'my-key'
        value = 'non-ascii-value äåéëþüü'

        self.action('DBPut', {'Family': family, 'Key': key, 'Val': value})
        result = self.action('DBGet', {'Family': family, 'Key': key})

        assert_that(
            result,
            has_item(
                has_entries(
                    {
                        'Event': 'DBGetResponse',
                        'Family': family,
                        'Key': key,
                        'Val': value,
                    }
                )
            ),
        )


@pytest.mark.usefixtures('base')
class TestHTTPCommand(APIIntegrationTest):
    def test_given_no_command_when_action_command_then_error_400(self):
        response = self.post_command_result({}, VALID_TOKEN)

        assert_that(response.status_code, equal_to(400))

        assert_that(response.json(), has_entry('error_id', equal_to('invalid-data')))

    def test_that_action_command_returns_command_response(self):
        result = self.command('moh show classes')

        assert_that(
            result,
            has_entry(
                'response',
                contains(
                    'Class: default',
                    '	Mode: files',
                    '	Directory: /var/lib/wazo/moh/default',
                ),
            ),
        )


@pytest.mark.usefixtures('base')
class TestHTTPMultipleIdenticalKeys(APIIntegrationTest):

    def test_when_action_with_multiple_identical_keys_then_all_keys_are_sent(self):
        self.action('Originate', {'Variable': ('Var1=one', 'Var2=two')})

        assert_that(
            self.ajam_requests(),
            has_entry(
                'requests',
                has_item(
                    has_entries(
                        {
                            'method': 'GET',
                            'path': '/rawman',
                            'query': contains(
                                ['action', 'Originate'],
                                ['Variable', 'Var1=one'],
                                ['Variable', 'Var2=two'],
                            ),
                        }
                    )
                ),
            ),
        )


@pytest.mark.usefixtures('base')
class TestHTTPError(APIIntegrationTest):
    def test_given_no_ajam_when_http_request_then_status_code_503(self):
        with self.ajam_stopped():
            result = self.post_action_result('ping', token=VALID_TOKEN)

            assert_that(result.status_code, equal_to(503))
            assert_that(
                result.json()['details']['ajam_url'],
                contains_string('asterisk-ajam:5040'),
            )
