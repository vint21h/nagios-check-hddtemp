# nagios-check-hddtemp
# nagios-plugin-check-hddtemp.spec

%global _unpackaged_files_terminate_build 0
%global original_name nagios-check-hddtemp
%global debug_package %{nil}

Summary: Check HDD temperature Nagios plugin
Name: nagios-plugins-check-hddtemp
Version: 1.4.10
Release: 1%{?dist}
Source0: %{original_name}-%{version}.tar.gz
License: GPLv3 or later
Group: Applications/System
BuildRequires: python-setuptools
Requires: python >= 2.7
Requires: nagios-plugins
Packager: Alexei Andrushievich <vint21h@vint21h.pp.ua>
Url: https://github.com/vint21h/nagios-check-hddtemp/

%description
Check HDD temperature Nagios plugin.

%prep
%setup -n %{original_name}-%{version}

%install
mkdir -p %{buildroot}%{_libdir}/nagios/plugins
install -p -m 755 check_hddtemp.py %{buildroot}%{_libdir}/nagios/plugins/check_hddtemp

%files
%defattr(-,root,root)
%doc README.rst COPYING AUTHORS
%{_libdir}/nagios/plugins/check_hddtemp

%changelog
* Wed Mar 10 2021 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.10-1
- Updated to new version

* Sun Mar 7 2021 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.9-1
- Updated to new version

* Sun Feb 14 2021 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.8-1
- Updated to new version

* Thu Feb 11 2021 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.7-1
- Updated to new version

* Thu Feb 11 2021 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.6-1
- Updated to new version

* Mon Jan 18 2021 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.5-1
- Updated to new version

* Tue Oct 20 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.4-1
- Updated to new version

* Sat Oct 10 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.3-1
- Updated to new version

* Sat Oct 10 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.2-1
- Updated to new version

* Sat Oct 10 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.1-1
- Updated to new version

* Wed Oct 7 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.4.0-1
- Updated to new version

* Mon Sep 28 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.3.1-1
- Updated to new version

* Sun Sep 20 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.3.0-1
- Updated to new version

* Tue Jun 9 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.2.3-1
- Updated to new version

* Wed Jun 3 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.2.2-1
- Updated to new version

* Sun May 10 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.2.1-1
- Updated to new version

* Sun May 10 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.2.0-1
- Updated to new version

* Sat Apr 25 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.11-1
- Updated to new version

* Sat Apr 25 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.10-1
- Updated to new version

* Fri Apr 17 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.9-1
- Updated to new version

* Fri Apr 17 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.8-1
- Updated to new version

* Fri Apr 17 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.7-1
- Updated to new version

* Fri Apr 17 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.6-1
- Updated to new version

* Fri Apr 17 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.5-1
- Updated to new version

* Thu Apr 16 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.4-1
- Updated to new version

* Thu Apr 16 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.3-1
- Updated to new version

* Mon Apr 13 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.2-1
- Updated to new version

* Sat Apr 11 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.1-1
- Updated to new version

* Sat Apr 11 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.0-1
- Updated to new version

* Thu Apr 9 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.0.1-1
- Updated to new version

* Thu Apr 9 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.0.0-1
- Updated to new version

* Tue Apr 7 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.9.0-1
- Updated to new version

* Fri Jul 29 2016 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.8.2-1
- Updated to new version

* Thu Dec 3 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.8.1-1
- Updated to new version

* Thu Dec 3 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.8.0-1
- Updated to new version

* Wed Sep 9 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.7.0-1
- Updated to new version

* Mon Jun 1 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.6.0-1
- Updated to new version

* Fri Feb 13 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.5.7-1
- Init
