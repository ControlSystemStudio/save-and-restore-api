import httpx

from ._api_base import _SaveRestoreAPI_Base
from ._api_threads import SaveRestoreAPI as _SaveRestoreAPI_Threads


class SaveRestoreAPI(_SaveRestoreAPI_Base):
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

    # =============================================================================================
    #                         INFO-CONTROLLER API METHODS
    # =============================================================================================

    async def info_get(self):
        method, url = self._prepare_info_get()
        return await self.send_request(method, url)

    async def version_get(self):
        """
        Returns current version of Save and Restore service.

        API: GET /verson
        """
        method, url = self._prepare_version_get()
        return await self.send_request(method, url)

    # =============================================================================================
    #                         AUTHENTICATION-CONTROLLER API METHODS
    # =============================================================================================

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

    async def node_add(self, parentNodeId, *, name, nodeType, auth=None, **kwargs):
        # Reusing docstrings from the threaded version
        method, url, url_params, params = self._prepare_node_add(
            parentNodeId=parentNodeId, name=name, nodeType=nodeType, **kwargs
        )
        return await self.send_request(method, url, url_params=url_params, params=params, auth=auth)

    async def node_delete(self, nodeId, *, auth=None):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_delete(nodeId=nodeId)
        return await self.send_request(method, url, auth=auth)

    async def nodes_delete(self, uniqueIds, *, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_nodes_delete(uniqueIds=uniqueIds)
        return await self.send_request(method, url, params=params, auth=auth)

    async def node_get_children(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_get_children(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)

    async def node_get_parent(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_node_get_parent(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)

    # =============================================================================================
    #                         CONFIGURATION-CONTROLLER API METHODS
    # =============================================================================================

    async def config_get(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_config_get(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)

    async def config_create(self, parentNodeId, *, configurationNode, configurationData, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_config_create(
            parentNodeId=parentNodeId, configurationNode=configurationNode, configurationData=configurationData
        )
        return await self.send_request(method, url, params=params, auth=auth)

    async def config_update(self, *, configurationNode, configurationData, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_config_update(
            configurationNode=configurationNode, configurationData=configurationData
        )
        return await self.send_request(method, url, params=params, auth=auth)

    # =============================================================================================
    #                         TAG-CONTROLLER API METHODS
    # =============================================================================================

    async def tags_get(self):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_tags_get()
        return await self.send_request(method, url)

    async def tags_add(self, *, uniqueNodeIds, tag, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_tags_add(uniqueNodeIds=uniqueNodeIds, tag=tag)
        return await self.send_request(method, url, params=params, auth=auth)

    async def tags_delete(self, *, uniqueNodeIds, tag, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_tags_delete(uniqueNodeIds=uniqueNodeIds, tag=tag)
        return await self.send_request(method, url, params=params, auth=auth)

    # =============================================================================================
    #                         TAKE-SNAPSHOT-CONTROLLER API METHODS
    # =============================================================================================

    async def take_snapshot_get(self, uniqueNodeId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_take_snapshot_get(uniqueNodeId=uniqueNodeId)
        return await self.send_request(method, url)

    async def take_snapshot_save(self, uniqueNodeId, *, name=None, comment=None, auth=None):
        # Reusing docstrings from the threaded version
        method, url, url_params = self._prepare_take_snapshot_save(
            uniqueNodeId=uniqueNodeId, name=name, comment=comment
        )
        return await self.send_request(method, url, url_params=url_params, auth=auth)

    # =============================================================================================
    #                         SNAPSHOT-CONTROLLER API METHODS
    # =============================================================================================

    async def snapshot_get(self, uniqueId):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_snapshot_get(uniqueId=uniqueId)
        return await self.send_request(method, url)

    async def snapshot_add(self, parentNodeId, *, snapshotNode, snapshotData, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_snapshot_add(
            parentNodeId=parentNodeId, snapshotNode=snapshotNode, snapshotData=snapshotData
        )
        return await self.send_request(method, url, params=params, auth=auth)

    async def snapshot_update(self, *, snapshotNode, snapshotData, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_snapshot_update(snapshotNode=snapshotNode, snapshotData=snapshotData)
        return await self.send_request(method, url, params=params, auth=auth)

    async def snapshots_get(self):
        # Reusing docstrings from the threaded version
        method, url = self._prepare_snapshots_get()
        return await self.send_request(method, url)

    # =============================================================================================
    #                     SNAPSHOT-RESTORE-CONTROLLER API METHODS
    # =============================================================================================

    async def restore_node(self, nodeId, *, auth=None):
        # Reusing docstrings from the threaded version
        method, url, url_params = self._prepare_restore_node(nodeId=nodeId)
        return await self.send_request(method, url, url_params=url_params, auth=auth)

    async def restore_items(self, *, snapshotItems, auth=None):
        # Reusing docstrings from the threaded version
        method, url, params = self._prepare_restore_items(snapshotItems=snapshotItems)
        return await self.send_request(method, url, params=params, auth=auth)


SaveRestoreAPI.info_get.__doc__ = _SaveRestoreAPI_Threads.info_get.__doc__
SaveRestoreAPI.login.__doc__ = _SaveRestoreAPI_Threads.login.__doc__
SaveRestoreAPI.node_get.__doc__ = _SaveRestoreAPI_Threads.node_get.__doc__
SaveRestoreAPI.nodes_get.__doc__ = _SaveRestoreAPI_Threads.nodes_get.__doc__
SaveRestoreAPI.node_add.__doc__ = _SaveRestoreAPI_Threads.node_add.__doc__
SaveRestoreAPI.node_delete.__doc__ = _SaveRestoreAPI_Threads.node_delete.__doc__
SaveRestoreAPI.nodes_delete.__doc__ = _SaveRestoreAPI_Threads.nodes_delete.__doc__
SaveRestoreAPI.node_get_children.__doc__ = _SaveRestoreAPI_Threads.node_get_children.__doc__
SaveRestoreAPI.node_get_parent.__doc__ = _SaveRestoreAPI_Threads.node_get_parent.__doc__
SaveRestoreAPI.config_get.__doc__ = _SaveRestoreAPI_Threads.config_get.__doc__
SaveRestoreAPI.config_create.__doc__ = _SaveRestoreAPI_Threads.config_create.__doc__
SaveRestoreAPI.config_update.__doc__ = _SaveRestoreAPI_Threads.config_update.__doc__
SaveRestoreAPI.tags_get.__doc__ = _SaveRestoreAPI_Threads.tags_get.__doc__
SaveRestoreAPI.tags_add.__doc__ = _SaveRestoreAPI_Threads.tags_add.__doc__
SaveRestoreAPI.tags_delete.__doc__ = _SaveRestoreAPI_Threads.tags_delete.__doc__
SaveRestoreAPI.take_snapshot_get.__doc__ = _SaveRestoreAPI_Threads.take_snapshot_get.__doc__
SaveRestoreAPI.take_snapshot_save.__doc__ = _SaveRestoreAPI_Threads.take_snapshot_save.__doc__
SaveRestoreAPI.snapshot_get.__doc__ = _SaveRestoreAPI_Threads.snapshot_get.__doc__
SaveRestoreAPI.snapshot_add.__doc__ = _SaveRestoreAPI_Threads.snapshot_add.__doc__
SaveRestoreAPI.snapshot_update.__doc__ = _SaveRestoreAPI_Threads.snapshot_update.__doc__
SaveRestoreAPI.snapshots_get.__doc__ = _SaveRestoreAPI_Threads.snapshots_get.__doc__
SaveRestoreAPI.restore_node.__doc__ = _SaveRestoreAPI_Threads.restore_node.__doc__
SaveRestoreAPI.restore_items.__doc__ = _SaveRestoreAPI_Threads.restore_items.__doc__
