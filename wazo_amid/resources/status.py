# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.auth_verifier import required_acl
from wazo_amid.rest_api import AuthResource


class Status(AuthResource):
    @classmethod
    def configure(cls, status_aggregator):
        cls.status_aggregator = status_aggregator

    @required_acl('amid.status.read')
    def get(self):
        return self.status_aggregator.status(), 200
