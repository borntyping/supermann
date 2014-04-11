%define name %(python setup.py --name)
%define version %(python setup.py --version)

Name: %{name}
Version: %{version}
Release: 1

Group: System Environment/Daemons
Url: http://borntyping.github.io/supermann/
Summary: A process monitor that connects Supervisor and Riemann
Vendor: Sam Clements <sam.clements@datasift.com>
License: MIT

Source0: %{name}-%{version}.tar.gz

Requires: python >= 2.6
Requires: python-argparse >= 1.1
Requires: python-blinker >= 1.1
Requires: python-psutil >= 0.6.1
Requires: python-riemann-client >= 3.1.0
Requires: supervisor >= 3.0
BuildRequires: python-setuptools

BuildArch: noarch

%description
Supermann is a Supervisord event listener that monitors the processes running
under Supervisor and sends system and process metrics to Riemann.

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --no-compile --skip-build --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README.rst LICENSE
%{_bindir}/supermann
%{python_sitelib}/*
