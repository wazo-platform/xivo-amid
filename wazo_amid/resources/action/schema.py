# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, Schema


class Command(Schema):
    command = fields.String(required=True)


command_schema = Command()
