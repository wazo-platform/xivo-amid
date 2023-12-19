# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging
import threading
from collections import deque
from typing import NoReturn

from wazo_amid.ami.client import AMIConnectionError, AMIClient, Message
from wazo_amid.bus.client import BusClient

logger = logging.getLogger(__name__)


class EventHandlerFacade:
    RECONNECTION_DELAY = 5

    def __init__(self, ami_client: AMIClient, bus_client: BusClient) -> None:
        self._ami_client = ami_client
        self._bus_client = bus_client
        self._stop_event = threading.Event()

    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._ami_client.connect_and_login()
                self._process_messages_indefinitely()
            except AMIConnectionError as e:
                self._handle_ami_connection_error(e)
            except Exception as e:
                self._handle_unexpected_error(e)

    def _handle_ami_connection_error(self, e: AMIConnectionError) -> None:
        self._ami_client.disconnect(reason=e.error)
        self._stop_event.wait(timeout=self.RECONNECTION_DELAY)

    def _handle_unexpected_error(self, e: Exception) -> NoReturn:
        self._ami_client.disconnect(reason=f'Unexpected error: {e}')
        raise

    def _process_messages_indefinitely(self) -> None:
        while not self._stop_event.is_set():
            new_messages = self._ami_client.parse_next_messages()
            self._process_messages(new_messages)

    def _process_messages(self, messages: deque[Message]) -> None:
        while len(messages):
            message = messages.pop()
            logger.debug('Processing message %s', message)
            self._bus_client.publish(message)

    def stop(self) -> None:
        self._stop_event.set()
        self._ami_client.stop()
