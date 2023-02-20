#!/usr/bin/env python3
# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages

setup(
    name="wazo-amid",
    version="0.1",
    description="Wazo AMI daemon",
    author="Wazo Authors",
    author_email="dev@wazo.community",
    url="http://wazo.community",
    license="GPLv3",
    packages=find_packages(),
    package_data={"wazo_amid.resources.api": ["*.yml"]},
    scripts=["bin/wazo-amid"],
    entry_points={
        'wazo_amid.plugins': [
            'api = wazo_amid.plugins.api.plugin:Plugin',
            'actions = wazo_amid.plugins.actions.plugin:Plugin',
        ],
    }
)
