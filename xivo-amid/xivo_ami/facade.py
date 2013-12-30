# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

import collections
import time
from xivo_ami.ami.client import AMIConnectionError
from xivo_ami.bus.client import BusConnectionError


class EventHandlerFacade(object):

    RECONNECTION_DELAY = 5

    def __init__(self, ami_client, bus_client, event_handler_callback):
        self._ami_client = ami_client
        self._bus_client = bus_client
        self._event_queue = collections.deque()
        self._event_handler_callback = event_handler_callback

    def run(self):
        try:
            self._bus_client.connect()
            self._ami_client.connect_and_login()
            self._process_messages()
        except AMIConnectionError:
            self._handle_ami_connection_error()
        except BusConnectionError:
            self._handle_bus_connection_error()
        except Exception as e:
            self._handle_unexpected_error(e)

    def _handle_ami_connection_error(self):
        self._ami_client.disconnect()
        time.sleep(self.RECONNECTION_DELAY)
        self._ami_client.connect_and_login()

    def _handle_bus_connection_error(self):
        self._bus_client.disconnect()
        time.sleep(self.RECONNECTION_DELAY)
        self._bus_client.connect()

    def _handle_unexpected_error(self, e):
        self._ami_client.disconnect()
        raise e

    def _process_messages(self):
        new_messages = self._ami_client.parse_next_messages()
        self._event_queue.extend(new_messages)
        self._event_handler_callback(self._event_queue)
