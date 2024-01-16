# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import TYPE_CHECKING

from wazo_bus.publisher import BusPublisherWithQueue
from wazo_bus.resources.ami.event import AMIEvent
from xivo.status import Status, StatusDict

if TYPE_CHECKING:
    from ..ami.client import Message
    from ..config import BusConfigDict


class BusClient(BusPublisherWithQueue):
    @classmethod
    def from_config(cls, service_uuid: str, bus_config: BusConfigDict) -> BusClient:
        name = 'wazo-amid'
        return cls(name=name, service_uuid=service_uuid, **bus_config)

    def provide_status(self, status: StatusDict) -> None:
        status['bus_publisher']['status'] = (
            Status.ok if self.queue_publisher_connected() else Status.fail
        )

    def publish(self, *messages: Message) -> None:
        for message in messages:
            super().publish_soon(AMIEvent(message.name, message.headers))
