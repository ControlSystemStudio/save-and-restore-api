import argparse

# import getpass
import logging
import os
from dataclasses import dataclass

# import pprint
import save_and_restore_api

version = save_and_restore_api.__version__

logger = logging.getLogger(__name__)

EXIT_CODE_SUCCESS = 0
EXIT_CODE_CLI_PARAMETER_ERROR = -1

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


@dataclass
class Settings:
    command: str = None
    operation: str = None
    base_url: str = None
    create_folders: bool = False
    user_name: str = None
    user_password: str = None
    config_name: str = None
    file_name: str = None
    file_format: str = None


def parse_args(settings):
    """
    Parse command line arguments. Results are saved in the ``settings`` object.
    """

    def formatter(prog):
        # Set maximum width such that printed help mostly fits in the RTD theme code block (documentation).
        return argparse.RawDescriptionHelpFormatter(prog, max_help_position=20, width=90)

    parser = argparse.ArgumentParser(
        description="save-and-restore: CLI tool for operations on Save-and-Restore nodes.\n"
        f"save-and-restore-api version {version}\n\n"
        "The tool connects to the save-and-restore service. Host URL specified as the '--base-url'\n"
        "parameter. User name (--user-name) is used for authentication with the service.\n"
        "Currently supported operations:\n"
        "    CONFIG GET: read an existing config node.\n"
        "    CONFIG ADD: create a new config node. The config node is created/updated based\n"
        "        on the list of PVs loaded from file. The file name and format are specified\n"
        "        using the '--file-name' ('-f') and '--file-format' parameters.\n"
        "    CONFIG UPDATE: update an existing config node.\n"
        "\n"
        "Supported environment variables:\n"
        "    SAVE_AND_RESTORE_API_BASE_URL: alternative way to specify the host URL.\n"
        "    SAVE_AND_RESTORE_API_USER_NAME: alternative way to specify the user name.\n"
        "    SAVE_AND_RESTORE_API_USER_PASSWORD: user password (use with caution).\n"
        "CLI parameters override the respective environment variables.\n"
        "\n"
        "Examples:\n"
        "\n"
        "  Read the configuration node named 'eiger_config'. Print the full config data:\n"
        "\n"
        "  save-and-restore --host-url http://localhost:8080/save-restore \\\n"
        "      CONFIG GET --config-name /detectors/imaging/eiger_config --show-data=ON\n"
        "\n"
        "  Create a new configuration node named 'eiger_config':\n"
        "\n"
        "  save-and-restore --host-url=http://localhost:8080/save-restore --username=user\\\n"
        "      --create-folders=true CONFIG ADD --config-name=/detectors/imaging/eiger_config \\\n"
        "      --file-name=eiger_pvs.sav --file-format=autosave\n"
        "\n"
        "  Update an existing configuration node named 'eiger_config':\n"
        "\n"
        "  save-and-restore --host-url http://localhost:8080/save-restore --username=user\\\n"
        "      CONFIG UPDATE --config-name /detectors/imaging/eiger_config \\\n"
        "      --file-name eiger_pvs.sav --file-format autosave\n",
        formatter_class=formatter,
    )

    parser.add_argument(
        "--base-url",
        dest="base_url",
        type=str,
        default=None,
        help="Base URL for communication with the host, e.g. http://localhost:8080/save-restore.",
    )

    parser.add_argument(
        "--user-name",
        dest="user_name",
        type=str,
        default=None,
        help=(
            "User name for authentication with save-and-restore service. If the operation requires "
            "authentication and the user name is not specified, the user is prompted for the name. "
            "The user is also prompted for the password."
        ),
    )

    parser.add_argument(
        "--create-folders",
        dest="create_folders",
        type=str,
        choices=["ON", "OFF"],
        default="OFF",
        help=(
            "Create missing folders if required to complete the operation. The operation fails "
            "if the parameter is OFF and the required folders are missing. Default: '%(default)s'."
        ),
    )

    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Enable print of the debug output, including tracebacks.",
    )

    subparser_command = parser.add_subparsers(dest="command", help="Select the operation type.")

    parser_config = subparser_command.add_parser(
        "LOGIN",
        help="Check user login credentials.",
        formatter_class=formatter,
    )

    parser_config = subparser_command.add_parser(
        "CONFIG",
        help="Operations on configuration nodes.",
        formatter_class=formatter,
    )

    subparser_config_operation = parser_config.add_subparsers(dest="operation", help="Select the operation.")
    parser_config_get = subparser_config_operation.add_parser(
        "GET",
        help="Read configuration node. The command may be used to check if a config node exists.",
        formatter_class=formatter,
    )

    parser_config_get.add_argument(
        "--config-name",
        "-c",
        dest="config_name",
        type=str,
        default=None,
        help="Configuration name including folders, e.g. /detectors/imaging/eiger_config",
    )

    parser_config_get.add_argument(
        "--show-data",
        dest="show_data",
        type=str,
        choices=["ON", "OFF"],
        default="OFF",
        help="Print the loaded config data. The config node information is always printed. "
        "Default: '%(default)s'.",
    )

    # subparser_config_operation = parser_config.add_subparsers(dest="operation", help="Select the operation.")
    parser_config_add = subparser_config_operation.add_parser(
        "ADD",
        help="Add (create) a new configuration node.",
        formatter_class=formatter,
    )

    parser_config_add.add_argument(
        "--config-name",
        "-c",
        dest="config_name",
        type=str,
        default=None,
        help="Configuration name including folders, e.g. /detectors/imaging/eiger_config",
    )

    parser_config_add.add_argument(
        "--file-name",
        "-f",
        dest="file_name",
        type=str,
        default=None,
        help="Name of the file used as a source of PV names.",
    )

    parser_config_add.add_argument(
        "--file-format",
        dest="file_format",
        type=str,
        choices=["autosave"],
        default="autosave",
        help="Format of the file specified by '--file-name'. Default: '%(default)s'",
    )

    parser_config_add.add_argument(
        "--show-data",
        dest="show_data",
        type=str,
        choices=["ON", "OFF"],
        default="OFF",
        help="Print the loaded config data. The config node information is always printed. "
        "Default: '%(default)s'.",
    )

    parser_config_update = subparser_config_operation.add_parser(
        "UPDATE", help="Update an existing configuration node."
    )

    parser_config_update.add_argument(
        "--config-name",
        "-c",
        dest="config_name",
        type=str,
        default=None,
        help="Configuration name including folders, e.g. /detectors/imaging/eiger_config",
    )

    parser_config_update.add_argument(
        "--file-name",
        "-f",
        dest="file_name",
        type=str,
        default=None,
        help="Name of the file used as a source of PV names.",
    )

    parser_config_update.add_argument(
        "--file-format",
        dest="file_format",
        type=str,
        choices=["autosave"],
        default="autosave",
        help="Format of the file specified by '--file-name'. Default: '%(default)s'",
    )

    parser_config_update.add_argument(
        "--show-data",
        dest="show_data",
        type=str,
        choices=["ON", "OFF"],
        default="OFF",
        help="Print the loaded config data. The config node information is always printed. "
        "Default: '%(default)s'.",
    )

    class ExitOnError(Exception):
        pass

    try:
        args = parser.parse_args()

        settings.base_url = args.base_url or os.environ.get("SAVE_AND_RESTORE_API_BASE_URL", None)
        settings.create_folders = args.create_folders
        settings.user_name = args.user_name or os.environ.get("SAVE_AND_RESTORE_API_USER_NAME", None)
        settings.user_password = os.environ.get("SAVE_AND_RESTORE_API_USER_PASSWORD", None)
        settings.verbose_output = args.verbose

        if not settings.base_url:
            logger.error("Required '--base-url' ('-u') parameter is not specified")
            parser.print_help()
            raise ExitOnError()

        success = False
        if args.command == "CONFIG":
            settings.command = args.command
            if args.operation == "ADD":
                settings.operation = args.operation
                settings.config_name = args.config_name
                settings.file_name = args.file_name
                settings.file_format = args.file_format
                settings.show_data = args.show_data == "ON"
                success = True
                if not settings.config_name:
                    logger.error("Required '--config-name' ('-c') parameter is not specified")
                    success = False
                if not settings.file_name:
                    logger.error("Required '--file-name' ('-f') parameter is not specified")
                    success = False
                if not success:
                    parser_config_add.print_help()
                    raise ExitOnError()
            elif args.operation == "UPDATE":
                settings.operation = args.operation
                settings.config_name = args.config_name
                settings.file_name = args.file_name
                settings.file_format = args.file_format
                settings.show_data = args.show_data == "ON"
                success = True
                if not settings.config_name:
                    logger.error("Required '--config-name' ('-c') parameter is not specified")
                    success = False
                if not settings.file_name:
                    logger.error("Required '--file-name' ('-f') parameter is not specified")
                    success = False
                if not success:
                    parser_config_add.print_help()
                    raise ExitOnError()
            if not success:
                parser_config.print_help()
                raise ExitOnError()

        elif args.command == "LOGIN":
            settings.command = args.command

        else:
            parser.print_help()
            raise ExitOnError()

    except ExitOnError:
        exit(EXIT_CODE_CLI_PARAMETER_ERROR)


