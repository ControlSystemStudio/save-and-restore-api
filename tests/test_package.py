from __future__ import annotations

import importlib.metadata

import save_and_restore_api as m
from save_and_restore_api import SaveRestoreAPI


def test_version():
    assert importlib.metadata.version("save_and_restore_api") == m.__version__


def test_import():
    from save_and_restore_api import SaveRestoreAPI  # noqa: F401


def test_comm():
    SR = SaveRestoreAPI(base_url="http://localhost:8080/save-restore", timeout=2)
    # SR.set_username_password(username="johndoe", password="1234")
    SR.set_username_password(username="user", password="userPass")
    # SR.set_username_password(username="admin", password="adminPass")
    SR.open()
    SR.login()
    SR.get_node(SR.ROOT_NODE_UID)
    SR.close()
