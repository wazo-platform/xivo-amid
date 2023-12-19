# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging
import signal

from functools import partial
from types import FrameType

from xivo.config_helper import set_xivo_uuid
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from wazo_amid.config import load_config
from wazo_amid.controller import Controller

logger = logging.getLogger(__name__)


def main() -> None:
    config = load_config()

    setup_logging(config['logfile'], debug=config['debug'])

    if config.get('user'):
        change_user(config['user'])

    set_xivo_uuid(config, logger)

    controller = Controller(config)
    signal.signal(signal.SIGTERM, partial(_signal_handler, controller))
    signal.signal(signal.SIGINT, partial(_signal_handler, controller))

    controller.run()


def _signal_handler(controller: Controller, signum: int, frame: FrameType) -> None:
    controller.stop(reason=signal.Signals(signum).name)


if __name__ == '__main__':
    main()
