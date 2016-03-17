# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2016 Avencall
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

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy
from xivo.http_helpers import DEFAULT_CIPHERS


_DAEMONNAME = 'xivo-amid'
_DEFAULT_CONFIG = {
    'user': 'xivo-amid',
    'debug': False,
    'foreground': False,
    'pidfile': '/var/run/{0}/{0}.pid'.format(_DAEMONNAME),
    'logfile': '/var/log/{}.log'.format(_DAEMONNAME),
    'config_file': '/etc/{}/config.yml'.format(_DAEMONNAME),
    'extra_config_files': '/etc/{}/conf.d/'.format(_DAEMONNAME),
    'publish_ami_events': True,
    'ajam': {'host': 'localhost',
             'port': 5040,
             'verify_certificate': '/usr/share/xivo-certs/server.crt',
             'username': 'xivo_amid',
             'password': 'default_password'},
    'ami': {'host': 'localhost',
            'port': 5038,
            'username': 'xivo_amid',
            'password': 'default'},
    'auth': {'host': 'localhost',
             'port': 9497},
    'bus': {'host': 'localhost',
            'port': 5672,
            'username': 'guest',
            'password': 'guest',
            'vhost': '/',
            'exchange_name': 'xivo',
            'exchange_type': 'topic',
            'exchange_durable': True},
    'rest_api': {'https': {'listen': '0.0.0.0',
                           'port': 9491,
                           'certificate': '/usr/share/xivo-certs/server.crt',
                           'private_key': '/usr/share/xivo-certs/server.key',
                           'ciphers': DEFAULT_CIPHERS},
                 'cors': {'enabled': True,
                          'allow_headers': 'Content-Type, X-Auth-Token'}},
}


def _get_cli_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
                        help="Foreground, don't daemonize. Default: %(default)s")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help="Enable debug messages. Default: %(default)s")
    parser.add_argument('--logfile', action='store', help='The path of the logfile')
    parser.add_argument('--pidfile', action='store', help='The path of the pidfile')
    parser.add_argument('-u',
                        '--user',
                        action='store',
                        help="The owner of the process.")
    parser.add_argument('-c',
                        '--config-file',
                        action='store',
                        help="The path where is the config file.")
    parser.add_argument('--disable-bus',
                        action='store_true',
                        help="Disable AMI message to BUS. Default: %(default)s")
    parsed_args = parser.parse_args()

    config = {}

    if parsed_args.logfile:
        config['logfile'] = parsed_args.logfile
    if parsed_args.pidfile:
        config['pidfile'] = parsed_args.pidfile
    if parsed_args.foreground:
        config['foreground'] = parsed_args.foreground
    if parsed_args.debug:
        config['debug'] = parsed_args.debug
    if parsed_args.user:
        config['user'] = parsed_args.user
    if parsed_args.disable_bus:
        config['publish_ami_events'] = not parsed_args.disable_bus
    if parsed_args.config_file:
        config['config_file'] = parsed_args.config_file

    return config


def load_config():
    cli_config = _get_cli_config()
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    return ChainMap(cli_config, file_config, _DEFAULT_CONFIG)
