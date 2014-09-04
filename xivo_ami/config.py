# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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
import os
import yaml

from xivo_bus.ctl.config import BusConfig

_DAEMONNAME = 'xivo-amid'
_CONF_FILENAME = '{}.yml'.format(_DAEMONNAME)


class ConfigXivoAMId(object):

    _LOG_FILENAME = '/var/log/{}.log'.format(_DAEMONNAME)
    _PID_FILENAME = '/var/run/{daemon}/{daemon}.pid'.format(daemon=_DAEMONNAME)
    _SOCKET_FILENAME = '/tmp/{}.sock'.format(_DAEMONNAME)

    def __init__(self, adict):
        self._update_config(adict)

    def _update_config(self, adict):
        self.__dict__.update(adict)
        for k, v in adict.items():
            if isinstance(v, dict):
                self.__dict__[k] = ConfigXivoAMId(v)

    @property
    def ajam_url(self):
        return 'http://%(host)s:%(port)s/rawman' % self.ajam.__dict__

    @property
    def bus_config_obj(self):
        bus_config_obj = BusConfig(host=config.bus.host,
                                   port=config.bus.port,
                                   virtual_host=config.bus.vhost,
                                   username=config.bus.username,
                                   password=config.bus.password)
        return bus_config_obj


def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
                        default=False,
                        help="Foreground, don't daemonize. Default: %(default)s")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=False,
                        help="Enable debug messages. Default: %(default)s")
    parser.add_argument('-u',
                        '--user',
                        action='store',
                        help="The owner of the process.")
    parser.add_argument('-c',
                        '--config_path',
                        action='store',
                        default="/etc/xivo/xivo-amid",
                        help="The path where is the config file. Default: %(default)s")
    parser.add_argument('--disable-bus',
                        action='store_true',
                        default=False,
                        help="Disable AMI message to BUS. Default: %(default)s")
    return parser.parse_args()


def _get_config_raw(config_path):
    path = os.path.join(config_path, _CONF_FILENAME)
    with open(path) as fobj:
        return yaml.load(fobj)

args_parsed = configure()
config = ConfigXivoAMId(_get_config_raw(args_parsed.config_path))
config._update_config(vars(args_parsed))
