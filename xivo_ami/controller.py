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

import logging

from threading import Thread
from xivo_ami.ami.client import AMIClient
from xivo_ami.bus.client import BusClient
from xivo_ami import rest_api
from xivo_ami.facade import EventHandlerFacade

logger = logging.getLogger(__name__)


class Controller(object):

    def __init__(self, config):
        self._config = config

    def run(self):
        if self._config['publish_ami_events']:
            ami_client = AMIClient(**self._config['ami'])
            bus_client = BusClient(self._config)
            facade = EventHandlerFacade(ami_client, bus_client)
            ami_thread = Thread(target=facade.run, name='ami_thread')
            ami_thread.start()
            try:
                self._run_rest_api()
            finally:
                facade.stop()
                ami_thread.join()
        else:
            self._run_rest_api()

    def _run_rest_api(self):
        rest_api.configure(self._config)
        rest_api.run(self._config['rest_api'])
