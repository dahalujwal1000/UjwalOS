Name:           ujwalos-gaming-setup
Version:        0.1
Release:        1%{?dist}
Summary:        Optional gaming setup for UjwalOS
License:        LicenseRef-UjwalOS-Internal
BuildArch:      noarch
Requires:       bash
Requires:       dnf5
Requires:       konsole
Requires:       polkit
Requires:       rpm

%description
User-invoked setup for Fedora gaming tools and optional Steam from a
repository already enabled by the user. No gaming software is bundled.

%prep

%build

%install
mkdir -p %{buildroot}
cp -a %{_sourcedir}/root/. %{buildroot}/

%files
/usr/bin/ujwalos-gaming-setup
/usr/share/applications/ujwalos-gaming-setup.desktop
