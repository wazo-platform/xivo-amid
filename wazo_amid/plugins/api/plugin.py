# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import APIResource


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        api.add_resource(APIResource, '/api/api.yml')
