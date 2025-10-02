# import getpass
import json
from collections.abc import Mapping

import httpx


class RequestParameterError(Exception): ...


class HTTPRequestError(httpx.RequestError): ...


class HTTPClientError(httpx.HTTPStatusError): ...


class HTTPServerError(httpx.HTTPStatusError): ...


class RequestTimeoutError(TimeoutError):
    def __init__(self, msg, request):
        msg = f"Request timeout: {msg}"
        self.request = request
        super().__init__(msg)


class RequestFailedError(Exception):
    def __init__(self, request, response):
        msg = response.get("msg", "") if isinstance(response, Mapping) else str(response)
        msg = msg or "(no error message)"
        msg = f"Request failed: {msg}"
        self.request = request
        self.response = response
        super().__init__(msg)


class _SaveRestoreAPI_Base:
    RequestParameterError = RequestParameterError
    RequestTimeoutError = RequestTimeoutError
    RequestFailedError = RequestFailedError
    HTTPRequestError = HTTPRequestError
    HTTPClientError = HTTPClientError
    HTTPServerError = HTTPServerError

    ROOT_NODE_UID = "44bef5de-e8e6-4014-af37-b8f6c8a939a2"

    def __init__(self, *, base_url, timeout, request_fail_exceptions=True):
        self._base_url = base_url
        self._timeout = timeout
        self._client = None
        self._auth = None

    @staticmethod
    def auth_gen(username, password):
        """
        Generate and return httpx.BasicAuth object based on username and password.
        The object can be passed as ``auth`` parameter in API calls.
        """
        return httpx.BasicAuth(username=username, password=password)

    def auth_set(self, *, username, password):
        """
        Configure authentication for the session based on username and password.
        If the authentication is configured, there is no need to pass the authentication
        object with each API call.
        """
        self._auth = self.auth_gen(username=username, password=password)

    def auth_clear(self):
        """
        Clear authentication for the session.
        """
        self._auth = None

    # def set_username_password(self, username=None, password=None):
    #     if not isinstance(username, str):
    #         print("Username: ", end="")
    #         username = input()
    #     if not isinstance(password, str):
    #         password = getpass.getpass()

    #     self._username = username
    #     self._password = password

    # # TODO: rewrite the logic in this function
    # def _check_response(self, *, request, response):
    #     """
    #     Check if response is a dictionary and has ``"success": True``. Raise an exception
    #     if the request is considered failed and exceptions are allowed. If response is
    #     a dictionary and contains no ``"success"``, then it is considered successful.
    #     """
    #     if self._request_fail_exceptions:
    #         # The response must be a list or a dictionary. If the response is a dictionary
    #         #   and the key 'success': False, then consider the request failed. If there
    #         #   is not 'success' key, then consider the request successful.
    #         is_iterable = isinstance(response, Iterable) and not isinstance(response, str)
    #         is_mapping = isinstance(response, Mapping)
    #         if not any([is_iterable, is_mapping]) or (is_mapping and not response.get("success", True)):
    #             raise self.RequestFailedError(request, response)

    def _process_response(self, *, client_response):
        client_response.raise_for_status()
        response = ""
        if client_response.content:
            try:
                response = client_response.json()
            except json.JSONDecodeError:
                response = client_response.text
        return response

    def _process_comm_exception(self, *, method, params, client_response):
        """
        The function must be called from ``except`` block and returns response with an error message
        or raises an exception.
        """
        try:
            raise

        except httpx.TimeoutException as ex:
            raise self.RequestTimeoutError(ex, {"method": method, "params": params}) from ex

        except httpx.RequestError as ex:
            raise self.HTTPRequestError(f"HTTP request error: {ex}") from ex

        except httpx.HTTPStatusError as exc:
            common_params = {"request": exc.request, "response": exc.response}
            if client_response and (client_response.status_code < 500):
                # Include more detail that httpx does by default.
                response_text = ""
                if client_response.content:
                    try:
                        _, response_text = exc.response.json(), ""
                        if isinstance(_, dict):
                            if "detail" in _:
                                response_text = _["detail"]
                            elif "error" in _:
                                response_text = _["error"]
                            else:
                                response_text = exc.response.text
                    except json.JSONDecodeError:
                        response_text = exc.response.text
                message = f"{exc.response.status_code}: {response_text} {exc.request.url}"
                raise self.HTTPClientError(message, **common_params) from exc
            else:
                raise self.HTTPServerError(exc, **common_params) from exc

    def _prepare_request(
        self, *, method, params=None, url_params=None, headers=None, data=None, timeout=None, auth=None
    ):
        kwargs = {}
        if params:
            kwargs.update({"json": params})
        if url_params:
            kwargs.update({"params": url_params})
        if headers:
            kwargs.update({"headers": headers})
        if data:
            kwargs.update({"data": data})
        if timeout is not None:
            kwargs.update({"timeout": self._adjust_timeout(timeout)})
        if method.upper() != "GET":
            auth = auth or self._auth
            if auth is not None:
                kwargs.update({"auth": auth})
        return kwargs

    # =============================================================================================
    #                         INFO-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_info_get(self):
        method, url = "GET", "/"
        return method, url

    def _prepare_version_get(self):
        method, url = "GET", "/version"
        return method, url

    # =============================================================================================
    #                         AUTHENTICATION-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_login(self, *, username=None, password=None):
        method, url = "POST", "/login"
        params = {"username": username, "password": password}
        return method, url, params

    # =============================================================================================
    #                         NODE-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_node_get(self, *, uniqueNodeId):
        method, url = "GET", f"/node/{uniqueNodeId}"
        return method, url

    def _prepare_nodes_get(self, *, uniqueIds):
        method, url = "GET", "/nodes"
        params = uniqueIds
        return method, url, params

    def _prepare_node_add(self, *, parentNodeId, name, nodeType, **kwargs):
        node_types = ("FOLDER", "CONFIGURATION")
        if nodeType not in node_types:
            raise self.RequestParameterError(f"Invalid nodeType: {nodeType!r}. Supported types: {node_types}.")
        method, url, url_params = "PUT", "/node", {"parentNodeId": parentNodeId}
        params = kwargs
        params.update({"name": name, "nodeType": nodeType})
        return method, url, url_params, params

    def _prepare_node_delete(self, *, nodeId):
        method, url = "DELETE", f"/node/{nodeId}"
        return method, url

    def _prepare_nodes_delete(self, *, uniqueIds):
        method, url = "DELETE", "/node"
        params = uniqueIds
        return method, url, params

    def _prepare_node_get_children(self, *, uniqueNodeId):
        method, url = "GET", f"/node/{uniqueNodeId}/children"
        return method, url

    def _prepare_node_get_parent(self, *, uniqueNodeId):
        method, url = "GET", f"/node/{uniqueNodeId}/parent"
        return method, url

    # =============================================================================================
    #                         CONFIGURATION-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_config_get(self, *, uniqueNodeId):
        method, url = "GET", f"/config/{uniqueNodeId}"
        return method, url

    def _prepare_config_create(self, *, parentNodeId, configurationNode, configurationData):
        method, url = "PUT", f"/config?parentNodeId={parentNodeId}"
        configurationData = configurationData or {}
        params = {"configurationNode": configurationNode, "configurationData": configurationData}
        return method, url, params

    def _prepare_config_update(self, *, configurationNode, configurationData):
        method, url = "POST", "/config"
        params = {"configurationNode": configurationNode, "configurationData": configurationData}
        return method, url, params

    # =============================================================================================
    #                         TAG-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_tags_get(self):
        method, url = "GET", "/tags"
        return method, url

    def _prepare_tags_add(self, *, uniqueNodeIds, tag):
        method, url = "POST", "/tags"
        params = {"uniqueNodeIds": uniqueNodeIds, "tag": tag}
        return method, url, params

    def _prepare_tags_delete(self, *, uniqueNodeIds, tag):
        method, url = "DELETE", "/tags"
        params = {"uniqueNodeIds": uniqueNodeIds, "tag": tag}
        return method, url, params

    # =============================================================================================
    #                         TAKE-SNAPSHOT-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_take_snapshot_get(self, *, uniqueNodeId):
        method, url = "GET", f"/take-snapshot/{uniqueNodeId}"
        return method, url

    def _prepare_take_snapshot_save(self, *, uniqueNodeId, name, comment):
        method, url = "PUT", f"/take-snapshot/{uniqueNodeId}"
        url_params = {"name": name, "comment": comment}
        return method, url, url_params

    # =============================================================================================
    #                         SNAPSHOT-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_snapshot_get(self, *, uniqueId):
        method, url = "GET", f"/snapshot/{uniqueId}"
        return method, url

    def _prepare_snapshot_add(self, *, parentNodeId, snapshotNode, snapshotData):
        method, url = "PUT", f"/snapshot?parentNodeId={parentNodeId}"
        params = {"snapshotNode": snapshotNode, "snapshotData": snapshotData}
        return method, url, params

    def _prepare_snapshot_update(self, *, snapshotNode, snapshotData):
        method, url = "POST", "/snapshot"
        params = {"snapshotNode": snapshotNode, "snapshotData": snapshotData}
        return method, url, params

    def _prepare_snapshots_get(self):
        method, url = "GET", "/snapshots"
        return method, url

    # =============================================================================================
    #                     SNAPSHOT-RESTORE-CONTROLLER API METHODS
    # =============================================================================================

    def _prepare_restore_node(self, *, nodeId):
        method, url = "POST", "/restore/node"
        url_params = {"nodeId": nodeId}
        return method, url, url_params

    def _prepare_restore_items(self, *, snapshotItems):
        method, url = "POST", "/restore/items"
        params = snapshotItems
        return method, url, params

    # =============================================================================================

    # def create_config(self, parent_node_uid, name, pv_list):
    #     config_dict = {
    #         "configurationNode": {
    #             "name": name,
    #             "nodeType": "CONFIGURATION",
    #             "userName": self._username,
    #         },
    #         "configurationData": {
    #             "pvList": pv_list,
    #         },
    #     }
    #     print(f"config_dict=\n{pprint.pformat(config_dict)}")
    #     return self.send_request("PUT", f"/config?parentNodeId={parent_node_uid}", json=config_dict)

    # def update_config(self, node_uid, name, pv_list):
    #     config_dict = {
    #         "configurationNode": {
    #             "name": name,
    #             "nodeType": "CONFIGURATION",
    #             "userName": self._username,
    #             "uniqueId": node_uid,
    #         },
    #         "configurationData": {
    #             "pvList": pv_list,
    #         },
    #     }
    #     print(f"config_dict=\n{pprint.pformat(config_dict)}")
    #     # return self.send_request("POST", f"/config/{node_uid}", json=config_dict)
    #     return self.send_request("POST", "/config", json=config_dict)
