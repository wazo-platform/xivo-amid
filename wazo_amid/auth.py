# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from werkzeug.local import LocalProxy as Proxy
from xivo.auth_verifier import required_acl as required_acl_
from xivo.auth_verifier import required_tenant

from .exceptions import NotInitializedException
from .rest_api import app

if TYPE_CHECKING:
    from wazo_auth_client.types import TokenDict

    F = TypeVar('F')

required_acl = required_acl_


def required_master_tenant() -> Callable[[F], F]:
    return required_tenant(master_tenant_uuid)


def init_master_tenant(token: TokenDict) -> None:
    tenant_uuid = token['metadata']['tenant_uuid']
    app.config['auth']['master_tenant_uuid'] = tenant_uuid


def get_master_tenant_uuid() -> str:
    if not app:
        raise Exception('Flask application not configured')

    tenant_uuid = app.config['auth'].get('master_tenant_uuid')
    if not tenant_uuid:
        raise NotInitializedException()
    return tenant_uuid


master_tenant_uuid = Proxy(get_master_tenant_uuid)
