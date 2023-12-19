# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from wazo_amid.exceptions import APIException


class UnsupportedAction(APIException):
    def __init__(self, action: str) -> None:
        super().__init__(
            status_code=501,
            message='Action incompatible with wazo-amid',
            error_id='incompatible-action',
            details={'action': action},
        )
