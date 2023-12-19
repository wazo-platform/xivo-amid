# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import TYPE_CHECKING

from xivo.auth_verifier import required_acl

from wazo_amid.rest_api import AuthResource

if TYPE_CHECKING:
    from xivo.status import StatusAggregator, StatusDict


class StatusResource(AuthResource):
    def __init__(self, status_aggregator: StatusAggregator) -> None:
        self.status_aggregator = status_aggregator

    @required_acl('amid.status.read')
    def get(self) -> tuple[StatusDict, int]:
        return self.status_aggregator.status(), 200
