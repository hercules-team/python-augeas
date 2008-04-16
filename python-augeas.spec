# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:		python-augeas
Version:	1.0
Release:	1%{?dist}
Summary:	Python bindings to augeas

Group:		Development/Languages
License:	LGPLv2+
URL:            http://augeas.net/
Source0:	python-augeas-%{version}.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	python-devel swig augeas-devel

%description
python-augeas is a set of Python bindings around augeas.

%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
make
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
# For arch-specific packages: sitearch
%{python_sitearch}/*


%changelog
* Wed Apr 16 2008 Harald Hoyer <harald@redhat.com> - 1.0
- initial version
