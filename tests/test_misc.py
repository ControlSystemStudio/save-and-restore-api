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
