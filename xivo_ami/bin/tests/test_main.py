# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from mock import Mock, patch, ANY
from unittest import TestCase

from xivo.chain_map import ChainMap
from xivo_ami.bin.daemon import main


USER = 'www-data'

default_config = {
    'logfile': 'default_logfile',
    'foreground': False,
    'debug': False,
    'pidfile': 'default_pidfile',
}


class TestMain(TestCase):

    def setUp(self):
        self.daemon_patch = patch('xivo.daemonize.daemonize')
        self.daemon_lock_patch = patch('xivo.daemonize.lock_pidfile_or_die')
        self.daemon_unlock_patch = patch('xivo.daemonize.unlock_pidfile')
        self.log_patch = patch('xivo_ami.bin.daemon.setup_logging')
        self.user_patch = patch('xivo_ami.bin.daemon.change_user')

        self.daemonize = self.daemon_patch.start()
        self.daemon_lock = self.daemon_lock_patch.start()
        self.daemon_unlock = self.daemon_unlock_patch.start()
        self.log = self.log_patch.start()
        self.change_user = self.user_patch.start()

    def tearDown(self):
        self.user_patch.stop()
        self.log_patch.stop()
        self.daemon_unlock_patch.stop()
        self.daemon_lock_patch.stop()
        self.daemon_patch.stop()

    @patch('xivo_ami.bin.daemon.load_config',
           Mock(return_value=ChainMap({'pidfile': 'pidfile'}, default_config)))
    @patch('xivo_ami.bin.daemon.Controller')
    def test_that_amid_has_a_pid_file(self, controller_init_mock):
        main()

        controller_init_mock.assert_called_once_with(ANY)
        self.daemon_lock.assert_called_once_with('pidfile')
        controller_init_mock.return_value.run.assert_called_once_with()
        self.daemon_unlock.asssert_called_once_with('pidfile')

    @patch('xivo_ami.bin.daemon.load_config',
           Mock(return_value=ChainMap({'user': 'foobar'}, default_config)))
    @patch('xivo_ami.bin.daemon.Controller', Mock())
    def test_when_arg_user_is_given_then_change_user(self):
        main()

        self.change_user.assert_called_once_with('foobar')
