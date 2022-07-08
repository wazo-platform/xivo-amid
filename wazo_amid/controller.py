# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from threading import Thread

from wazo_auth_client import Client as AuthClient
from wazo_amid.ami.client import AMIClient
from wazo_amid.bus.client import BusClient
from wazo_amid import auth
from wazo_amid import rest_api
from wazo_amid.facade import EventHandlerFacade
from xivo.status import StatusAggregator, TokenStatus
from xivo.token_renewer import TokenRenewer

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config):
        self._config = config
        self._token_renewer = TokenRenewer(AuthClient(**self._config['auth']))
        self._token_status = TokenStatus()
        self._status_aggregator = StatusAggregator()

    def run(self):
        self._token_renewer.subscribe_to_token_change(
            self._token_status.token_change_callback
        )
        self._status_aggregator.add_provider(self._token_status.provide_status)
        if self._config['publish_ami_events']:
            ami_client = AMIClient(**self._config['ami'])
            bus_client = BusClient(self._config)
            facade = EventHandlerFacade(ami_client, bus_client)
            self._status_aggregator.add_provider(ami_client.provide_status)
            self._status_aggregator.add_provider(bus_client.provide_status)
            ami_thread = Thread(target=facade.run, name='ami_thread')
            ami_thread.start()
            try:
                self._run_rest_api()
            finally:
                logger.debug('stopping facade...')
                facade.stop()
                logger.debug('facade stopped.')
                logger.debug('joining ami thread...')
                ami_thread.join()
                logger.debug('ami thread joined')
        else:
            self._run_rest_api()

    def _run_rest_api(self):
        rest_api.configure(self._config, self._status_aggregator)
        if not rest_api.app.config['auth'].get('master_tenant_uuid'):
            self._token_renewer.subscribe_to_next_token_details_change(
                auth.init_master_tenant
            )
        self._token_renewer.subscribe_to_next_token_details_change(
            lambda t: self._token_renewer.emit_stop()
        )
        with self._token_renewer:
            rest_api.run(self._config['rest_api'])

    def stop(self, reason):
        logger.warning('Stopping wazo-amid: %s', reason)
        rest_api.stop()
