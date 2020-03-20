# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo import rest_api_helpers

logger = logging.getLogger(__name__)


APIException = rest_api_helpers.APIException


class ValidationError(APIException):
    def __init__(self, errors):
        super().__init__(
            status_code=400,
            message='Sent data is invalid',
            error_id='invalid-data',
            details=errors,
        )
