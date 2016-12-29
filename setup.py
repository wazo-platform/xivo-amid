#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-amid',
    version='0.1',
    description='XiVO AMI adapter server',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='http://wazo.community',
    license='GPLv3',

    packages=find_packages(),
    package_data={
        'xivo_ami.resources.api': ['*.yml'],
    },
    scripts=['bin/xivo-amid'],
)
