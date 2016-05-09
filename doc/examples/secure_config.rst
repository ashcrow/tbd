.. note::

   Using client side certificates to access etcd/kubernetes will require proper configuration within etcd/kubernetes.

.. code-block:: shell

   (virtualenv)$ cat /etc/commissaire/commissaire.conf
   {
       "tls-keyfile": "/path/to/server.key",
       "tls-certificate": "/path/to/server.crt",
       "etcd-uri": "https://192.168.152.100:2379",
       "etcd-cert-path": "/path/to/etcd_clientside.crt",
       "etcd-cert-key-path": "/path/to/etcd_clientside.key",
       "kube-uri": "https://192.168.152.101:8080",
       "authentication-plugin": {
           "name": "commissaire.authentication.httpbasicauth",
           "users": {
               "a": {
                   "hash": "$2a$12$GlBCEIwz85QZUCkWYj11he6HaRHufzIvwQjlKeu7Rwmqi/mWOpRXK"
               }
           }
       }
   }

