Name:           ujwalos-apps
Version:        0.1
Release:        2%{?dist}
Summary:        UjwalOS development Gaming Center and Phone Panel
License:        LicenseRef-UjwalOS-Internal
BuildArch:      noarch
Requires:       python3
Requires:       python3-pyside6
Requires:       qt6-qtdeclarative
Requires:       kde-connect

%description
Unprivileged Qt/QML gaming profile editor and KDE Connect status panel with
confirmed pairing and unpair requests. These engineering previews do not apply
performance settings. No autostart service or privileged helper is installed.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/ujwalos/gaming-center
mkdir -p %{buildroot}/usr/share/ujwalos/phone-panel
mkdir -p %{buildroot}/usr/share/applications
install -m 0644 %{_sourcedir}/apps/gaming-center/{main.py,profiles.py,Main.qml} %{buildroot}/usr/share/ujwalos/gaming-center/
install -m 0644 %{_sourcedir}/apps/phone-panel/{phone_panel.py,backend.py,Main.qml} %{buildroot}/usr/share/ujwalos/phone-panel/
install -m 0644 %{_sourcedir}/packaging/desktop/*.desktop %{buildroot}/usr/share/applications/

%files
/usr/share/ujwalos
/usr/share/applications/ujwalos-gaming-center.desktop
/usr/share/applications/ujwalos-phone-panel.desktop
