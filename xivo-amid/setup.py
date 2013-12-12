#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='xivo-amid',
    version='0.1',
    description='XiVO ami event server',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.fr/',
    license='GPLv3',
    packages=['xivo_amid',
              'xivo_amid.bin'],
    scripts=['bin/xivo-amid'],
)
