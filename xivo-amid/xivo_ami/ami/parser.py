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

import logging

logger = logging.getLogger(__name__)


class AMIParsingError(Exception):
    pass


def parse_buffer(raw_buffer, event_callback, response_callback):
    unparsed_buffer = raw_buffer
    while unparsed_buffer:
        head, sep, unparsed_buffer = unparsed_buffer.partition('\r\n\r\n')
        if not sep:
            unparsed_buffer = head
            break

        try:
            _parse_msg(head, event_callback, response_callback)
        except Exception as e:
            logger.error('Could not parse message: %s', e)
            continue

    return unparsed_buffer


def _parse_msg(data, event_callback, response_callback):
    lines = data.split('\r\n')
    if not _is_valid_message(lines):
        raise AMIParsingError('unexpected data: %r' % data)

    first_header, first_value = _parse_line(lines[0])

    headers = {}
    for line in lines[1:]:
        header, value = _parse_line(line)
        headers[header] = value

    if first_header.startswith('Response'):
        callback = response_callback
    elif first_header.startswith('Event'):
        callback = event_callback
    else:
        raise AMIParsingError('unexpected data: %r' % data)

    if callback:
        callback(first_value, headers.get('ActionID'), headers)


def _parse_line(line):
    header, value = line.split(':', 1)
    value = value.lstrip()
    return header, value


def _is_valid_message(lines):
    return (lines
            and _is_colon_in_each_line(lines))


def _is_colon_in_each_line(lines):
    for line in lines:
        if ':' not in line:
            return False
    return True
