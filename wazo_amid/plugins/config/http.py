# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from flask import request
from jsonpatch import JsonPatch

from .schemas import config_patch_schema

from wazo_amid.auth import required_acl, required_master_tenant
from wazo_amid.rest_api import AuthResource


class ConfigResource(AuthResource):
    def __init__(self, config_service) -> None:
        self._config_service = config_service

    @required_master_tenant()
    @required_acl('amid.config.read')
    def get(self):
        return self._config_service.get_config(), 200

    @required_master_tenant()
    @required_acl('amid.config.update')
    def patch(self):
        config_patch = config_patch_schema.load(request.get_json(), many=True)
        config = self._config_service.get_config()
        patched_config = JsonPatch(config_patch).apply(config)
        self._config_service.update_config(patched_config)
        return self._config_service.get_config(), 200
