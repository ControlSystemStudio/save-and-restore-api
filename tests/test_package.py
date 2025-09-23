from __future__ import annotations

import asyncio
import importlib.metadata

import pytest

import save_and_restore_api
from save_and_restore_api import SaveRestoreAPI as SaveRestoreAPI_Threads
from save_and_restore_api.aio import SaveRestoreAPI as SaveRestoreAPI_Async

from .common import _is_async

admin_username, admin_password = "admin", "adminPass"
user_username, user_password = "user", "userPass"
read_username, read_password = "johndoe", "1234"

base_url = "http://localhost:8080/save-restore"


def test_version():
    assert importlib.metadata.version("save_and_restore_api") == save_and_restore_api.__version__


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("username, password, roles, code", [
    (admin_username, admin_password,  ["ROLE_SAR-ADMIN"], 200),
    (user_username, user_password,  ["ROLE_SAR-USER"], 200),
    (read_username, read_password,  [], 200),
    (user_username, read_password,  [], 401),
])
# fmt: on
def test_login_01(username, password, roles, library, code):
    if not _is_async(library):
        SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
        SR.set_auth(username=user_username, password=user_password)
        SR.open()
        if code == 200:
            response = SR.login(username=username, password=password)
            assert response["userName"] == username
            assert response["roles"] == roles
        else:
            with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                SR.login(username=username, password=password)
        SR.close()
    else:
        async def testing():
            SR = SaveRestoreAPI_Async(base_url=base_url, timeout=2)
            SR.set_auth(username=user_username, password=user_password)
            SR.open()
            if code == 200:
                response = await SR.login(username=username, password=password)
                assert response["userName"] == username
                assert response["roles"] == roles
            else:
                with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                    await SR.login(username=username, password=password)
            await SR.close()

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
