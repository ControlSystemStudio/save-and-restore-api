from __future__ import annotations

import asyncio
import importlib.metadata

import pytest

import save_and_restore_api
from save_and_restore_api import SaveRestoreAPI as SaveRestoreAPI_Threads
from save_and_restore_api.aio import SaveRestoreAPI as SaveRestoreAPI_Async

from .common import (
    _is_async,
    admin_password,
    admin_username,
    base_url,
    clear_sar,  # noqa: F401
    read_password,
    read_username,
    user_password,
    user_username,
)


def test_version_01():
    """
    Test that the versioning works correctly.
    """
    assert importlib.metadata.version("save_and_restore_api") == save_and_restore_api.__version__


# # fmt: off
# @pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# # fmt: on
# def test_api_call_01(library):
#     """
#     Test generic API call
#     """
#     username, password = user_username, user_password

#     if not _is_async(library):
#         SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
#         SR.set_auth(username=user_username, password=user_password)
#         SR.open()
#         response = SR.login(username=username, password=password)
#         assert response["userName"] == username
#         SR.close()
#         SR.open()
#         response = SR.login(username=username, password=password)
#         assert response["userName"] == username
#         SR.close()
#     else:
#         async def testing():
#             SR = SaveRestoreAPI_Async(base_url=base_url, timeout=2)
#             SR.set_auth(username=user_username, password=user_password)
#             SR.open()
#             response = await SR.login(username=username, password=password)
#             assert response["userName"] == username
#             await SR.close()
#             SR.open()
#             response = await SR.login(username=username, password=password)
#             assert response["userName"] == username
#             await SR.close()

#         asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("username, password, roles, code", [
    (admin_username, admin_password,  ["ROLE_SAR-ADMIN"], 200),
    (user_username, user_password,  ["ROLE_SAR-USER"], 200),
    (read_username, read_password,  [], 200),
    (user_username, read_password,  [], 401),  # Incorrect password
    (user_username + "_a", user_password,  [], 401),  # Incorrect login
])
# fmt: on
def test_login_01(username, password, roles, library, code):
    """
    Tests for the 'login' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            if code == 200:
                response = SR.login(username=username, password=password)
                assert response["userName"] == username
                assert response["roles"] == roles
            else:
                with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                    SR.login(username=username, password=password)
    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                if code == 200:
                    response = await SR.login(username=username, password=password)
                    assert response["userName"] == username
                    assert response["roles"] == roles
                else:
                    with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                        await SR.login(username=username, password=password)

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("node_uid, code", [
    (SaveRestoreAPI_Threads.ROOT_NODE_UID, 200),
    ("abc", 404),
])
# fmt: on
def test_get_node_01(clear_sar, node_uid, library, code):  # noqa: F811
    """
    Tests for the 'login' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            if code == 200:
                response = SR.get_node(node_uid)
                assert response["uniqueId"] == node_uid
            else:
                with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                    SR.get_node(node_uid)
    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                if code == 200:
                    response = await SR.get_node(node_uid)
                    assert response["uniqueId"] == node_uid
                else:
                    with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                        await SR.get_node(node_uid)

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_add_node_01(clear_sar, library):  # noqa: F811
    """
    Tests for the 'add_node' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            SR.set_auth(username=user_username, password=user_password)

            response = SR.add_node(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER")
            assert response["name"] == "Test Folder"
            assert response["nodeType"] == "FOLDER"
            folder_uid = response["uniqueId"]

            response = SR.add_node(folder_uid, name="Test Config 1", nodeType="CONFIGURATION")
            assert response["name"] == "Test Config 1"
            assert response["nodeType"] == "CONFIGURATION"
            node_uid_1 = response["uniqueId"]

            response = SR.add_node(folder_uid, name="Test Config 2", nodeType="CONFIGURATION")
            assert response["name"] == "Test Config 2"
            assert response["nodeType"] == "CONFIGURATION"
            node_uid_2 = response["uniqueId"]

            SR.delete_nodes([node_uid_1, node_uid_2])
            SR.delete_nodes([folder_uid])

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                SR.set_auth(username=user_username, password=user_password)

                response = await SR.add_node(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER")
                assert response["name"] == "Test Folder"
                assert response["nodeType"] == "FOLDER"
                folder_uid = response["uniqueId"]

                response = await SR.add_node(folder_uid, name="Test Config 1", nodeType="CONFIGURATION")
                assert response["name"] == "Test Config 1"
                assert response["nodeType"] == "CONFIGURATION"
                node_uid_1 = response["uniqueId"]

                response = await SR.add_node(folder_uid, name="Test Config 2", nodeType="CONFIGURATION")
                assert response["name"] == "Test Config 2"
                assert response["nodeType"] == "CONFIGURATION"
                node_uid_2 = response["uniqueId"]

                await SR.delete_nodes([node_uid_1, node_uid_2])
                await SR.delete_nodes([folder_uid])

        asyncio.run(testing())


def test_comm(clear_sar):  # noqa: F811
    SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
    SR.set_auth(username=user_username, password=user_password)
    SR.open()
    SR.login(username="user", password="userPass")
    SR.get_node(SR.ROOT_NODE_UID)
    SR.close()
