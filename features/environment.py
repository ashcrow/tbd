import etcd
import json
import platform
import subprocess
import time

# XXX Reproducing commissaire.compat.urlparser because I can't seem to
#     import it from here.
if platform.python_version()[0] == '2':
    from urlparse import urlparse as _urlparse
else:
    from urllib.parse import urlparse as _urlparse
urlparse = _urlparse


def before_all(context):
    """
    Sets up anything before all tests run.
    """
    # Set SERVER via -D server=... or use a default
    context.SERVER = context.config.userdata.get(
        'server', 'http://127.0.0.1:8000')

    # Set ETCD via -D etcd=... or use a default
    context.ETCD = context.config.userdata.get(
        'etcd', 'http://127.0.0.1:2379')

    # Start etcd up via -D start-etcd=$ANYTHING
    if context.config.userdata.get('start-etcd', None):
        context.ETCD_PROCESS = subprocess.Popen('etcd', shell=True)
        time.sleep(3)

    # Connect to the etcd service
    url = urlparse(context.ETCD)
    context.etcd = etcd.Client(host=url.hostname, port=url.port)
    context.etcd.write('/commissaire/config/kubetoken', 'test')

    # Start the server up via -D start-server=$ANYTHING
    if context.config.userdata.get('start-server', None):
        # TODO: add kubernetes URL to options
        context.SERVER_PROCESS = subprocess.Popen(
            ['python', 'src/commissaire/script.py',
             '-e', context.ETCD, '-k', 'http://127.0.0.1:8080'])
        time.sleep(3)


def before_scenario(context, scenario):
    """
    Runs before every scenario.
    """
    # Reset HOST_DATA
    context.HOST_DATA = {
        "address": "",
        "status": "active",
        "os": "fedora",
        "cpus": 1,
        "memory": 1234,
        "space": 12345,
        "last_check": "",
        "ssh_priv_key": "",
    }

    # Wipe etcd state clean
    # XXX Delete individual subdirectories of '/commissaire' so we don't
    #     clobber '/commissaire/config'. Maybe reorganize so we can wipe
    #     state in one shot?  e.g. '/commissaire/state/...'
    delete_dirs = ['/commissaire/hosts',
                   '/commissaire/cluster',
                   '/commissaire/clusters']
    for dir in delete_dirs:
        try:
            context.etcd.delete(dir, recursive=True)
        except etcd.EtcdKeyNotFound:
            pass


def after_scenario(context, scenario):
    """
    Runs after every scenario.
    """
    # Wait for investigator processes to finish.
    busy_states = ('investigating', 'bootstrapping')
    try:
        etcd_resp = context.etcd.read('/commissaire/hosts', recursive=True)
        for child in etcd_resp._children:
            resp_data = etcd.EtcdResult(node=child)
            host_data = json.loads(resp_data.value)
            while host_data.get('status') in busy_states:
                context.etcd.watch(resp_data.key)
                resp_data = context.etcd.get(resp_data.key)
                host_data = json.loads(resp_data.value)
    except etcd.EtcdKeyNotFound:
        pass


def after_all(context):
    """
    Run after everything finishes.
    """
    if context.config.userdata.get('start-etcd', None):
        context.ETCD_PROCESS.kill()
    if context.config.userdata.get('start-server', None):
        context.SERVER_PROCESS.terminate()
        context.SERVER_PROCESS.wait()
