# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           python-augeas
Version:        0.0.8
Release:        1%{?dist}
Summary:        Python bindings to augeas

Group:          Development/Languages
License:        LGPLv2+
URL:            http://augeas.net/
Source0:        http://augeas.net/download/python/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel swig augeas-devel

%description
python-augeas is a set of Python bindings around augeas.

%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build_ext
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS README.txt
# For arch-specific packages: sitearch
%{python_sitearch}/augeas.py*
%{python_sitearch}/_augeas.so
%{python_sitearch}/*.egg-info


%changelog
* Wed Apr 16 2008 Harald Hoyer <harald@redhat.com> - 0.0.8-1
- initial version
