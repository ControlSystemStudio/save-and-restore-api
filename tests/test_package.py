from __future__ import annotations

import importlib.metadata

import pytest

import save_and_restore_api
from save_and_restore_api import SaveRestoreAPI as SaveRestoreAPI_Threads
from save_and_restore_api.aio import SaveRestoreAPI as SaveRestoreAPI_Async

admin_username, admin_password = "admin", "adminPass"
user_username, user_password = "user", "userPass"
read_username, read_password = "johndoe", "1234"

base_url = "http://localhost:8080/save-restore"


def test_version():
    assert importlib.metadata.version("save_and_restore_api") == save_and_restore_api.__version__


def test_comm():
    SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
    SR.set_auth(username=user_username, password=user_password)
    SR.open()
    SR.login(username="user", password="userPass")
    SR.get_node(SR.ROOT_NODE_UID)
    SR.close()


@pytest.mark.asyncio
async def test_comm_async():
    SR = SaveRestoreAPI_Async(base_url=base_url, timeout=2)
    SR.set_auth(username="user", password="userPass")
    SR.open()
    await SR.login(username="user", password="userPass")
    await SR.get_node(SR.ROOT_NODE_UID)
    await SR.close()
