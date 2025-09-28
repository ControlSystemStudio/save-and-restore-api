import httpx

from ._api_base import _SaveRestoreAPI_Base


class _SaveRestoreAPI_Threads(_SaveRestoreAPI_Base):
    def open(self):
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def close(self):
        self._client.close()
        self._client = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def send_request(
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
            client_response = self._client.request(method, url, **kwargs)
            response = self._process_response(client_response=client_response)
        except Exception:
            response = self._process_comm_exception(method=method, params=params, client_response=client_response)

        return response

    def login(self, *, username=None, password=None):
        method, url, params = self._prepare_login(username=username, password=password)
        return self.send_request(method, url, params=params)

    # =============================================================================================
    #                         NODE-CONTROLLER API METHODS
    # =============================================================================================

    def get_node(self, uniqueNodeId):
        """
        Returns the node with specified node UID.

        API: GET /node/{uniqueNodeId}
        """
        method, url = self._prepare_get_node(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def get_nodes(self, uniqueIds):
        """
        Returns nodes specified by a list of UIDs.

        API: GET /nodes
        """
        method, url, params = self._prepare_get_nodes(uniqueIds=uniqueIds)
        return self.send_request(method, url, params=params)

    def add_node(self, parentNodeId, *, name, nodeType, **kwargs):
        """
        Creates a new node under the specified parent node. Required parameters:
        ``name`` and ``nodeType``. Supported types: ``"FOLDER"``, ``"CONFIGURATION"``.

        API: PUT /node?parentNodeId={parentNodeId}
        """
        method, url, params = self._prepare_add_node(
            parentNodeId=parentNodeId, name=name, nodeType=nodeType, **kwargs
        )
        return self.send_request(method, url, params=params)

    def delete_node(self, nodeId):
        """
        Deletes the node with specified node ID. The call fails if the node can
        not be deleted.

        API: DELETE /node/{nodeId}
        """
        method, url = self._prepare_delete_node(nodeId=nodeId)
        return self.send_request(method, url)

    def delete_nodes(self, uniqueIds):
        """
        Deletes multiple nodes specified as a list of UIDs. The call fails if
        any of the nodes can not be deleted.

        API: DELETE /node
        """
        method, url, params = self._prepare_delete_nodes(uniqueIds=uniqueIds)
        return self.send_request(method, url, params=params)

    def get_children(self, uniqueNodeId):
        """
        Returns the list of child nodes for the specified node UID.

        API: GET /node/{uniqueNodeId}/children
        """
        method, url = self._prepare_get_children(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def get_parent(self, uniqueNodeId):
        """
        Returns the parent node for the specified node UID.

        API: GET /node/{uniqueNodeId}/parent
        """
        method, url = self._prepare_get_parent(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)
