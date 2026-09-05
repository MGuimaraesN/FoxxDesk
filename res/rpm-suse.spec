Name:       foxxdesk
Version:    1.1.9
Release:    0
Summary:    RPM package
License:    GPL-3.0
Requires:   gtk3 libxcb1 libXfixes3 alsa-utils libXtst6 libva2 pam gstreamer-plugins-base gstreamer-plugin-pipewire
Recommends: libayatana-appindicator3-1 xdotool

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/

%description
The best open-source remote desktop client software, written in Rust.

%prep
# we have no source, so nothing here

%build
# we have no source, so nothing here

%global __python %{__python3}

%install
mkdir -p %{buildroot}/usr/bin/
mkdir -p %{buildroot}/usr/share/foxxdesk/
mkdir -p %{buildroot}/usr/share/foxxdesk/files/
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps/
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps/
install -m 755 $HBB/target/release/foxxdesk %{buildroot}/usr/bin/foxxdesk
install $HBB/libsciter-gtk.so %{buildroot}/usr/share/foxxdesk/libsciter-gtk.so
install $HBB/res/foxxdesk.service %{buildroot}/usr/share/foxxdesk/files/
install $HBB/res/128x128@2x.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/foxxdesk.png
install $HBB/res/scalable.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/foxxdesk.svg
install $HBB/res/foxxdesk.desktop %{buildroot}/usr/share/foxxdesk/files/
install $HBB/res/foxxdesk-link.desktop %{buildroot}/usr/share/foxxdesk/files/

%files
/usr/bin/foxxdesk
/usr/share/foxxdesk/libsciter-gtk.so
/usr/share/foxxdesk/files/foxxdesk.service
/usr/share/icons/hicolor/256x256/apps/foxxdesk.png
/usr/share/icons/hicolor/scalable/apps/foxxdesk.svg
/usr/share/foxxdesk/files/foxxdesk.desktop
/usr/share/foxxdesk/files/foxxdesk-link.desktop

%changelog
# let's skip this for now

%pre
# can do something for centos7
case "$1" in
  1)
    # for install
  ;;
  2)
    # for upgrade
    systemctl stop foxxdesk || true
  ;;
esac

%post
cp /usr/share/foxxdesk/files/foxxdesk.service /etc/systemd/system/foxxdesk.service
cp /usr/share/foxxdesk/files/foxxdesk.desktop /usr/share/applications/
cp /usr/share/foxxdesk/files/foxxdesk-link.desktop /usr/share/applications/
systemctl daemon-reload
systemctl enable foxxdesk
systemctl start foxxdesk
update-desktop-database

%preun
case "$1" in
  0)
    # for uninstall
    systemctl stop foxxdesk || true
    systemctl disable foxxdesk || true
    rm /etc/systemd/system/foxxdesk.service || true
  ;;
  1)
    # for upgrade
  ;;
esac

%postun
case "$1" in
  0)
    # for uninstall
    rm /usr/share/applications/foxxdesk.desktop || true
    rm /usr/share/applications/foxxdesk-link.desktop || true
    update-desktop-database
  ;;
  1)
    # for upgrade
  ;;
esac
