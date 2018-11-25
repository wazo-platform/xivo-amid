#!/usr/bin/env python3
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-amid',
    version='0.1',
    description='XiVO AMI adapter server',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',

    packages=find_packages(),
    package_data={
        'xivo_ami.resources.api': ['*.yml'],
    },
    scripts=['bin/xivo-amid'],
)
