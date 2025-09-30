from __future__ import annotations

# import asyncio
# import pytest
from epics import caget

# from save_and_restore_api import SaveRestoreAPI as SaveRestoreAPI_Threads
# from save_and_restore_api.aio import SaveRestoreAPI as SaveRestoreAPI_Async
from .common import (
    # _is_async,
    # _select_auth,
    # base_url,
    clear_sar,  # noqa: F401
    # create_root_folder,
    ioc,  # noqa: F401
    ioc_pvs,
)

# =============================================================================================
#                         TESTS FOR SNAPSHOT-CONTROLLER API METHODS
# =============================================================================================


def test_epics(ioc):  # noqa: F811
    for pv, value in ioc_pvs.items():
        assert caget(pv) == value, f"PV {pv} has value {caget(pv)}, expected {value}"
