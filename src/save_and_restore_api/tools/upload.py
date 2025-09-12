import getpass
import logging
import pprint

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "http://epics-services-hxn.nsls2.bnl.local:20381/save-restore"
timeout = 2
file_name = "auto_settings.sav"


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
        self._client = httpx.Client(base_url=BASE_URL, timeout=timeout, auth=auth)

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


def add_to_pv_list(pv_list, *, pv_name):
    pv_list.append({"pvName": pv_name})


def load_pvs_from_autosave_file(file_name):
    pv_names = []
    with open(file_name) as f:
        for line in f:
            ln = line.strip()
            if ln.startswith("#") or ln.startswith("<"):
                continue
            pv_name = ln.split(" ")[0]
            if pv_name:
                pv_names.append(pv_name)
    return pv_names


def main():
    logging.basicConfig(level=logging.WARNING)
    # logging.getLogger("bluesky_queueserver").setLevel("INFO")

    SR = SaveRestoreAPI(base_url=BASE_URL, timeout=timeout)
    try:
        pv_names = load_pvs_from_autosave_file(file_name)

        SR.set_username_password()
        SR.open()
        SR.login()

        data = SR.get_node(SR.ROOT_NODE_UID)
        print(f"data=\n{pprint.pformat(data)}")
        data = SR.get_children(data["uniqueId"])
        print(f"data=\n{pprint.pformat(data)}")
        parent_node_uid = data[0]["uniqueId"]
        name = "test5"
        pv_list = []
        for pv_name in pv_names:
            add_to_pv_list(pv_list, pv_name=pv_name)
        add_to_pv_list(pv_list, pv_name="13SIM1:{SimDetector-Cam:1}cam1:BinX")
        add_to_pv_list(pv_list, pv_name="13SIM1:{SimDetector-Cam:1}cam1:BinY")
        data = SR.create_config(parent_node_uid, name, pv_list)
        print(f"data=\n{pprint.pformat(data)}")
        node_uid = data["configurationNode"]["uniqueId"]
        data = SR.update_config(node_uid, name + "a", pv_list)
        print(f"data=\n{pprint.pformat(data)}")

    finally:
        SR.close()
