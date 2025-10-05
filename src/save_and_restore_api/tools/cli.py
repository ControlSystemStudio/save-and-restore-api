import argparse
import getpass
import logging
import os
import pprint
import sys
from dataclasses import dataclass

import save_and_restore_api
from save_and_restore_api import SaveRestoreAPI

version = save_and_restore_api.__version__

logger = logging.getLogger("save-and-restore-api")

EXIT_CODE_SUCCESS = 0
EXIT_CODE_CLI_PARAMETER_ERROR = -1
EXIT_CODE_OPERATION_FAILED = -2


# BASE_URL = "http://epics-services-hxn.nsls2.bnl.local:20381/save-restore"
# timeout = 5
# file_name = "auto_settings.sav"


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
    timeout: float = 5


def setup_loggers(*, log_level, name="save-and-restore-api"):
    """
    Configure loggers.

    Parameters
    ----------
    name: str
        Module name (typically ``__name__``)
    log_level
        Logging level (e.g. ``logging.INFO``, ``"INFO"`` or ``20``)
    """
    log_stream_handler = logging.StreamHandler(sys.stdout)
    log_stream_handler.setLevel(log_level)
    if (
        (log_level == logging.DEBUG)
        or (log_level == "DEBUG")
        or (isinstance(log_level, int) and (log_level <= 10))
    ):
        log_stream_format = "[%(levelname)1.1s %(asctime)s.%(msecs)03d %(name)s %(module)s:%(lineno)d] %(message)s"
    else:
        log_stream_format = "[%(levelname)1.1s %(asctime)s %(name)s] %(message)s"

    log_stream_handler.setFormatter(logging.Formatter(fmt=log_stream_format))
    logging.getLogger(name).handlers.clear()
    logging.getLogger(name).addHandler(log_stream_handler)
    logging.getLogger(name).setLevel(log_level)
    logging.getLogger(name).propagate = False


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
            if args.operation == "GET":
                settings.operation = args.operation
                settings.config_name = args.config_name
                settings.show_data = args.show_data == "ON"
                success = True
                if not settings.config_name:
                    logger.error("Required '--config-name' ('-c') parameter is not specified")
                    success = False
                if not success:
                    parser_config_get.print_help()
                    raise ExitOnError()

            elif args.operation == "ADD":
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

        if settings.file_name:
            settings.file_name = os.path.abspath(os.path.expanduser(settings.file_name))

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


def set_username_password(settings):
    user_name, password = settings.user_name, settings.user_password
    user_name_interactive = False
    if not isinstance(user_name, str) or not user_name:
        user_name_interactive = True
        print("Username: ", end="")
        user_name = input()
    if not isinstance(password, str):
        if not user_name_interactive:
            print(f"Username: {user_name}")
        password = getpass.getpass()
    settings.user_name = user_name
    settings.user_password = password
    print("")


def process_login_command(settings):
    """
    Process the LOGIN command.
    """
    success = False
    set_username_password(settings)

    with SaveRestoreAPI(base_url=settings.base_url, timeout=settings.timeout) as SR:
        # SR.auth_set(username=settings.user_name, password=settings.user_password)
        try:
            logger.debug("Sending 'login' request ...")
            response = SR.login(username=settings.user_name, password=settings.user_password)
            logger.debug(f"Response received: {response}")
            print(f"Login successful. Response: \n{pprint.pformat(response)}")
            success = True
        except Exception as ex:
            logger.error(f"Login failed: {ex}")
            if settings.verbose_output:
                logger.exception(ex)

    return success


def check_node_exists(SR, config_name, *, node_type="CONFIGURATION"):
    """
    Returns uniqueId of the node if 'config_name' points to an existing configuration node.
    Otherwise returns None.
    """
    if node_type not in ("CONFIGURATION", "FOLDER"):
        raise ValueError(f"Unsupported node type: {node_type}")
    try:
        nodes = SR.structure_path_nodes(config_name)
    except SR.HTTPClientError:
        nodes = []
    config_nodes = [_ for _ in nodes if _["nodeType"] == node_type]
    if config_nodes:
        return config_nodes[0]["uniqueId"]
    else:
        return None


def split_node_path(node_path):
    """
    Split node path into the list of folders and the node name.
    """
    if not node_path.startswith("/"):
        node_path = "/" + node_path
    _ = node_path.split("/")
    folders, name = _[1:-1], _[-1]
    return folders, name


