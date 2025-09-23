import getpass
import pprint
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


class SaveRestoreAPI:
    RequestParameterError = RequestParameterError
    RequestTimeoutError = RequestTimeoutError
    RequestFailedError = RequestFailedError
    HTTPRequestError = HTTPRequestError
    HTTPClientError = HTTPClientError
    HTTPServerError = HTTPServerError

    def __init__(self, *, base_url, timeout, request_fail_exceptions=True):
        self._base_url = base_url
        self._timeout = timeout
        self._client = None
        self._root_node_uid = "44bef5de-e8e6-4014-af37-b8f6c8a939a2"

        self._username = None
        self._password = None
        # self._username = "***REMOVED***"
        # self._password = "***REMOVED***"

    @property
    def ROOT_NODE_UID(self):
        return self._root_node_uid

    def open(self):
        auth = httpx.BasicAuth(username=self._username, password=self._password)
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout, auth=auth)

    def close(self):
        self._client.close()
        self._client = None

    def set_username_password(self, username=None, password=None):
        if not isinstance(username, str):
            print("Username: ", end="")
            username = input()
        if not isinstance(password, str):
            password = getpass.getpass()

        self._username = username
        self._password = password

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
        response = client_response.json()
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
                message = (
                    f"{exc.response.status_code}: "
                    f"{exc.response.json()['detail'] if client_response.content else ''} "
                    f"{exc.request.url}"
                )
                raise self.HTTPClientError(message, **common_params) from exc
            else:
                raise self.HTTPServerError(exc, **common_params) from exc

    def send_request(self, method, url, *, params=None, url_params=None, headers=None, data=None, timeout=None):
        try:
            client_response = None
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
            client_response = self._client.request(method, url, **kwargs)
            response = self._process_response(client_response=client_response)
        except Exception:
            response = self._process_comm_exception(method=method, params=params, client_response=client_response)

        return response

    def login(self, *, username=None, password=None):
        params = {"username": self._username, "password": self._password}
        self.send_request("POST", "/login", params=params)

    def get_node(self, node_uid):
        return self.send_request("GET", f"/node/{node_uid}")

    def get_children(self, node_uid):
        return self.send_request("GET", f"/node/{node_uid}/children")

    def create_config(self, parent_node_uid, name, pv_list):
        config_dict = {
            "configurationNode": {
                "name": name,
                "nodeType": "CONFIGURATION",
                "userName": self._username,
            },
            "configurationData": {
                "pvList": pv_list,
            },
        }
        print(f"config_dict=\n{pprint.pformat(config_dict)}")
        return self.send_request("PUT", f"/config?parentNodeId={parent_node_uid}", json=config_dict)

    def update_config(self, node_uid, name, pv_list):
        config_dict = {
            "configurationNode": {
                "name": name,
                "nodeType": "CONFIGURATION",
                "userName": self._username,
                "uniqueId": node_uid,
            },
            "configurationData": {
                "pvList": pv_list,
            },
        }
        print(f"config_dict=\n{pprint.pformat(config_dict)}")
        # return self.send_request("POST", f"/config/{node_uid}", json=config_dict)
        return self.send_request("POST", "/config", json=config_dict)
