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


def _select_auth(*, SR, usesetauth):
    auth = {}
    if usesetauth:
        SR.auth_set(username=user_username, password=user_password)
    else:
        auth["auth"] = SR.auth_gen(username=user_username, password=user_password)
    return auth


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
#         SR.auth_set(username=user_username, password=user_password)
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
#             SR.auth_set(username=user_username, password=user_password)
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


# =============================================================================================
#                         TESTS FOR NODE-CONTROLLER API METHODS
# =============================================================================================


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("node_uid, code", [
    (SaveRestoreAPI_Threads.ROOT_NODE_UID, 200),
    ("abc", 404),
])
# fmt: on
def test_node_get_01(clear_sar, node_uid, library, code):  # noqa: F811
    """
    Basic tests for the 'node_get' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            if code == 200:
                response = SR.node_get(node_uid)
                assert response["uniqueId"] == node_uid
            else:
                with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                    SR.node_get(node_uid)
    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                if code == 200:
                    response = await SR.node_get(node_uid)
                    assert response["uniqueId"] == node_uid
                else:
                    with pytest.raises(SR.HTTPClientError, match=f"{code}"):
                        await SR.node_get(node_uid)

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_nodes_get_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Basic tests for the 'nodes_get' API.
    """

    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Parent Folder", nodeType="FOLDER", **auth)
            parent_uid = response["uniqueId"]

            response = SR.node_add(parent_uid, name="Child Folder", nodeType="FOLDER", **auth)
            folder_uid = response["uniqueId"]

            response = SR.node_add(parent_uid, name="Child Config", nodeType="CONFIGURATION", **auth)
            node_uid = response["uniqueId"]

            node_uids = [parent_uid, folder_uid, node_uid]
            node_types = ["FOLDER", "FOLDER", "CONFIGURATION"]

            response = SR.nodes_get(node_uids)
            assert len(response) == 3
            assert [_["uniqueId"] for _ in response] == node_uids
            assert [_["nodeType"] for _ in response] == node_types

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Parent Folder", nodeType="FOLDER", **auth)
                parent_uid = response["uniqueId"]

                response = await SR.node_add(parent_uid, name="Child Folder", nodeType="FOLDER", **auth)
                folder_uid = response["uniqueId"]

                response = await SR.node_add(parent_uid, name="Child Config", nodeType="CONFIGURATION", **auth)
                node_uid = response["uniqueId"]

                node_uids = [parent_uid, folder_uid, node_uid]
                node_types = ["FOLDER", "FOLDER", "CONFIGURATION"]

                response = await SR.nodes_get(node_uids)
                assert len(response) == 3
                assert [_["uniqueId"] for _ in response] == node_uids
                assert [_["nodeType"] for _ in response] == node_types

        asyncio.run(testing())



# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_node_add_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Basic tests for the 'node_add' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER", **auth)
            assert response["name"] == "Test Folder"
            assert response["nodeType"] == "FOLDER"
            folder_uid = response["uniqueId"]

            response = SR.node_add(folder_uid, name="Test Config 1", nodeType="CONFIGURATION", **auth)
            assert response["name"] == "Test Config 1"
            assert response["nodeType"] == "CONFIGURATION"

            response = SR.node_add(folder_uid, name="Test Config 2", nodeType="CONFIGURATION", **auth)
            assert response["name"] == "Test Config 2"
            assert response["nodeType"] == "CONFIGURATION"

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER", **auth)
                assert response["name"] == "Test Folder"
                assert response["nodeType"] == "FOLDER"
                folder_uid = response["uniqueId"]

                response = await SR.node_add(folder_uid, name="Test Config 1", nodeType="CONFIGURATION", **auth)
                assert response["name"] == "Test Config 1"
                assert response["nodeType"] == "CONFIGURATION"

                response = await SR.node_add(folder_uid, name="Test Config 2", nodeType="CONFIGURATION", **auth)
                assert response["name"] == "Test Config 2"
                assert response["nodeType"] == "CONFIGURATION"


        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_node_delete_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Basic tests for the 'node_delete' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER", **auth)
            folder_uid = response["uniqueId"]

            response = SR.node_add(folder_uid, name="Test Config 1", nodeType="CONFIGURATION", **auth)
            node_uid_1 = response["uniqueId"]

            response = SR.node_add(folder_uid, name="Test Config 2", nodeType="CONFIGURATION", **auth)
            node_uid_2 = response["uniqueId"]

            SR.node_delete(node_uid_1)
            SR.node_delete(node_uid_2)
            SR.node_delete(folder_uid)

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER", **auth)
                folder_uid = response["uniqueId"]

                response = await SR.node_add(folder_uid, name="Test Config 1", nodeType="CONFIGURATION", **auth)
                node_uid_1 = response["uniqueId"]

                response = await SR.node_add(folder_uid, name="Test Config 2", nodeType="CONFIGURATION", **auth)
                node_uid_2 = response["uniqueId"]

                await SR.node_delete(node_uid_1)
                await SR.node_delete(node_uid_2)
                await SR.node_delete(folder_uid)

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_nodes_delete_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Basic tests for the 'nodes_delete' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER", **auth)
            folder_uid = response["uniqueId"]

            response = SR.node_add(folder_uid, name="Test Config 1", nodeType="CONFIGURATION", **auth)
            node_uid_1 = response["uniqueId"]

            response = SR.node_add(folder_uid, name="Test Config 2", nodeType="CONFIGURATION", **auth)
            node_uid_2 = response["uniqueId"]

            SR.nodes_delete([node_uid_1, node_uid_2], **auth)
            SR.nodes_delete([folder_uid], **auth)

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Test Folder", nodeType="FOLDER", **auth)
                folder_uid = response["uniqueId"]

                response = await SR.node_add(folder_uid, name="Test Config 1", nodeType="CONFIGURATION", **auth)
                node_uid_1 = response["uniqueId"]

                response = await SR.node_add(folder_uid, name="Test Config 2", nodeType="CONFIGURATION", **auth)
                node_uid_2 = response["uniqueId"]

                await SR.nodes_delete([node_uid_1, node_uid_2], **auth)
                await SR.nodes_delete([folder_uid], **auth)

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_node_get_children_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Basic tests for the 'node_get_children' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Parent Folder", nodeType="FOLDER", **auth)
            parent_uid = response["uniqueId"]

            response = SR.node_add(parent_uid, name="Child Folder", nodeType="FOLDER", **auth)
            folder_uid = response["uniqueId"]

            response = SR.node_add(parent_uid, name="Child Config", nodeType="CONFIGURATION", **auth)
            node_uid = response["uniqueId"]

            response = SR.node_get_children(parent_uid)
            assert len(response) == 2
            assert response[0]["uniqueId"] == folder_uid
            assert response[0]["nodeType"] == "FOLDER"
            assert response[1]["uniqueId"] == node_uid
            assert response[1]["nodeType"] == "CONFIGURATION"

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Parent Folder", nodeType="FOLDER", **auth)
                parent_uid = response["uniqueId"]

                response = await SR.node_add(parent_uid, name="Child Folder", nodeType="FOLDER", **auth)
                folder_uid = response["uniqueId"]

                response = await SR.node_add(parent_uid, name="Child Config", nodeType="CONFIGURATION", **auth)
                node_uid = response["uniqueId"]

                response = await SR.node_get_children(parent_uid)
                assert len(response) == 2
                assert response[0]["uniqueId"] == folder_uid
                assert response[0]["nodeType"] == "FOLDER"
                assert response[1]["uniqueId"] == node_uid
                assert response[1]["nodeType"] == "CONFIGURATION"

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_node_get_parent_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Tests for the 'node_get_parent' API.
    """
    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Child Folder", nodeType="FOLDER", **auth)
            folder_uid = response["uniqueId"]

            response = SR.node_get_parent(folder_uid)
            assert response["uniqueId"] == SR.ROOT_NODE_UID
            assert response["nodeType"] == "FOLDER"

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Child Folder", nodeType="FOLDER", **auth)
                folder_uid = response["uniqueId"]

                response = await SR.node_get_parent(folder_uid)
                assert response["uniqueId"] == SR.ROOT_NODE_UID
                assert response["nodeType"] == "FOLDER"

        asyncio.run(testing())


# =============================================================================================
#                         CONFIGURATION-CONTROLLER API METHODS
# =============================================================================================


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_config_create_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Tests for the 'config_create' and 'config_get' API.
    """

    pv_list = [
            {
                "pvName": "13SIM1:{SimDetector-Cam:1}cam1:BinX"
            },
            {
                "pvName": "13SIM1:{SimDetector-Cam:1}cam1:BinY",
                "comparison": {
                    "comparisonMode": "ABSOLUTE",
                    "tolerance": 2.7
                }
            },
            {
                "pvName": "13SIM1:{SimDetector-Cam:2}cam2:BinX",
                "readbackPvName": None,
                "readOnly": False,
            },
            {
                "pvName": "13SIM1:{SimDetector-Cam:2}cam2:BinY",
                "readbackPvName": None,
                "readOnly": False,
            }
    ]

    configurationNode = {
        "name": "Config",
    }
    configurationData = {
        "pvList": pv_list,
    }

    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=2) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            response = SR.node_add(SR.ROOT_NODE_UID, name="Child Folder", nodeType="FOLDER", **auth)
            folder_uid = response["uniqueId"]


            response = SR.config_create(
                folder_uid, configurationNode=configurationNode, configurationData=configurationData, **auth
            )
            assert response["configurationNode"]["name"] == "Config"
            assert response["configurationNode"]["nodeType"] == "CONFIGURATION"
            assert response["configurationNode"]["userName"] == user_username
            assert len(response["configurationData"]["pvList"]) == len(pv_list)

            config_uid = response["configurationNode"]["uniqueId"]

            response = SR.config_get(config_uid)
            assert response["uniqueId"] == config_uid
            assert len(response["pvList"]) == len(pv_list)

            response = SR.node_get(config_uid)
            assert response["uniqueId"] == config_uid
            assert response["name"] == "Config"
            assert response["nodeType"] == "CONFIGURATION"
            assert response["userName"] == user_username

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                response = await SR.node_add(SR.ROOT_NODE_UID, name="Child Folder", nodeType="FOLDER", **auth)
                folder_uid = response["uniqueId"]

                response = await SR.config_create(
                    folder_uid, configurationNode=configurationNode, configurationData=configurationData, **auth
                )
                assert response["configurationNode"]["name"] == "Config"
                assert response["configurationNode"]["nodeType"] == "CONFIGURATION"
                assert response["configurationNode"]["userName"] == user_username
                assert len(response["configurationData"]["pvList"]) == len(pv_list)

                config_uid = response["configurationNode"]["uniqueId"]

                response = await SR.config_get(config_uid)
                assert response["uniqueId"] == config_uid
                assert len(response["pvList"]) == len(pv_list)

                response = await SR.node_get(config_uid)
                assert response["uniqueId"] == config_uid
                assert response["name"] == "Config"
                assert response["nodeType"] == "CONFIGURATION"
                assert response["userName"] == user_username

        asyncio.run(testing())





def test_comm(clear_sar):  # noqa: F811
    SR = SaveRestoreAPI_Threads(base_url=base_url, timeout=2)
    SR.auth_set(username=user_username, password=user_password)
    SR.open()
    SR.login(username="user", password="userPass")
    SR.node_get(SR.ROOT_NODE_UID)
    SR.close()
