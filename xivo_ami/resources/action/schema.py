# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields, Schema
from marshmallow.validate import Length


class Command(Schema):
    command = fields.String(required=True)

command_schema = Command(strict=True)
