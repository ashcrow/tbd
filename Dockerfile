FROM fedora
MAINTAINER Red Hat, Inc. <container-tools@redhat.com>

RUN dnf -y update && dnf -y install --setopt=tsflags=nodocs python-pip python-virtualenv git etcd gcc rpm-build libffi-devel && dnf clean all

ENV MHM_RELEASE v0.0.0
ENV PYTHONPATH  /commissaire/src/

LABEL k8s.io/display-name="MHM v0.0.0" \
      openshift.io/expose-services="2379:http" \

RUN git clone https://github.com/projectatomic/commissaire.git \
    cd commissaire \
    virtualenv . \
    . bin/activate \
    pip install -r requirements.txt \
    pip freeze > installed-python-deps.txt \
    curl -s $ETCD:2379/v2/keys/commissaire/config/logger | grep -qci -e 'errorCode' && cat conf/logger.json | etcdctl set '/commissaire/config/logger' \
    curl -s $ETCD:2379/v2/keys/commissaire/config/httpbasicauthbyuserlist | grep -qci -e 'errorCode' && cat conf/users.json | etcdctl set '/commissaire/config/httpbasicauthbyuserlist'

EXPOSE 2379

CMD ["python", "src/commissaire/script.py", "http://$ETCD:2379"]
