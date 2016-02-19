import etcd
# import subprocess

# XXX Reproducing commissaire.compat.urlparser because I can't seem to
#     import it from here.
import platform
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

    # Connect to the etcd service
    url = urlparse(context.ETCD)
    context.etcd = etcd.Client(host=url.hostname, port=url.port)


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

# TODO: Not needed?
'''
def before_all(context):
    """
    Start the server via a subproccess.
    """
    context.server_pipe = subprocess.Popen(
        ['python', 'src/commissaire/script.py',
         '-e', 'http://127.0.0.1:2379', '-k', 'http://127.0.0.1:8080'],
        stdout=subprocess.PIPE)


def after_all(context):
    """
    Kill the server at the end.
    """
    context.server_pipe.kill()
'''
