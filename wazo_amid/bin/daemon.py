# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal

from functools import partial
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from wazo_amid.config import load_config
from wazo_amid.controller import Controller

logger = logging.getLogger(__name__)


def main():
    config = load_config()

    setup_logging(config['logfile'], debug=config['debug'])

    if config.get('user'):
        change_user(config['user'])

    controller = Controller(config)
    signal.signal(signal.SIGTERM, partial(sigterm, controller))

    controller.run()


def sigterm(controller, signum, frame):
    controller.stop(reason='SIGTERM')


if __name__ == '__main__':
    main()
