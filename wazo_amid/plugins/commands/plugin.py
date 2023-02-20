# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import CommandResource


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        ajam_client = dependencies['ajam_client']

        api.add_resource(
            CommandResource,
            '/action/Command',
            resource_class_args=[ajam_client],
        )
