# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_ami.ami.event import Event


class AMIParsingError(Exception):
    pass


def parse_msg(data):
    lines = data.split('\r\n')
    if not _is_valid_message(lines):
        raise AMIParsingError('unexpected data: %r' % data)

    first_header, first_value = _parse_line(lines[0])
    msg_factory = Event

    headers = {}
    for line in lines[1:]:
        header, value = _parse_line(line)
        headers[header] = value

    return msg_factory(first_value, headers.get('ActionID'), headers)


def _parse_line(line):
    header, value = line.split(':', 1)
    value = value.lstrip()
    return header, value


def _is_valid_message(lines):
    return (lines
            and lines[0].startswith('Event:')
            and _is_colon_in_each_line(lines))


def _is_colon_in_each_line(lines):
    for line in lines:
        if ':' not in line:
            return False
    return True
