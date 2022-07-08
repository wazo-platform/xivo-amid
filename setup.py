#!/usr/bin/env python3
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)

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
)
