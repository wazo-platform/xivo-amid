# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from contextlib import contextmanager

from wazo_amid.exceptions import APIException


class AJAMUnreachable(APIException):
    def __init__(self, ajam_url, error):
        super().__init__(
            status_code=503,
            message='AJAM server unreachable',
            error_id='ajam-unreachable',
            details={'ajam_url': ajam_url, 'original_error': str(error)},
        )


class AJAMClient:
    logoff_params = {'action': 'logoff'}

    def __init__(
        self,
        host,
        port,
        username=None,
        password=None,
        https=True,
        verify_certificate=True,
    ):
        scheme = 'https' if https else 'http'
        self.url = f'{scheme}://{host}:{port}/rawman'
        self.login_params = {
            'action': 'login',
            'username': username,
            'secret': password,
        }
        self.verify = verify_certificate if https else None

    def get(self, action, ami_args):
        params = self._build_params(action, ami_args)
        with self._session() as session:
            return session.get(self.url, params=params)

    @contextmanager
    def _session(self):
        with requests.Session() as session:
            session.get(self.url, params=self.login_params, verify=self.verify)
            yield session
            session.get(self.url, params=self.logoff_params, verify=self.verify)

    def _build_params(self, action, ami_args):
        result = [('action', action)]
        for extra_arg_key, extra_arg_value in ami_args.items():
            if isinstance(extra_arg_value, list):
                result.extend([(extra_arg_key, value) for value in extra_arg_value])
            else:
                result.append((extra_arg_key, extra_arg_value))

        return result
