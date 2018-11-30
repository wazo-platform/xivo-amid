# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import signal

from functools import partial
from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from xivo_ami.config import load_config
from xivo_ami.controller import Controller

logger = logging.getLogger(__name__)


def main():
    config = load_config()

    setup_logging(config['logfile'], config['foreground'], config['debug'])

    if config.get('user'):
        change_user(config['user'])

    controller = Controller(config)
    signal.signal(signal.SIGTERM, partial(sigterm, controller))

    with pidfile_context(config['pidfile'], config['foreground']):
        controller.run()


def sigterm(controller, signum, frame):
    controller.stop(reason='SIGTERM')


if __name__ == '__main__':
    main()
