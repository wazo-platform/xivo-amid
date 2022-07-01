# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.auth_verifier import no_auth
from wazo_amid.rest_api import AuthResource


class Status(AuthResource):
    @classmethod
    def configure(cls, status_aggregator):
        cls.status_aggregator = status_aggregator

    @no_auth
    def get(self):
        return self.status_aggregator.status(), 200
