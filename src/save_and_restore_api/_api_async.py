import httpx

from ._api_base import _SaveRestoreAPI_Base


class _SaveRestoreAPI_Async(_SaveRestoreAPI_Base):
    def open(self):
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def close(self):
        await self._client.aclose()
        self._client = None