def create_missing_folders(SR, config_name, *, create_folders=False):
    """
    Create folders if they do not exist. Folders are created only if 'create_folders' is True.
    Return node_uid for the folder node, or None if the operation fails.
    """
    folders, name = split_node_path(config_name)
    node_uid = check_node_exists(SR, config_name, node_type="FOLDER")
    if create_folders and not node_uid:
        path, parent_uid = "", SR.ROOT_NODE_UID
        for f in folders:
            path += f"/{f}"
            node_uid = check_node_exists(SR, path, node_type="FOLDER")
            if not node_uid:
                response = SR.node_add(parent_uid, name=f, nodeType="FOLDER")
                node_uid = response["uniqueId"]
            parent_uid = node_uid
    return node_uid


def load_pvs_from_file(file_name, *, file_format):
    """
    Load PV names from file.

    Parameters
    ----------
    file_name: str
        Name of the file containing PV names.
    file_format: str
        Format of the file. Supported formats: "autosave".

    Returns
    -------
    list(str)
        List of PV names loaded from file.
    """
    pv_names = []
    if file_format == "autosave":
        with open(file_name) as f:
            for line in f:
                ll = line.strip()
                if ll.startswith("#") or ll.startswith("<"):
                    continue
                pv_name = ll.split(" ")[0]
                if pv_name:
                    pv_names.append(pv_name)
        # Convert PV list to the format accepted by the API
        pv_names = [{"pvName": _} for _ in pv_names]
    else:
        raise ValueError(f"Unsupported file format: {file_format}.")
    return pv_names


def process_config_command(settings):
    success = False

    if settings.file_name and not os.path.isfile(settings.file_name):
        print(f"Input file '{settings.file_name}' does not exist.")
        return False

    if settings.operation != "GET":
        set_username_password(settings)

    with SaveRestoreAPI(base_url=settings.base_url, timeout=settings.timeout) as SR:
        if settings.operation != "GET":
            SR.auth_set(username=settings.user_name, password=settings.user_password)
        try:
            node_uid = check_node_exists(SR, settings.config_name, node_type="CONFIGURATION")
            config_node = SR.node_get(node_uid) if node_uid else None
            config_data = SR.config_get(node_uid) if node_uid else None

            if settings.operation == "GET":
                if node_uid is None:
                    print(f"Config node '{settings.config_name}' does not exist.")
                else:
                    print(f"Config node:\n{pprint.pformat(config_node)}")
                    if settings.show_data:
                        print(f"Config data:\n{pprint.pformat(config_data)}")
                    success = True
            elif settings.operation == "ADD":
                if node_uid:
                    print(f"Config node '{settings.config_name}' already exists.")
                else:
                    pv_list = load_pvs_from_file(settings.file_name, file_format=settings.file_format)
                    # do something if pv_list is empty !!!
                    parent_uid = create_missing_folders(
                        SR, settings.config_name, create_folders=settings.create_folders
                    )
                    if parent_uid is None:
                        print(f"The folder '{settings.config_name}' does not exist.")
                    else:
                        _, name = split_node_path(settings.config_name)
                        response = SR.config_add(
                            parent_uid,
                            configurationNode={"name": name},
                            configurationData={"pvList": []},
                        )
                        print(f"Config node created:\n{pprint.pformat(response['configurationNode'])}")
                        if settings.show_data:
                            print(f"Config data:\n{pprint.pformat(response['configurationData'])}")
                        success = True
            elif settings.operation == "UPDATE":
                if not node_uid:
                    print(f"Config node '{settings.config_name}' does not exist.")
                else:
                    pv_list = load_pvs_from_file(settings.file_name, file_format=settings.file_format)
                    # do something if pv_list is empty !!!
                    config_data["pvList"] = pv_list
                    response = SR.config_update(
                        configurationNode=config_node,
                        configurationData=config_data,
                    )
                    print(f"Config node modified:\n{pprint.pformat(response['configurationNode'])}")
                    if settings.show_data:
                        print(f"Config data:\n{pprint.pformat(response['configurationData'])}")
                    success = True

        except Exception as ex:
            logger.error(f"Login failed: {ex}")
            if settings.verbose_output:
                logger.exception(ex)
    return success


def main():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("save-and-restore-api").setLevel("INFO")

    settings = Settings()
    parse_args(settings)
    print_settings(settings)

    setup_loggers(
        log_level=logging.DEBUG if settings.verbose_output else logging.INFO,
        name="save-and-restore-api",
    )

    success = False
    if settings.command == "LOGIN":
        success = process_login_command(settings)
    elif settings.command == "CONFIG":
        success = process_config_command(settings)
    else:
        logger.error(f"Unsupported command: {settings.command}")

    if not success:
        exit(EXIT_CODE_OPERATION_FAILED)
