# Copyright 2012-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import logging

logger = logging.getLogger(__name__)


class AMIParsingError(Exception):
    pass


def parse_buffer(raw_buffer, event_callback, response_callback):
    unparsed_buffer = raw_buffer
    while unparsed_buffer:
        head, sep, unparsed_buffer = unparsed_buffer.partition(b'\r\n\r\n')
        if not sep:
            unparsed_buffer = head
            break

        try:
            _parse_msg(head, event_callback, response_callback)
        except AMIParsingError as e:
            logger.exception('Could not parse message: %s', e)
            continue

    return unparsed_buffer


def parse_command_response(raw_buffer):
    lines = raw_buffer.decode('utf8', 'replace').split('\r\n')
    return [line[8:] for line in lines if line.startswith('Output: ')]


def _parse_msg(data, event_callback, response_callback):
    lines = data.decode('utf8', 'replace').split('\r\n')

    headers = {}
    chan_variables = {}
    try:
        first_header, first_value = _parse_line(lines[0])

        headers[first_header] = first_value
        for line in lines[1:]:
            header, value = _parse_line(line)
            if header == 'ChanVariable':
                variable, value = _parse_chan_variable(value)
                chan_variables[variable] = value
            else:
                headers[header] = value
        if chan_variables:
            headers['ChanVariable'] = chan_variables

    except AMIParsingError:
        raise AMIParsingError('unexpected data: %r' % data)

    if first_header.startswith('Event'):
        callback = event_callback
    elif first_header.startswith('Response'):
        callback = response_callback
    else:
        raise AMIParsingError('unexpected data: %r' % data)

    if callback:
        callback(first_value, headers.get('ActionID'), dict(headers.items()))


@functools.lru_cache(maxsize=8192)
def _parse_line(line):
    try:
        header, value = line.split(':', 1)
    except ValueError:
        raise AMIParsingError()
    value = value.lstrip()
    return header, value


@functools.lru_cache(maxsize=8192)
def _parse_chan_variable(chan_variable):
    return chan_variable.split('=', 1)
