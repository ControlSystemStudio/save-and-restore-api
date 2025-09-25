import httpx

from ._api_base import _SaveRestoreAPI_Base


class _SaveRestoreAPI_Async(_SaveRestoreAPI_Base):
    def open(self):
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def close(self):
        await self._client.aclose()
        self._client = None

    async def __aenter__(self):
        self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

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

    async def login(self, *, username=None, password=None):
        method, url, params = self._prepare_login(username=username, password=password)
        return await self.send_request(method, url, params=params)

    async def get_node(self, node_uid):
        method, url = self._prepare_get_node(node_uid=node_uid)
        return await self.send_request(method, url)

    async def add_node(self, parentNodeId, *, name, nodeType, **kwargs):
        method, url, params = self._prepare_add_node(
            parentNodeId=parentNodeId, name=name, nodeType=nodeType, **kwargs
        )
        return await self.send_request(method, url, params=params)

    async def delete_nodes(self, uniqueIds):
        method, url, params = self._prepare_delete_nodes(uniqueIds=uniqueIds)
        return await self.send_request(method, url, params=params)

    async def get_children(self, node_uid):
        method, url = self._prepare_get_children(node_uid=node_uid)
        return await self.send_request(method, url)
