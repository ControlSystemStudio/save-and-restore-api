import httpx

from ._api_base import _SaveRestoreAPI_Base
from ._api_threads import _SaveRestoreAPI_Threads


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

    # =============================================================================================
    #                         NODE-CONTROLLER API METHODS
    # =============================================================================================

    async def node_get(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_get(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)

    async def nodes_get(self, uniqueIds):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_nodes_get(uniqueIds=uniqueIds)
        return await self.send_request(method, url, params=params)

    async def node_add(self, parentNodeId, *, name, nodeType, **kwargs):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_node_add(
            parentNodeId=parentNodeId, name=name, nodeType=nodeType, **kwargs
        )
        return await self.send_request(method, url, params=params)

    async def node_delete(self, nodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_delete(nodeId=nodeId)
        return await self.send_request(method, url)

    async def nodes_delete(self, uniqueIds):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_nodes_delete(uniqueIds=uniqueIds)
        return await self.send_request(method, url, params=params)

    async def node_get_children(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_get_children(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)

    async def node_get_parent(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_get_parent(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)


_SaveRestoreAPI_Async.node_get.__doc__ = _SaveRestoreAPI_Threads.node_get.__doc__
_SaveRestoreAPI_Async.nodes_get.__doc__ = _SaveRestoreAPI_Threads.nodes_get.__doc__
_SaveRestoreAPI_Async.node_add.__doc__ = _SaveRestoreAPI_Threads.node_add.__doc__
_SaveRestoreAPI_Async.node_delete.__doc__ = _SaveRestoreAPI_Threads.node_delete.__doc__
_SaveRestoreAPI_Async.nodes_delete.__doc__ = _SaveRestoreAPI_Threads.nodes_delete.__doc__
_SaveRestoreAPI_Async.node_get_children.__doc__ = _SaveRestoreAPI_Threads.node_get_children.__doc__
_SaveRestoreAPI_Async.node_get_parent.__doc__ = _SaveRestoreAPI_Threads.node_get_parent.__doc__