def print_settings(settings):
    """
    Print settings for user convenience.
    """
    operation = settings.command
    if settings.operation:
        operation += " " + settings.operation
    print(f"\nOperation: {operation}")
    print(f"Base URL: {settings.base_url}")
    print(f"User name: {settings.user_name}")
    print(f"User password: {'*********' if settings.user_password else None}")
    print(f"Verbose output: {settings.verbose_output}")
    if settings.command == "CONFIG":
        print(f"Config name: {settings.config_name}")
        print(f"Show data: {settings.show_data}")
        if settings.operation in ("ADD", "UPDATE"):
            print(f"Create folders: {settings.create_folders}")
            print(f"File name: {settings.file_name}")
            print(f"File format: {settings.file_format}")
    print("")


def main():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("save-and-restore-api").setLevel("INFO")

    settings = Settings()
    parse_args(settings)
    print_settings(settings)

    # try:
    #     if args.file_name is None:
    #         raise ValueError("Required '--file-name' ('-f') parameter is not specified")

    #     if args.config_name is None:
    #         raise ValueError("Required '--config-name' ('-c') parameter is not specified")

    #     file_name = os.path.abspath(os.path.expanduser(file_name))

    #     print(f"file_name={file_name}")
    #     print(f"config_name={config_name}")
    #     print(f"create_folders={create_folders}")
    #     print(f"update={config_update}")

    #     if not os.path.isfile(file_name):
    #         raise ValueError(f"Input file '{file_name}' does not exist")

    #     folders, name = split_config_name(config_name)
    #     print(f"folders={folders}, name={name}")

    # except Exception as ex:
    #     logger.error(f"Failed: {ex}")

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
