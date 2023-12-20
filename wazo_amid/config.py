# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
from typing import Any, Literal, TypedDict

from xivo.chain_map import ChainMap
from xivo.config_helper import parse_config_file, read_config_file_hierarchy


class ServiceConfigDict(TypedDict):
    host: str
    port: int
    username: str
    password: str


class AjamCofigDict(ServiceConfigDict):
    https: bool


class AuthConfigDict(TypedDict):
    host: str
    port: int
    prefix: str | None
    https: bool
    key_file: str


class BusConfigDict(ServiceConfigDict):
    vhost: str
    exchange_name: str
    exchange_type: Literal['headers']


class CorsConfigDict(TypedDict):
    enabled: bool
    allow_headers: list[str]


class RestApiConfigDict(TypedDict):
    listen: str
    port: int
    certificate: str | None
    private_key: str | None
    cors: CorsConfigDict
    max_threads: int


class AmidConfigDict(TypedDict):
    uuid: str
    user: str
    debug: bool
    logfile: str
    config_file: str
    extra_config_files: str
    publish_ami_events: bool
    ajam: AjamCofigDict
    ami: ServiceConfigDict
    auth: AuthConfigDict
    bus: BusConfigDict
    rest_api: RestApiConfigDict
    enabled_plugins: dict[str, bool]


_DAEMONNAME = 'wazo-amid'
_DEFAULT_CONFIG: AmidConfigDict = {  # type: ignore
    'user': 'wazo-amid',
    'debug': False,
    'logfile': f'/var/log/{_DAEMONNAME}.log',
    'config_file': f'/etc/{_DAEMONNAME}/config.yml',
    'extra_config_files': f'/etc/{_DAEMONNAME}/conf.d/',
    'publish_ami_events': True,
    'ajam': {
        'host': 'localhost',
        'port': 5039,
        'https': False,
        'username': 'wazo_amid',
        'password': 'default_password',
    },
    'ami': {
        'host': 'localhost',
        'port': 5038,
        'username': 'wazo_amid',
        'password': 'default',
    },
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'prefix': None,
        'https': False,
        'key_file': '/var/lib/wazo-auth-keys/wazo-amid-key.yml',
    },
    'bus': {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest',
        'vhost': '/',
        'exchange_name': 'wazo-headers',
        'exchange_type': 'headers',
    },
    'rest_api': {
        'listen': '127.0.0.1',
        'port': 9491,
        'certificate': None,
        'private_key': None,
        'cors': {'enabled': True, 'allow_headers': ['Content-Type', 'X-Auth-Token']},
        'max_threads': 10,
    },
    'enabled_plugins': {
        'api': True,
        'actions': True,
        'commands': True,
        'status': True,
    },
}


def _get_cli_config() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug messages. Default: %(default)s",
    )
    parser.add_argument('--logfile', action='store', help='The path of the logfile')
    parser.add_argument(
        '-u', '--user', action='store', help="The owner of the process."
    )
    parser.add_argument(
        '-c', '--config-file', action='store', help="The path where is the config file."
    )
    parser.add_argument(
        '--disable-bus',
        action='store_true',
        help="Disable AMI message to BUS. Default: %(default)s",
    )
    parsed_args = parser.parse_args()

    config = {}

    if parsed_args.logfile:
        config['logfile'] = parsed_args.logfile
    if parsed_args.debug:
        config['debug'] = parsed_args.debug
    if parsed_args.user:
        config['user'] = parsed_args.user
    if parsed_args.disable_bus:
        config['publish_ami_events'] = not parsed_args.disable_bus
    if parsed_args.config_file:
        config['config_file'] = parsed_args.config_file

    return config


def _load_key_file(config: dict[str, Any]) -> dict[str, Any]:
    if config['auth'].get('username') and config['auth'].get('password'):
        return {}

    key_file = parse_config_file(config['auth']['key_file'])
    return {
        'auth': {
            'username': key_file['service_id'],
            'password': key_file['service_key'],
        }
    }


def load_config() -> AmidConfigDict:
    cli_config = _get_cli_config()
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(cli_config, file_config, _DEFAULT_CONFIG))
    return ChainMap(cli_config, service_key, file_config, _DEFAULT_CONFIG)
