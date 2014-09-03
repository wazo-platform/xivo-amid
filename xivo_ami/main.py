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

import argparse
import logging
import signal

from xivo.daemonize import pidfile_context
from xivo.xivo_logging import setup_logging
from xivo_ami.ami.client import AMIClient
from xivo_ami.bus.client import BusClient
from xivo_ami.facade import EventHandlerFacade
from xivo_bus.ctl.producer import BusProducer

_LOG_FILENAME = '/var/log/xivo-amid.log'
_PID_FILENAME = '/var/run/xivo-amid.pid'

logger = logging.getLogger(__name__)


def main():
    parsed_args = _parse_args()

    setup_logging(_LOG_FILENAME, parsed_args.foreground, parsed_args.verbose)

    with pidfile_context(_PID_FILENAME, parsed_args.foreground):
        logger.info('Starting xivo-amid')
        try:
            _run()
        except Exception:
            logger.exception('Unexpected error:')
        logger.info('Stopping xivo-amid')


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--foreground', action='store_true',
                        help='run in foreground')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    return parser.parse_args()


def _run():
    _init_signal()
    ami_client = AMIClient('localhost', 'xivo_amid', 'eeCho8ied3u')
    bus_producer = BusProducer()
    bus_client = BusClient(bus_producer)
    facade = EventHandlerFacade(ami_client, bus_client)
    facade.run()


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _handle_sigterm(signum, frame):
    raise SystemExit()


if __name__ == '__main__':
    main()
