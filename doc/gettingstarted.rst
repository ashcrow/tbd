Getting Started
===============

.. _manual_installation:

Manual Installation
-------------------
To test out the current code you will need the following installed:

* Python2.6+
* virtualenv
* etcd2 (running)
* Kubernetes Cluster with a bearer token for access (running)
* (Optional) docker (running)

Set up virtualenv
~~~~~~~~~~~~~~~~~

.. include:: examples/setup_virtualenv.rst

(Optional): Run Unittests
~~~~~~~~~~~~~~~~~~~~~~~~~
If you are running from the matest master it's a good idea to verify that all
the unittests run. From the repo root...

.. include:: examples/run_unittest_example.rst


(Optional): Put Configs in Etcd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
commissaire will default back to the local files but using Etcd is where configuration should be stored.

.. include:: examples/etcd_authentication_example.rst

.. include:: examples/etcd_logging_example.rst


(Recommended) Set The Kubernetes Access Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bearer Token
````````````

To use a Bearer token:

.. note:: There is no default for the bearer token!

.. include:: examples/etcd_set_kube_bearer_token.rst


Client Certificate
``````````````````

To use a client certificate:

.. note:: There is no default for the client certificate!

.. include:: examples/etcd_set_kube_client_side_certificate.rst


(Optional): Build Docker Container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to run from Docker and would like to build the image for yourself run...

.. code-block:: shell

    docker build --tag commissaire .
    ...

Running the service
~~~~~~~~~~~~~~~~~~~

From Source
```````````
From the repo root...

**Not So Secure Mode**

.. include:: examples/run_from_source.rst

**More Secure Mode**

.. include:: examples/run_from_source_more_secure.rst


Via Docker
``````````
To run the image specify the ETCD and KUBE variables pointing towards the specific services.

**Not So Secure Mode**

.. include:: examples/run_via_docker.rst


**More Secure Mode**

.. include:: examples/run_via_docker_more_secure.rst


Adding a Cluster
~~~~~~~~~~~~~~~~
Verify that Commissaire is running as a container or in the virtual environment then execute...

.. include:: examples/create_cluster.rst

Adding a Host
~~~~~~~~~~~~~
Verify that Commissaire is running as a container or in the virtual environment then execute...

.. include:: examples/create_host.rst