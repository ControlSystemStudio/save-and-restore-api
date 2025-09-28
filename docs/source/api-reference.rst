=============
API Reference
=============

.. currentmodule:: save_and_restore_api

Synchronous Communication with Save-And-Restore Server
------------------------------------------------------

.. autosummary::
   :nosignatures:
   :toctree: generated

    SaveRestoreAPI

Authentication
**************

.. autosummary::
   :nosignatures:
   :toctree: generated

    SaveRestoreAPI.auth_gen
    SaveRestoreAPI.auth_set
    SaveRestoreAPI.auth_clear

Node Controller API
*******************

.. autosummary::
   :nosignatures:
   :toctree: generated

      SaveRestoreAPI.node_get
      SaveRestoreAPI.nodes_get
      SaveRestoreAPI.node_add
      SaveRestoreAPI.node_delete
      SaveRestoreAPI.nodes_delete
      SaveRestoreAPI.node_get_children
      SaveRestoreAPI.node_get_parent


Asynchronous Communication with 0MQ Server
------------------------------------------

.. autosummary::
   :nosignatures:
   :toctree: generated

    aio.SaveRestoreAPI
