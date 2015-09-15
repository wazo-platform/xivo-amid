#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-amid',
    version='0.1',
    description='XiVO AMI adapter server',
    author='Avencall',
    author_email='dev@avencall.com',
    url='https://github.com/xivo-pbx/xivo-amid',
    license='GPLv3',

    packages=find_packages(),
    package_data={
        'xivo_ami.resources.api': ['*.json'],
    },
    scripts=['bin/xivo-amid'],
)
