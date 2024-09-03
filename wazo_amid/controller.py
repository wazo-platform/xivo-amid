# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from threading import Thread
from typing import TYPE_CHECKING

from wazo_auth_client import Client as AuthClient
from xivo.status import StatusAggregator, TokenStatus
from xivo.token_renewer import TokenRenewer

from wazo_amid import auth, rest_api
from wazo_amid.ami.client import AMIClient
from wazo_amid.bus.client import BusClient
from wazo_amid.facade import EventHandlerFacade

if TYPE_CHECKING:
    from wazo_amid.config import AmidConfigDict

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: AmidConfigDict) -> None:
        self._config = config
        self._token_renewer = TokenRenewer(AuthClient(**self._config['auth']))
        self._token_status = TokenStatus()
        self._status_aggregator = StatusAggregator()
        self._stopping_thread: Thread | None = None

    def run(self) -> None:
        self._token_renewer.subscribe_to_token_change(
            self._token_status.token_change_callback
        )
        self._status_aggregator.add_provider(self._token_status.provide_status)
        if self._config['publish_ami_events']:
            uuid = self._config['uuid']
            ami_client = AMIClient(**self._config['ami'])
            bus_client = BusClient.from_config(uuid, self._config['bus'])
            facade = EventHandlerFacade(ami_client, bus_client)
            self._status_aggregator.add_provider(ami_client.provide_status)
            self._status_aggregator.add_provider(bus_client.provide_status)
            ami_thread = Thread(target=facade.run, name='ami_thread')
            ami_thread.start()
            try:
                with bus_client:
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

    def _run_rest_api(self) -> None:
        rest_api.configure(self._config, self._status_aggregator)
        if not rest_api.app.config['auth'].get('master_tenant_uuid'):
            self._token_renewer.subscribe_to_next_token_details_change(
                auth.init_master_tenant
            )
        self._token_renewer.subscribe_to_next_token_details_change(
            lambda t: self._token_renewer.emit_stop()
        )
        try:
            with self._token_renewer:
                rest_api.run(self._config['rest_api'])
        finally:
            if self._stopping_thread:
                self._stopping_thread.join()

    def stop(self, reason: str) -> None:
        logger.warning('Stopping wazo-amid: %s', reason)
        self._stopping_thread = Thread(target=rest_api.stop, name=reason)
        self._stopping_thread.start()
