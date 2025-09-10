from __future__ import annotations

import importlib.metadata

import save_and_restore_api as m


def test_version():
    assert importlib.metadata.version("save_and_restore_api") == m.__version__
