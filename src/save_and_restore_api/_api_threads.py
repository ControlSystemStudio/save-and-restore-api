import httpx

from ._api_base import _SaveRestoreAPI_Base


class SaveRestoreAPI(_SaveRestoreAPI_Base):
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

    # =============================================================================================
    #                         INFO-CONTROLLER API METHODS
    # =============================================================================================

    def info_get(self):
        """
        Returns information about the Save and Restore service.

        API: GET /
        """
        method, url = self._prepare_info_get()
        return self.send_request(method, url)

    def version_get(self):
        """
        Returns information on the name and current version of the service.

        API: GET /verson
        """
        method, url = self._prepare_version_get()
        return self.send_request(method, url)

    # =============================================================================================
    #                         SEARCH-CONTROLLER API METHODS
    # =============================================================================================

    def search(self, allRequestParams):
        """
        Send search query to the database. Example search queries (``allRequestParams``):
        search for nodes with name containing 'test config': ``{"name": "test config"}``,
        search for nodes with the description containing 'backup pvs': ``{"description": "backup pvs"}``,

        Returns a dictionary with the following keys: ``hitCount`` - the number of matching nodes,
        ``nodes`` - a list of matching nodes (not including data).

        API: GET /search
        """
        method, url, url_params = self._prepare_search(allRequestParams=allRequestParams)
        return self.send_request(method, url, url_params=url_params)

    # =============================================================================================
    #                         HELP-RESOURCE API METHODS
    # =============================================================================================

    def help(self, what, *, lang=None):
        """
        Download help pages, e.g. /help/SearchHelp

        API: GET /help/{what}?lang={lang}
        """
        method, url, url_params = self._prepare_help(what=what, lang=lang)
        return self.send_request(method, url, url_params=url_params)

    # =============================================================================================
    #                         AUTHENTICATION-CONTROLLER API METHODS
    # =============================================================================================

    def login(self, *, username=None, password=None):
        """
        Validate user credentials and return user information.

        API: POST /login
        """
        method, url, params = self._prepare_login(username=username, password=password)
        return self.send_request(method, url, params=params)

    # =============================================================================================
    #                         NODE-CONTROLLER API METHODS
    # =============================================================================================

    def node_get(self, uniqueNodeId):
        """
        Returns the node with specified node UID.

        API: GET /node/{uniqueNodeId}
        """
        method, url = self._prepare_node_get(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def nodes_get(self, uniqueIds):
        """
        Returns nodes specified by a list of UIDs.

        API: GET /nodes
        """
        method, url, params = self._prepare_nodes_get(uniqueIds=uniqueIds)
        return self.send_request(method, url, params=params)

    def node_add(self, parentNodeId, *, name, nodeType, auth=None, **kwargs):
        """
        Creates a new node under the specified parent node. Required parameters:
        ``name`` and ``nodeType``. Supported types: ``"FOLDER"``, ``"CONFIGURATION"``.

        API: PUT /node?parentNodeId={parentNodeId}
        """
        method, url, url_params, params = self._prepare_node_add(
            parentNodeId=parentNodeId, name=name, nodeType=nodeType, **kwargs
        )
        return self.send_request(method, url, url_params=url_params, params=params, auth=auth)

    def node_delete(self, nodeId, *, auth=None):
        """
        Deletes the node with specified node ID. The call fails if the node can
        not be deleted.

        API: DELETE /node/{nodeId}
        """
        method, url = self._prepare_node_delete(nodeId=nodeId)
        return self.send_request(method, url, auth=auth)

    def nodes_delete(self, uniqueIds, *, auth=None):
        """
        Deletes multiple nodes specified as a list of UIDs. The call fails if
        any of the nodes can not be deleted.

        API: DELETE /node
        """
        method, url, params = self._prepare_nodes_delete(uniqueIds=uniqueIds)
        return self.send_request(method, url, params=params, auth=auth)

    def node_get_children(self, uniqueNodeId):
        """
        Returns the list of child nodes for the specified node UID.

        API: GET /node/{uniqueNodeId}/children
        """
        method, url = self._prepare_node_get_children(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def node_get_parent(self, uniqueNodeId):
        """
        Returns the parent node for the specified node UID.

        API: GET /node/{uniqueNodeId}/parent
        """
        method, url = self._prepare_node_get_parent(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    # =============================================================================================
    #                         CONFIGURATION-CONTROLLER API METHODS
    # =============================================================================================

    def config_get(self, uniqueNodeId):
        """
        Returns the config data for the node with specified node UID. Returns only the configuration
        data. To get the node metadata use ``node_get()``.

        API: GET /config/{uniqueNodeId}
        """
        method, url = self._prepare_config_get(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def config_create(self, parentNodeId, *, configurationNode, configurationData, auth=None):
        """
        Creates a new configuration node under the specified parent node. Parameters:
        ``configurationNode`` - the node metadata, ``configurationData`` - the configuration data.

        Minimum required fields:

        configurationNode = {"name": "test_config"}
        configurationData = {"pvList": [{"pvName": "PV1"}, {"pvName": "PV2"}]}

        The fields ``uniqueId``, ``nodeType``, ``userName`` in ``configurationNode`` are ignored
        and overwritten by the server.

        The function returns the dictionary with ``configurationNode`` and ``configurationData``
        as returned by the server.

        API: PUT /config?parentNodeId={parentNodeId}
        """
        method, url, params = self._prepare_config_create(
            parentNodeId=parentNodeId, configurationNode=configurationNode, configurationData=configurationData
        )
        return self.send_request(method, url, params=params, auth=auth)

    def config_update(self, *, configurationNode, configurationData, auth=None):
        """
        Updates an existing configuration node. Parameters ``configurationNode`` and ``configurationData``
        should be loaded using ``node_get()`` and ``config_get()`` respectively. Both parameters must
        contain correct ``uniqueID`` field values.

        API: POST /config
        """
        method, url, params = self._prepare_config_update(
            configurationNode=configurationNode, configurationData=configurationData
        )
        return self.send_request(method, url, params=params, auth=auth)

    # =============================================================================================
    #                         TAG-CONTROLLER API METHODS
    # =============================================================================================

    def tags_get(self):
        """
        Returns all existing tags.

        API: GET /tags
        """
        method, url = self._prepare_tags_get()
        return self.send_request(method, url)

    def tags_add(self, *, uniqueNodeIds, tag, auth=None):
        """
        Adds ``tag`` to nodes specified by a list of UIDs ``uniqueNodeIds``. The ``tag``
        dictionary must contain the ``name`` key and optionally ``comment`` key.

        API: POST /tags
        """
        method, url, params = self._prepare_tags_add(uniqueNodeIds=uniqueNodeIds, tag=tag)
        return self.send_request(method, url, params=params, auth=auth)

    def tags_delete(self, *, uniqueNodeIds, tag, auth=None):
        """
        Deletes ``tag`` to nodes specified by a list of UIDs ``uniqueNodeIds``. The ``tag``
        dictionary must contain the ``name`` key and optionally ``comment`` key.

        API: DELETE /tags
        """
        method, url, params = self._prepare_tags_delete(uniqueNodeIds=uniqueNodeIds, tag=tag)
        return self.send_request(method, url, params=params, auth=auth)

    # =============================================================================================
    #                         TAKE-SNAPSHOT-CONTROLLER API METHODS
    # =============================================================================================

    def take_snapshot_get(self, uniqueNodeId):
        """
        Reads and returns a list of PV values based on configuration specified by
        ``uniqueNodeId``. The API does not create any nodes in the database.
        The returned list format matches the format of ``snapshotData["snapshotItems"]``.

        API: GET /take-snapshot/{uniqueNodeId}
        """
        method, url = self._prepare_take_snapshot_get(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def take_snapshot_save(self, uniqueNodeId, *, name=None, comment=None, auth=None):
        """
        Reads PV values based on configuration specified by ``uniqueNodeId`` and
        saves the values in a new snapshot node. The parameter ``name`` specifies
        the name of the snapshot node and ``comment`` specifies the node description.

        API: PUT /take-snapshot/{uniqueNodeId}
        """
        method, url, url_params = self._prepare_take_snapshot_save(
            uniqueNodeId=uniqueNodeId, name=name, comment=comment
        )
        return self.send_request(method, url, url_params=url_params, auth=auth)

    # =============================================================================================
    #                         SNAPSHOT-CONTROLLER API METHODS
    # =============================================================================================

    def snapshot_get(self, uniqueId):
        """
        Returns snapshot data (``snapshotData``) for the snapshot specified by ``uniqueId``.

        API: GET /snapshot/{uniqueId}
        """
        method, url = self._prepare_snapshot_get(uniqueId=uniqueId)
        return self.send_request(method, url)

    def snapshot_add(self, parentNodeId, *, snapshotNode, snapshotData, auth=None):
        """
        Upload data for the new snapshot and save it to the database. The new node is created
        under the existing configuration node specified by ``parentNodeId``.

        API: PUT /snapshot?parentNodeId={parentNodeId}
        """
        method, url, params = self._prepare_snapshot_add(
            parentNodeId=parentNodeId, snapshotNode=snapshotNode, snapshotData=snapshotData
        )
        return self.send_request(method, url, params=params, auth=auth)

    def snapshot_update(self, *, snapshotNode, snapshotData, auth=None):
        """
        Upload and update data for an existing snapshot. Both ``snapshotNode`` and ``snapshotData``
        must have valid ``uniqueId`` fields pointing to an existing node.

        API: POST /snapshot
        """
        method, url, params = self._prepare_snapshot_update(snapshotNode=snapshotNode, snapshotData=snapshotData)
        return self.send_request(method, url, params=params, auth=auth)

    def snapshots_get(self):
        """
        Returns a list of all existing snapshots (list of ``snapshotNode`` objects).

        API: GET /snapshots
        """
        method, url = self._prepare_snapshots_get()
        return self.send_request(method, url)

    # =============================================================================================
    #                     SNAPSHOT-RESTORE-CONTROLLER API METHODS
    # =============================================================================================

    def restore_node(self, nodeId, *, auth=None):
        """
        Restore PVs based on the data from an existing snapshot node specified by nodeId.

        Returns a list of snapshotItems that were NOT restored. Ideally the list should be empty.

        API: POST /restore/node
        """
        method, url, url_params = self._prepare_restore_node(nodeId=nodeId)
        return self.send_request(method, url, url_params=url_params, auth=auth)

    def restore_items(self, *, snapshotItems, auth=None):
        """
        Restore PVs based on the list of snapshot items passed with the request. The list
        format matches the format of ``snapshotData["snapshotItems"]``

        Returns a list of snapshotItems that were NOT restored. Ideally the list should be empty.

        API: POST /restore/items
        """
        method, url, params = self._prepare_restore_items(snapshotItems=snapshotItems)
        return self.send_request(method, url, params=params, auth=auth)

    # =============================================================================================
    #                     COMPARISON-CONTROLLER API METHODS
    # =============================================================================================

    def compare(self, nodeId, *, tolerance=None, compareMode=None, skipReadback=None):
        """
        Compare stored PV values with live values for the selected snapshot or composite snapshot.
        The snapshot is selected by ``nodeId``. The API returns a list of results for each PV in
        the snapshot.

        API: GET /compare/{nodeId}
        """
        method, url, url_params = self._prepare_compare(
            nodeId=nodeId, tolerance=tolerance, compareMode=compareMode, skipReadback=skipReadback
        )
        return self.send_request(method, url, url_params=url_params)

    # =============================================================================================
    #                     STRUCTURE-CONTROLLER API METHODS
    # =============================================================================================

    def structure_move(self, nodeIds, *, newParentNodeId, auth=None):
        """
        Move nodes specified by a list of UIDs ``nodeIds`` to a new parent node specified
        by ``newParentNodeId``. The API requires 'admin' priviledges.

        API: POST /move
        """
        method, url, params, url_params = self._prepare_structure_move(
            nodeIds=nodeIds, newParentNodeId=newParentNodeId
        )
        return self.send_request(method, url, params=params, url_params=url_params, auth=auth)

    def structure_copy(self, nodeIds, *, newParentNodeId, auth=None):
        """
        Copy nodes specified by a list of UIDs ``nodeIds`` to a new parent node specified
        by ``newParentNodeId``. The API requires 'admin' priviledges.

        API: POST /copy
        """
        method, url, params, url_params = self._prepare_structure_copy(
            nodeIds=nodeIds, newParentNodeId=newParentNodeId
        )
        return self.send_request(method, url, params=params, url_params=url_params, auth=auth)

    def structure_path_get(self, uniqueNodeId):
        """
        Get path for the node with specified uniqueNodeId.

        API: GET /path/{uniqueNodeId}
        """
        method, url = self._prepare_structure_path_get(uniqueNodeId=uniqueNodeId)
        return self.send_request(method, url)

    def structure_path_nodes(self, path):
        """
        Get a list of nodes that match the specified path. The path can point to multiple
        nodes as long as node type is different (e.g. a folder and a configuration may have
        the same name).

        API: GET /path
        """
        method, url, url_params = self._prepare_structure_path_nodes(path=path)
        return self.send_request(method, url, url_params=url_params)
