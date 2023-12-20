# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from typing import Any, TypedDict, Union

logger = logging.getLogger(__name__)


ParserCallback = Callable[[str, Union[str, None], dict[str, Any]], None]


class AMIParsingError(Exception):
    pass


class ChanVariableDict(TypedDict):
    ChanVariable: dict[str, str]


def parse_buffer(
    raw_buffer: bytes,
    event_callback: ParserCallback,
    response_callback: ParserCallback | None,
) -> bytes:
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


def parse_command_response(raw_buffer: bytes) -> list[str]:
    lines = raw_buffer.decode('utf8', 'replace').split('\r\n')
    return [line[8:] for line in lines if line.startswith('Output: ')]


def _parse_msg(
    data: bytes,
    event_callback: ParserCallback,
    response_callback: ParserCallback | None,
) -> None:
    lines = data.decode('utf8', 'replace').split('\r\n')

    try:
        first_header, first_value = _parse_line(lines.pop(0))
        headers: dict[str, Any] = _parse_msg_body(lines, first_header, first_value)  # type: ignore
    except AMIParsingError as e:
        raise AMIParsingError(f'unexpected data: {data!r}. Details: {e}')

    if first_header.startswith('Event'):
        callback: ParserCallback | None = event_callback
    elif first_header.startswith('Response'):
        callback = response_callback
    else:
        raise AMIParsingError('unexpected first header: %r' % data)

    if callback is not None:
        callback(first_value, headers.get('ActionID'), dict(headers.items()))


def _parse_msg_body(
    lines: list[str], first_header: str, first_value: str
) -> dict[str, str] | ChanVariableDict:
    headers: dict[str, str] = {}
    chan_variables: dict[str, str] = {}

    headers[first_header] = first_value
    for line in lines:
        header, value = _parse_line(line)
        if header == 'ChanVariable':
            variable, value = _parse_chan_variable(value)
            chan_variables[variable] = value
        else:
            headers[header] = value

    if chan_variables:
        headers['ChanVariable'] = chan_variables  # type: ignore

    return headers


@functools.lru_cache(maxsize=8192)
def _parse_line(line: str) -> tuple[str, str]:
    try:
        header, value = line.split(': ', 1)
    except ValueError:
        try:
            header, value = line.split(':', 1)
        except ValueError:
            raise AMIParsingError('unexpected line: %r' % line)
    return header, value


@functools.lru_cache(maxsize=8192)
def _parse_chan_variable(chan_variable: str) -> tuple[str, str]:
    try:
        variable, value = chan_variable.split('=', 1)
    except ValueError:
        raise AMIParsingError('unexpected channel variable: %r' % chan_variable)
    return variable, value
