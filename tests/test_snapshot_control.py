from __future__ import annotations

import asyncio

import pytest
from epics import caget

from save_and_restore_api import SaveRestoreAPI as SaveRestoreAPI_Threads
from save_and_restore_api.aio import SaveRestoreAPI as SaveRestoreAPI_Async

from .common import (
    _is_async,
    _select_auth,
    base_url,
    clear_sar,  # noqa: F401
    create_root_folder,
    ioc,  # noqa: F401
    ioc_pvs,
)

# =============================================================================================
#                         TESTS FOR SNAPSHOT-CONTROLLER API METHODS
# =============================================================================================


def test_epics(ioc):  # noqa: F811
    for pv, value in ioc_pvs.items():
        assert caget(pv) == value, f"PV {pv} has value {caget(pv)}, expected {value}"


# fmt: off
@pytest.mark.parametrize("usesetauth", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
# fmt: on
def test_take_snapshot_get_01(clear_sar, library, usesetauth):  # noqa: F811
    """
    Basic tests for the 'take_snapshot_get' API.
    """
    root_folder_uid = create_root_folder()

    if not _is_async(library):
        with SaveRestoreAPI_Threads(base_url=base_url, timeout=10) as SR:
            auth = _select_auth(SR=SR, usesetauth=usesetauth)

            configurationNode = {"name": "Test Config"}
            configurationData = {"pvList": [{"pvName": _} for _ in ioc_pvs.keys()]}

            response = SR.config_create(
                root_folder_uid,
                configurationNode=configurationNode,
                configurationData=configurationData,
                **auth
            )
            config_uid = response["configurationNode"]["uniqueId"]

            response = SR.take_snapshot_get(config_uid)

            snapshot_pv_values = {}
            for data in response:
                pv_name, val = data["configPv"]["pvName"], data["value"]["value"]
                snapshot_pv_values[pv_name] = val

            for pv, value in ioc_pvs.items():
                assert snapshot_pv_values[pv] == value, \
                    print(f"pv: {pv}, expected: {value}, got: {snapshot_pv_values[pv]}")

    else:
        async def testing():
            async with SaveRestoreAPI_Async(base_url=base_url, timeout=2) as SR:
                auth = _select_auth(SR=SR, usesetauth=usesetauth)

                configurationNode = {"name": "Test Config"}
                configurationData = {"pvList": [{"pvName": _} for _ in ioc_pvs.keys()]}

                response = await SR.config_create(
                    root_folder_uid,
                    configurationNode=configurationNode,
                    configurationData=configurationData,
                    **auth
                )
                config_uid = response["configurationNode"]["uniqueId"]

                response = await SR.take_snapshot_get(config_uid)

                snapshot_pv_values = {}
                for data in response:
                    pv_name, val = data["configPv"]["pvName"], data["value"]["value"]
                    snapshot_pv_values[pv_name] = val

                for pv, value in ioc_pvs.items():
                    assert snapshot_pv_values[pv] == value, \
                        print(f"pv: {pv}, expected: {value}, got: {snapshot_pv_values[pv]}")

        asyncio.run(testing())
