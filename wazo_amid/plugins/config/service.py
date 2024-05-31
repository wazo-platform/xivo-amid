# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import threading


class ConfigService:

    # Changing root logger log-level requires application-wide lock.
    # This lock will be shared across all instances.
    _lock = threading.Lock()

    def __init__(self, config):
        self._config = dict(config)
        self._enabled = False

    def get_config(self):
        with self._lock:
            return dict(self._config)