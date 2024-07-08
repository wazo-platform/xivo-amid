#!/usr/bin/env python3
# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

setup(
    name="wazo-amid",
    version="0.1",
    description="Wazo AMI daemon",
    author="Wazo Authors",
    author_email="dev@wazo.community",
    url="http://wazo.community",
    license="GPLv3",
    packages=find_packages(),
    package_data={"wazo_amid.plugins": ["*/api.yml"]},
    scripts=["bin/wazo-amid"],
    entry_points={
        'wazo_amid.plugins': [
            'api = wazo_amid.plugins.api.plugin:Plugin',
            'actions = wazo_amid.plugins.actions.plugin:Plugin',
            'commands = wazo_amid.plugins.commands.plugin:Plugin',
            'config = wazo_amid.plugins.config.plugin:Plugin',
            'status = wazo_amid.plugins.status.plugin:Plugin',
        ],
    },
)
