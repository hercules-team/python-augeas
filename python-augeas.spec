# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%if ! 0%{?fedora}%{?rhel} || 0%{?fedora} >= 9 || 0%{?rhel} >= 6
bcond_without egg
%endif

Name:		python-augeas
Version:	0.4.1
Release:	1%{?dist}
Summary:	Python bindings to augeas
Group:		Development/Languages
License:	LGPLv2+
URL:		http://augeas.net/
Source0:	http://augeas.net/download/python/%{name}-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:	augeas-libs 
BuildArch:	noarch

BuildRequires:	python-setuptools python-devel

%description
python-augeas is a set of Python bindings around augeas.

%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build_ext -i
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS README.txt
%{python_sitelib}/augeas.py*
%if %{with egg}
%{python_sitelib}/*augeas*.egg-info
%endif

%changelog
* Fri Oct 28 2011 Nils Philippsen <nils@redhat.com> 0.4.1-1
- version 0.4.1
- include egg only on F-9, RHEL-6 and later

* Tue Sep 09 2008 Harald Hoyer <harald@redhat.com> 0.3.0-1
- version 0.3.0

* Thu Jul 03 2008 Harald Hoyer <harald@redhat.com>
- added python-devel to buildrequires

* Thu Jul 03 2008 Harald Hoyer <harald@redhat.com> 0.2.1-1
- version 0.2.1

* Wed Jun 11 2008 Harald Hoyer <harald@redhat.com> 0.2.0-1
- switched to noarch, dlopen/ python bindings

* Mon May 05 2008 Harald Hoyer <harald@redhat.com> 0.1.0-4
- version to import in CVS (rhbz#444945)

* Mon May 05 2008 Harald Hoyer <harald@redhat.com> 0.1.0-3
- set mode of _augeas.so to 0755

* Mon May 05 2008 Harald Hoyer <harald@redhat.com> 0.1.0-2
- wildcard to catch egg-info in case it is build

* Fri May 02 2008 Harald Hoyer <harald@redhat.com> 0.1.0-1
- new version

* Wed Apr 16 2008 Harald Hoyer <harald@redhat.com> - 0.0.8-1
- initial version
