import httpx

from ._api_base import _SaveRestoreAPI_Base


class _SaveRestoreAPI_Async(_SaveRestoreAPI_Base):
    def open(self):
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def close(self):
        await self._client.aclose()
        self._client = None

    async def send_request(
        self, method, url, *, params=None, url_params=None, headers=None, data=None, timeout=None, auth=None
    ):
        try:
            client_response = None
            kwargs = self._prepare_request(
                method=method,
                params=params,
                url_params=url_params,
                headers=headers,
                data=data,
                timeout=timeout,
                auth=auth,
            )
            client_response = await self._client.request(method, url, **kwargs)
            response = self._process_response(client_response=client_response)
        except Exception:
            response = self._process_comm_exception(method=method, params=params, client_response=client_response)

        return response
