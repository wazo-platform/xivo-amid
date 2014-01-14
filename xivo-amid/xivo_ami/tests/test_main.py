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

from mock import sentinel
import unittest
import collections

from xivo_ami.main import _process_messages


class TestMain(unittest.TestCase):

    def test_given_events_in_queue_when_process_messages_then_queue_is_emptied(self):
        queue = collections.deque()
        queue.append(sentinel.event1)
        queue.append(sentinel.event2)

        _process_messages(queue)

        self.assertFalse(queue)
