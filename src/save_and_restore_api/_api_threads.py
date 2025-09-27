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

    def get_node(self, node_uid):
        """
        Returns the node with specified node UID.
        """
        method, url = self._prepare_get_node(node_uid=node_uid)
        return self.send_request(method, url)

    def add_node(self, parentNodeId, *, name, nodeType, **kwargs):
        method, url, params = self._prepare_add_node(
            parentNodeId=parentNodeId, name=name, nodeType=nodeType, **kwargs
        )
        return self.send_request(method, url, params=params)

    def delete_node(self, nodeId):
        method, url = self._prepare_delete_node(nodeId=nodeId)
        print(f"================= method={method}, url={url} =================")  ##
        return self.send_request(method, url)

    def delete_nodes(self, uniqueIds):
        method, url, params = self._prepare_delete_nodes(uniqueIds=uniqueIds)
        return self.send_request(method, url, params=params)

    def get_children(self, node_uid):
        method, url = self._prepare_get_children(node_uid=node_uid)
        return self.send_request(method, url)
