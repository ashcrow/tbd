Name:           commissaire
Version:        0.0.1rc1
Release:        1%{?dist}
Summary:        Simple cluster host management
License:        AGPLv3+
URL:            http://github.com/projectatomic/commissaire
Source0:        %{name}-%{version}.tar.gz

# XXX: Waiting on python2-python-etcd to pass review
#      https://bugzilla.redhat.com/show_bug.cgi?id=1310796
BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools
BuildRequires:  python2-falcon
BuildRequires:  python2-python-etcd
BuildRequires:  python-gevent
BuildRequires:  python-jinja2
BuildRequires:  python-requests
BuildRequires:  py-bcrypt
BuildRequires:  ansible

# For tests
BuildRequires:  python-coverage
BuildRequires:  python-pep8

%description
Commissaire allows administrators of a Kubernetes, Atomic Enterprise or
OpenShift installation to perform administrative tasks without the need
to write custom scripts or manually intervene on systems.

Example tasks include:
  * rolling reboot of cluster hosts
  * upgrade software on cluster hosts
  * check the status of cluster hosts
  * scan for known vulnerabilities
  * add a new host to a cluster for container orchestration


%prep
%autosetup


%build
%py2_build


%install
%py2_install


%check
%{__python2} setup.py test


%files
%license COPYING
%doc README.md
%{_bindir}/commctl
%{_bindir}/commissaire
%{_bindir}/commissaire-hashpass
%{python2_sitelib}/*


%changelog
* Mon Feb 22 2016 Matthew Barnes <mbarnes@redhat.com> - 0.0.1rc1-1
- Initial packaging.
