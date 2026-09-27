Name:           ujwalos-branding
Version:        0.3
Release:        1%{?dist}
Summary:        UjwalOS desktop, login, and boot appearance
License:        LicenseRef-UjwalOS-Internal
BuildArch:      noarch
Requires:       plasma-workspace
Requires:       plasma-login-manager
Requires:       plymouth
Requires:       plymouth-plugin-two-step

%description
UjwalOS wallpaper and first-run Plasma defaults, Plasma Login Manager
background, and a Plymouth theme. No user home files are installed.

%prep

%build

%install
mkdir -p %{buildroot}
cp -a %{_sourcedir}/root/. %{buildroot}/

%files
%config(noreplace) /etc/xdg/kdeglobals
%config(noreplace) /etc/xdg/kicker-extra-favoritesrc
%config(noreplace) /usr/lib/plasmalogin/plasmalogin.conf.d/50-ujwalos-wallpaper.conf
/usr/share/wallpapers/UjwalOS/
/usr/share/plasma/look-and-feel/org.ujwalos.desktop/
/usr/share/plymouth/themes/ujwalos/
