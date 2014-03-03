# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from hamcrest import assert_that, equal_to
from mock import Mock
import unittest

from xivo_ami.ami.parser import parse_buffer

MESSAGE_DELIMITER = '\r\n\r\n'
EVENT_DELIMITER = 'Event: '
RESPONSE_DELIMITER = 'Response: '


class TestParser(unittest.TestCase):

    def setUp(self):
        self.mock_event_callback = Mock()
        self.mock_response_callback = Mock()

    def test_given_incomple_message_when_parse_buffer_then_whole_buffer_returned(self):
        raw_buffer = 'incomplete'

        unparsed_buffer = parse_buffer(raw_buffer, self.mock_event_callback, self.mock_response_callback)

        assert_that(raw_buffer, equal_to(unparsed_buffer))

    def test_given_complete_message_when_parse_buffer_then_callback_and_buffer_emptied(self):
        complete_msg = 'complete message'
        raw_buffer = EVENT_DELIMITER + complete_msg + MESSAGE_DELIMITER

        unparsed_buffer = parse_buffer(raw_buffer, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(''))
        self.mock_event_callback.assert_called_once_with(complete_msg, None, {})

    def test_given_complete_messages_when_parse_buffer_then_multiple_callback_and_buffer_emptied(self):
        first_msg = "first complete message"
        second_msg = "second complete message"
        raw_buffer = EVENT_DELIMITER + first_msg + MESSAGE_DELIMITER + RESPONSE_DELIMITER + second_msg + MESSAGE_DELIMITER

        unparsed_buffer = parse_buffer(raw_buffer, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(''))
        self.mock_event_callback.assert_any_call(first_msg, None, {})
        self.mock_response_callback.assert_any_call(second_msg, None, {})

    def test_given_unknown_message_when_parse_buffer_then_no_callback(self):
        msg = "unknown: message" + MESSAGE_DELIMITER

        unparsed_buffer = parse_buffer(msg, self.mock_event_callback, self.mock_response_callback)

        assert_that(unparsed_buffer, equal_to(''))
        assert_that(self.mock_event_callback.call_count, equal_to(0))
        assert_that(self.mock_response_callback.call_count, equal_to(0))
