# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from .helpers import base as asset

if TYPE_CHECKING:
    from pytest import Config, FixtureRequest, Item, Session


def pytest_collection_modifyitems(
    session: Session, config: Config, items: list[Item]
) -> None:
    # item == test method
    # item.parent == test class
    # item.parent.own_markers == pytest markers of the test class
    # item.parent.own_markers[0].args[0] == name of the asset
    # It also removes the run-order pytest feature (--ff, --nf)
    items.sort(key=lambda item: item.parent.own_markers[0].args[0])


@pytest.fixture(scope='session')
def base() -> Generator[None, None, None]:
    asset.APIAssetLaunchingTestCase.setUpClass()
    try:
        yield
    finally:
        asset.APIAssetLaunchingTestCase.tearDownClass()


@pytest.fixture(autouse=True, scope='function')
def mark_logs(request: FixtureRequest) -> Generator[None, None, None]:
    test_name = f'{request.cls.__name__}.{request.function.__name__}'
    asset.APIAssetLaunchingTestCase.mark_logs_test_start(test_name)
    yield
    asset.APIAssetLaunchingTestCase.mark_logs_test_end(test_name)
