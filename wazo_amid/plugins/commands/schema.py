# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields
from xivo.mallow_helpers import Schema


class Command(Schema):
    command = fields.String(required=True)


command_schema = Command()
