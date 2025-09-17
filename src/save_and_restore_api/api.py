import getpass

# import logging
import pprint

import httpx


class SaveRestoreAPI:
    def __init__(self, *, base_url, timeout):
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

    def login(self, *, username=None, password=None):
        params = {"username": self._username, "password": self._password}
        self.send_request("POST", "/login", json=params)

    def send_request(self, method, url, **kwargs):
        response = self._client.request(method, url, **kwargs)

        print(f"{response.request.url=}")
        print(f"{response.headers.get('content-type')=}")

        if response.status_code != 200:
            print(f"Request failed: status code {response.status_code}")
            print(f"Error message: {response.text}")
            raise Exception(f"Request failed with code {response.status_code}")

        if response.headers.get("content-type") == "application/json":
            data = response.json()
        else:
            data = {}

        return data

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
