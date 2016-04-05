.. code-block:: shell

   (virtualenv)$  etcdctl set '/atomic01/network/config' '{"Network": "172.16.0.0/12", "SubnetLen": 24, "Backend": {"Type": "vxlan"}}'
   ...
