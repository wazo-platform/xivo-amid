# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Any

import requests
from flask import request

from wazo_amid.ami import parser
from wazo_amid.auth import required_acl, required_master_tenant
from wazo_amid.plugin_helpers.ajam import AJAMClient, AJAMUnreachable
from wazo_amid.rest_api import AuthResource

class ConfigResource(AuthResource):
    
    def __init__(self, config_service):
        self._config_service = config_service
    
    @required_master_tenant()
    @required_acl('amid.config.read')
    def get(self):
        return self._config_service.get_config(), 200
    
    def patch(self):
        return '', 200