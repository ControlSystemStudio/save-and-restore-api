import pytest

from save_and_restore_api import SaveRestoreAPI

base_url = "http://localhost:8080/save-restore"

admin_username, admin_password = "admin", "adminPass"
user_username, user_password = "user", "userPass"
read_username, read_password = "johndoe", "1234"


def _is_async(library):
    if library == "ASYNC":
        return True
    elif library == "THREADS":
        return False
    else:
        raise ValueError(f"Unknown library: {library!r}")


def _select_auth(*, SR, usesetauth):
    """
    Switch between using ``SR.auth_set()`` to set authentication for the whole session or
    using ``SR.auth_gen()`` to generate authentication object and pass it with each request.

    Parameters
    ----------
    SR : SaveRestoreAPI
        Instance of SaveRestoreAPI
    usesetauth : bool
        If True, use ``SR.auth_set()``, otherwise use ``SR.auth_gen()``.

    Returns
    -------
    dict
        If ``usesetauth`` is False, returns dictionary with authentication to be passed with each request,
        otherwise returns empty dictionary.
    """
    auth = {}
    if usesetauth:
        SR.auth_set(username=user_username, password=user_password)
    else:
        auth["auth"] = SR.auth_gen(username=user_username, password=user_password)
    return auth


@pytest.fixture
def clear_sar():
    """
    Clear save-and-restore database before and after the experiment.
    """

    def _clear():
        """
        Remove all nodes from the database.
        """
        with SaveRestoreAPI(base_url=base_url, timeout=2) as SR:
            SR.auth_set(username=user_username, password=user_password)

            # Create all nodes. Children always follow the parent
            n_uid = 0
            uids = [SR.ROOT_NODE_UID]
            while n_uid < len(uids):
                uid = uids[n_uid]
                res_1 = SR.node_get(uid)
                if res_1["nodeType"] == "FOLDER":
                    res_2 = SR.node_get_children(uid)
                    ch_uids = [_["uniqueId"] for _ in res_2]
                    if ch_uids:
                        uids.extend(ch_uids)
                n_uid += 1

            # Delete all nodes starting with children
            for uid in reversed(uids[1:]):
                SR.nodes_delete([uid])

    _clear()
    yield
    _clear()
