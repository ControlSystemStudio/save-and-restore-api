import httpx

from ._api_base import _SaveRestoreAPI_Base


class _SaveRestoreAPI_Threads(_SaveRestoreAPI_Base):
    def open(self):
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def close(self):
        self._client.close()
        self._client = None
