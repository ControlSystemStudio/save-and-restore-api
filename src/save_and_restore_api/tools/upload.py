import argparse

# import getpass
import logging
import os

# import pprint
import save_and_restore_api

version = save_and_restore_api.__version__

logger = logging.getLogger(__name__)

BASE_URL = "http://epics-services-hxn.nsls2.bnl.local:20381/save-restore"
timeout = 2
file_name = "auto_settings.sav"

# def set_username_password(self, username=None, password=None):
#     if not isinstance(username, str):
#         print("Username: ", end="")
#         username = input()
#     if not isinstance(password, str):
#         password = getpass.getpass()

#     self._username = username
#     self._password = password


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


def split_config_name(config_name):
    if not config_name.startswith("/"):
        config_name = "/" + config_name
    _ = config_name.split("/")
    folders, name = _[1:-1], _[-1]
    return folders, name


def main():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("save-and-restore-api").setLevel("INFO")

    def formatter(prog):
        # Set maximum width such that printed help mostly fits in the RTD theme code block (documentation).
        return argparse.RawDescriptionHelpFormatter(prog, max_help_position=20, width=90)

    parser = argparse.ArgumentParser(
        description="save-and-restore-upload: create configuration based on a batch of PVs.\n"
        f"save-and-restore-api version {version}\n\n"
        "Read a batch of PVs from a file and creates a configuration in Save and Restore service.\n",
        formatter_class=formatter,
    )

    parser.add_argument(
        "--file-name",
        "-f",
        dest="file_name",
        type=str,
        default=None,
        help="File name with PV names.",
    )

    parser.add_argument(
        "--config-name",
        "-c",
        dest="config_name",
        type=str,
        default=None,
        help="Configuration name including folders, e.g. /detectors/imaging/eiger_config",
    )

    parser.add_argument(
        "--create-folders",
        dest="create_folders",
        action="store_true",
        help="Configuration name including folders, e.g. /detectors/imaging/eiger_config",
    )

    parser.add_argument(
        "--update",
        dest="config_update",
        action="store_true",
        help="Configuration name including folders, e.g. /detectors/imaging/eiger_config",
    )

    args = parser.parse_args()
    file_name = args.file_name
    config_name = args.config_name
    create_folders = args.create_folders
    config_update = args.config_update

    try:
        if args.file_name is None:
            raise ValueError("Required '--file-name' ('-f') parameter is not specified")

        if args.config_name is None:
            raise ValueError("Required '--config-name' ('-c') parameter is not specified")

        file_name = os.path.abspath(os.path.expanduser(file_name))

        print(f"file_name={file_name}")
        print(f"config_name={config_name}")
        print(f"create_folders={create_folders}")
        print(f"update={config_update}")

        if not os.path.isfile(file_name):
            raise ValueError(f"Input file '{file_name}' does not exist")

        folders, name = split_config_name(config_name)
        print(f"folders={folders}, name={name}")

    except Exception as ex:
        logger.error(f"Failed: {ex}")

    # SR = SaveRestoreAPI(base_url=BASE_URL, timeout=timeout)
    # try:
    #     pv_names = load_pvs_from_autosave_file(file_name)

    #     SR.set_username_password()
    #     SR.open()
    #     SR.login()

    #     data = SR.node_get(SR.ROOT_NODE_UID)
    #     print(f"data=\n{pprint.pformat(data)}")
    #     data = SR.node_get_children(data["uniqueId"])
    #     print(f"data=\n{pprint.pformat(data)}")
    #     parent_node_uid = data[0]["uniqueId"]
    #     name = "test5"
    #     pv_list = []
    #     for pv_name in pv_names:
    #         add_to_pv_list(pv_list, pv_name=pv_name)
    #     add_to_pv_list(pv_list, pv_name="13SIM1:{SimDetector-Cam:1}cam1:BinX")
    #     add_to_pv_list(pv_list, pv_name="13SIM1:{SimDetector-Cam:1}cam1:BinY")
    #     data = SR.create_config(parent_node_uid, name, pv_list)
    #     print(f"data=\n{pprint.pformat(data)}")
    #     node_uid = data["configurationNode"]["uniqueId"]
    #     data = SR.update_config(node_uid, name + "a", pv_list)
    #     print(f"data=\n{pprint.pformat(data)}")

    # finally:
    #     SR.close()
