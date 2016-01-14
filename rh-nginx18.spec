%global scl_name_prefix  rh-
%global scl_name_base    nginx
%global scl_name_version 18
%global scl              %{scl_name_prefix}%{scl_name_base}%{scl_name_version}
%{!?nfsmountable: %global nfsmountable 1}
%scl_package %scl

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary:       Package that installs %scl
Name:          %scl_name
Version:       2.1
Release:       4%{?dist}
License:       GPLv2+
Group: Applications/File
Source0: README
Source1: LICENSE
Source2: README.7

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
# Temporary work-around
BuildRequires: iso-codes

Requires: %{scl_prefix}nginx

%description
This is the main package for %scl Software Collection.

%package runtime
Summary:   Package that handles %scl Software Collection.
Requires:  scl-utils
Requires(post): policycoreutils-python libselinux-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary:   Package shipping basic build configuration
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -c -T

# copy the license file so %%files section sees it
cp %{SOURCE0} .
cp %{SOURCE1} .
cp %{SOURCE2} .

sed -i 's|%%{scl_name}|%{scl_name}|g' README.7
sed -i 's|%%{_scl_root}|%{_scl_root}|g' README.7
sed -i 's|%%{version}|%{version}|g' README.7

# Not required for now
#export LIBRARY_PATH=%{_libdir}\${LIBRARY_PATH:+:\${LIBRARY_PATH}}
#export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_name_base}         %{scl}
%%scl_prefix_%{scl_name_base}  %{scl_prefix}
EOF

%build

%install
mkdir -p %{buildroot}%{_scl_scripts}/root
install -m 644 enable  %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

mkdir -p %{buildroot}%{_localstatedir}/run/

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 README.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%scl_install

# create directory for SCL register scripts
mkdir -p %{buildroot}%{?_scl_scripts}/register.content
mkdir -p %{buildroot}%{?_scl_scripts}/register.d
cat <<EOF | tee %{buildroot}%{?_scl_scripts}/register
#!/bin/sh
ls %{?_scl_scripts}/register.d/* | while read file ; do
    [ -x \$f ] && source \$(readlink -f \$file)
done
EOF
# and deregister as well
mkdir -p %{buildroot}%{?_scl_scripts}/deregister.d
cat <<EOF | tee %{buildroot}%{?_scl_scripts}/deregister
#!/bin/sh
ls %{?_scl_scripts}/deregister.d/* | while read file ; do
    [ -x \$f ] && source \$(readlink -f \$file)
done
EOF

%post runtime
# Simple copy of context from system root to DSC root.
# In case new version needs some additional rules or context definition,
# it needs to be solved.
# Unfortunately, semanage does not have -e option in RHEL-5, so we have to
# have its own policy for collection
semanage fcontext -a -e / %{_scl_root} >/dev/null 2>&1 || :
restorecon -R %{_scl_root} >/dev/null 2>&1 || :
selinuxenabled && load_policy || :

%files

%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%dir %{_mandir}/man7
%dir %{_mandir}/man8
%{_mandir}/man7/%{scl_name}.*

%dir %{_localstatedir}/run

%attr(0755,root,root) %{?_scl_scripts}/register
%attr(0755,root,root) %{?_scl_scripts}/deregister
%{?_scl_scripts}/register.content
%dir %{?_scl_scripts}/register.d
%dir %{?_scl_scripts}/deregister.d

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Tue Aug 11 2015 Jan Kaluza <jkaluza@redhat.com> - 2.1-4
- expand variables in rh-nginx18 manual page (#1249927)

* Tue Jul 14 2015 Jan Kaluza <jkaluza@redhat.com> - 2.1-3
- Escape apostrophs in rh-nginx18(7) manual page

* Wed Jul 08 2015 Jan Kaluza <jkaluza@redhat.com> - 2.1-2
- rebuild against new scl-utils

* Wed Jul 08 2015 Jan Kaluza <jkaluza@redhat.com> - 2.1-1
- initial packaging
