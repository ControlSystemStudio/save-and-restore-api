from __future__ import annotations

import importlib.metadata

import asyncio
import pytest
from .common import _is_async

import save_and_restore_api
from save_and_restore_api import SaveRestoreAPI as SaveRestoreAPI_Threads
from save_and_restore_api.aio import SaveRestoreAPI as SaveRestoreAPI_Async

admin_username, admin_password = "admin", "adminPass"
user_username, user_password = "user", "userPass"
read_username, read_password = "johndoe", "1234"

base_url = "http://localhost:8080/save-restore"


def test_version():
    assert importlib.metadata.version("save_and_restore_api") == save_and_restore_api.__version__


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("username, password, roles", [
    (admin_username, admin_password,  ["ROLE_SAR-ADMIN"]),
    (user_username, user_password,  ["ROLE_SAR-USER"]),
    (read_username, read_password,  []),
])
# fmt: on
def test_login_01(username, password, roles, library):
    if not _is_async(library):
        SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
        SR.set_auth(username=user_username, password=user_password)
        SR.open()
        response = SR.login(username=username, password=password)
        SR.close()
        assert response["userName"] == username
        assert response["roles"] == roles
    else:
        async def testing():
            SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
            SR.set_auth(username=user_username, password=user_password)
            SR.open()
            response = SR.login(username=username, password=password)
            SR.close()
            assert response["userName"] == username
            assert response["roles"] == roles

        asyncio.run(testing())


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
