#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import fnmatch
import os

from distutils.core import setup

packages = [
    package for package, _, _ in os.walk('xivo_ami')
    if not fnmatch.fnmatch(package, '*tests')
]

setup(
    name='xivo-amid',
    version='0.1',
    description='XiVO ami event server',
    author='Avencall',
    author_email='dev@avencall.com',
    url='https://github.com/xivo-pbx/xivo-amid',
    license='GPLv3',
    packages=packages,
    scripts=['bin/xivo-amid'],
)
