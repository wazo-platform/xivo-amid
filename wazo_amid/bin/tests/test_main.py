# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from unittest.mock import Mock, patch

from xivo.chain_map import ChainMap

from wazo_amid.bin.daemon import main

USER = 'wazo-amid'

default_config = {
    'logfile': 'default_logfile',
    'debug': False,
}


class TestMain(TestCase):
    def setUp(self):
        self.log_patch = patch('wazo_amid.bin.daemon.setup_logging')
        self.user_patch = patch('wazo_amid.bin.daemon.change_user')
        self.set_xivo_uuid = patch('wazo_amid.bin.daemon.set_xivo_uuid')

        self.log = self.log_patch.start()
        self.change_user = self.user_patch.start()
        self.set_xivo_uuid = self.set_xivo_uuid.start()

    def tearDown(self):
        self.user_patch.stop()
        self.log_patch.stop()
        self.set_xivo_uuid.stop()

    @patch(
        'wazo_amid.bin.daemon.load_config',
        Mock(return_value=ChainMap({'user': 'foobar'}, default_config)),
    )
    @patch('wazo_amid.bin.daemon.Controller', Mock())
    def test_when_arg_user_is_given_then_change_user(self):
        main()

        self.change_user.assert_called_once_with('foobar')
