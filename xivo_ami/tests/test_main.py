# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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

from mock import Mock, patch
from mock import sentinel
from unittest import TestCase

from xivo_ami import main
from xivo_ami import config


USER = 'www-data'


class TestMain(TestCase):

    def setUp(self):
        self.config = Mock(config.ConfigXivoAMId)
        self.argparse_patch = patch('argparse.ArgumentParser')
        self.daemon_patch = patch('xivo.daemonize.daemonize')
        self.daemon_lock_patch = patch('xivo.daemonize.lock_pidfile_or_die')
        self.daemon_unlock_patch = patch('xivo.daemonize.unlock_pidfile')
        self.log_patch = patch('xivo_ami.main.setup_logging')
        self.user_patch = patch('xivo_ami.main.change_user')

        self.argparse = self.argparse_patch.start()
        self.daemonize = self.daemon_patch.start()
        self.daemon_lock = self.daemon_lock_patch.start()
        self.daemon_unlock = self.daemon_unlock_patch.start()
        self.log = self.log_patch.start()
        self.change_user = self.user_patch.start()

        self.args = self.argparse.return_value.parse_args.return_value
        self.args.foreground = False

    def tearDown(self):
        self.user_patch.stop()
        self.log_patch.stop()
        self.daemon_unlock_patch.stop()
        self.daemon_lock_patch.stop()
        self.daemon_patch.stop()
        self.argparse_patch.stop()

    @patch('xivo_ami.main.config_loader.fetch_and_merge_config')
    @patch('xivo_ami.main._run')
    def test_that_amid_has_a_pid_file(self, run_mock, config_get_mock):
        configuration = Mock(_PID_FILENAME=sentinel.pidfile)
        config_get_mock.return_value = configuration

        main.main()

        self.daemon_lock.assert_called_once_with(sentinel.pidfile)
        run_mock.assert_called_once_with(configuration)
        self.daemon_unlock.asssert_called_once_with(sentinel.pidfile)

    @patch('xivo_ami.main.config_loader.fetch_and_merge_config')
    @patch('xivo_ami.main._run', Mock())
    def test_when_arg_user_is_given_then_change_user(self, config_get_mock):
        config = Mock(user=sentinel.user)
        config_get_mock.return_value = config

        main.main()

        self.change_user.assert_called_once_with(sentinel.user)
