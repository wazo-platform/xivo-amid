# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import TYPE_CHECKING

from .http import CommandResource

if TYPE_CHECKING:
    from wazo_amid.rest_api import PluginDependencies


class Plugin:
    def load(self, dependencies: PluginDependencies) -> None:
        api = dependencies['api']
        ajam_client = dependencies['ajam_client']

        api.add_resource(
            CommandResource,
            '/action/Command',
            resource_class_args=[ajam_client],
        )
