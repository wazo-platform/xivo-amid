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

    try:
        first_header, first_value = _parse_line(lines.pop(0))
        headers = _parse_msg_body(lines, first_header, first_value)
    except AMIParsingError as e:
        raise AMIParsingError('unexpected data: %r. Details: %s' % (data, e))

    if first_header.startswith('Event'):
        callback = event_callback
    elif first_header.startswith('Response'):
        callback = response_callback
    else:
        raise AMIParsingError('unexpected first header: %r' % data)

    if callback:
        callback(first_value, headers.get('ActionID'), dict(headers.items()))


def _parse_msg_body(lines, first_header, first_value):
    headers = {}
    chan_variables = {}

    headers[first_header] = first_value
    for line in lines:
        header, value = _parse_line(line)
        if header == 'ChanVariable':
            variable, value = _parse_chan_variable(value)
            chan_variables[variable] = value
        else:
            headers[header] = value

    if chan_variables:
        headers['ChanVariable'] = chan_variables

    return headers


@functools.lru_cache(maxsize=8192)
def _parse_line(line):
    try:
        header, value = line.split(': ', 1)
    except ValueError:
        try:
            header, value = line.split(':', 1)
        except ValueError:
            raise AMIParsingError('unexpected line: %r' % line)
    return header, value


@functools.lru_cache(maxsize=8192)
def _parse_chan_variable(chan_variable):
    try:
        variable, value = chan_variable.split('=', 1)
    except ValueError:
        raise AMIParsingError('unexpected channel variable: %r' % chan_variable)
    return variable, value
