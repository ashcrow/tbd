.. warning::

   Do **not** point to a real instance of commissaire. e2e/BDD tests will
   simulate real usage on a running server will probably cause damage.

.. code-block:: shell

   # start up etcd
   # start up commissaire
   (virtualenv)$ behave -D server=$http://127.0.0.1:8000 -D etcd=http://127.0.0.1:2379
   ...
