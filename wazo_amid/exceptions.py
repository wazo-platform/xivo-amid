# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging

from xivo.rest_api_helpers import APIException

logger = logging.getLogger(__name__)


class ValidationError(APIException):
    def __init__(self, errors: list[str | bytes]) -> None:
        super().__init__(
            status_code=400,
            message='Sent data is invalid',
            error_id='invalid-data',
            details=errors,
        )


class NotInitializedException(APIException):
    def __init__(self) -> None:
        msg = 'wazo-amid is not initialized'
        super().__init__(503, msg, 'not-initialized')
