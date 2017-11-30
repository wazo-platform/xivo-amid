# -*- coding: utf-8 -*-

# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
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

import textwrap
import unittest

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import contains
from mock import Mock

from xivo_ami.ami.parser import parse_buffer
from xivo_ami.ami.parser import parse_command_response

MESSAGE_DELIMITER = '\r\n\r\n'
EVENT_DELIMITER = 'Event: '
RESPONSE_DELIMITER = 'Response: '


class TestParser(unittest.TestCase):

    def setUp(self):
        self.mock_event_callback = Mock()
        self.mock_response_callback = Mock()

    def test_given_incomplete_message_when_parse_buffer_then_whole_buffer_returned(self):
        raw_buffer = 'incomplete'

        unparsed_buffer = parse_buffer(raw_buffer, self.mock_event_callback, self.mock_response_callback)

        assert_that(raw_buffer, equal_to(unparsed_buffer))

    def test_given_complete_message_when_parse_buffer_then_callback_and_buffer_emptied(self):
        complete_msg = 'complete message'
        raw_buffer = EVENT_DELIMITER + complete_msg + MESSAGE_DELIMITER

        unparsed_buffer = parse_buffer(raw_buffer, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(''))
        self.mock_event_callback.assert_called_once_with(complete_msg, None, {'Event': complete_msg})

    def test_given_complete_messages_when_parse_buffer_then_multiple_callback_and_buffer_emptied(self):
        first_msg = "first complete message"
        second_msg = "second complete message"
        raw_buffer = EVENT_DELIMITER + first_msg + MESSAGE_DELIMITER + RESPONSE_DELIMITER + second_msg + MESSAGE_DELIMITER

        unparsed_buffer = parse_buffer(raw_buffer, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(''))
        self.mock_event_callback.assert_any_call(first_msg, None, {'Event': first_msg})
        self.mock_response_callback.assert_any_call(second_msg, None, {'Response': second_msg})

    def test_given_unknown_message_when_parse_buffer_then_no_callback(self):
        msg = "unknown: message" + MESSAGE_DELIMITER

        unparsed_buffer = parse_buffer(msg, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(''))
        assert_that(self.mock_event_callback.call_count, equal_to(0))
        assert_that(self.mock_response_callback.call_count, equal_to(0))

    def test_given_incomplete_character_when_parse_buffer_then_incomplete_character_returned(self):
        msg = "foo\xc3"

        unparsed_buffer = parse_buffer(msg, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(msg))

    def test_given_valid_command_response_when_parse_command_response_then_command_response_returned(self):
        msg = textwrap.dedent('''\
            Response: Success\r
            Message: Command output follows\r
            Output: Class: default\r
            Output: 	Mode: files\r
            Output: 	Directory: /var/lib/xivo/moh/default\r
            \r
            ''')

        response_lines = parse_command_response(msg)

        assert_that(response_lines, contains(
            'Class: default',
            '	Mode: files',
            '	Directory: /var/lib/xivo/moh/default'
        ))

    def test_given_event_with_chan_variables_when_parse_buffer_then_chan_variables_are_parsed(self):
        msg = textwrap.dedent('''\
            Event: some-event\r
            ChanVariable: FOO=bar\r
            ChanVariable: BAZ=inga\r
            \r
            ''')
        expected_event = {
            'Event': 'some-event',
            'ChanVariable': {
                'FOO': 'bar',
                'BAZ': 'inga',
            }
        }

        parse_buffer(msg, self.mock_event_callback, self.mock_response_callback)

        self.mock_event_callback.assert_any_call('some-event', None, expected_event)
