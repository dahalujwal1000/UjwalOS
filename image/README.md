# Fedora 44 KDE derivative

The vendored archive is the complete upstream source at
`dfc49a5a10f69941179fdadd96aa6a5984f7c677`, the `f44` branch tip inspected on
2026-09-26, not an assertion that this is Fedora's original release compose.
Source: https://forge.fedoraproject.org/releng/kiwi-descriptions.git

`inputs.json` pins its SHA-256; `upstream/COPYING` preserves GPL-3.0-or-later
terms. The archive includes upstream authorship, configuration and helper scripts.
To reproduce that archive from a checkout at the recorded commit:

```sh
git archive --format=tar.gz --output=fedora-kiwi-f44.tar.gz dfc49a5a10f69941179fdadd96aa6a5984f7c677
sha256sum fedora-kiwi-f44.tar.gz
```

`scripts/build/prepare-description.py` checks the checksum and extracts into a
new directory. It changes the image name to `UjwalOS-0.1` and includes
`compose/packages.xml`, which explicitly selects `kde-connect`. The Stage 1
ISO retained the stock wallpaper. Stage 2 adds an original wallpaper and
desktop defaults in the versioned `ujwalos-branding` RPM. The repository alias
symlink is materialized with identical content for mapped
9p sharing. A `boxroot` overlay selects Fedora's `isomd5sum` media-check backend
inside the disposable builder; it is not an installed-image change. The x86-64
live filesystem disables EROFS fragments after a builder failure, retaining
LZMA level 6 compression and 1 MiB clusters. The
generated `config.sh` unsets a KIWI build-path `blsdir` in GRUB's environment
for live images; without this, Anaconda copies a path that hides installed
kernel entries. It also installs the branding RPM into the disposable image
root and selects its Plymouth theme. The RPM owns initial Plasma defaults,
wallpaper and login appearance without changing installed release identity,
installer or GRUB templates. Version 44 and release-version 44 remain
unchanged. Compose CLI overrides only ISO volume/application ID and publisher.

Exact image selection: file `Fedora.kiwi`, type `iso`, profile
`KDE-Desktop-Live`. The inherited profiles are `KDE-Desktop`, `DesktopCommon`,
`BaseCommon`, `HardwareCommon`, `LiveInstall`, and `BootCoreLive`.
The x86-64 live root uses EROFS in dmsquash mode, UEFI/GRUB, and media checking.
The stock installer includes `anaconda-live`, `anaconda-install-env-deps`, the
`anaconda-tools` collection and `livesys-scripts`.

DNF5 resolves these stock repositories from `repositories/core.xml`:

- `fedora`: https://mirrors.fedoraproject.org/metalink?repo=fedora-44&arch=x86_64
- `updates`: https://mirrors.fedoraproject.org/metalink?repo=updates-released-f44&arch=x86_64

The signing key is supplied by `distribution-gpg-keys` at
`/usr/share/distribution-gpg-keys/fedora/RPM-GPG-KEY-fedora-44-primary`.
No testing, Rawhide or third-party repository is selected.

This makes the **description derivative reproducible**, not the entire image:
Fedora updates and group metadata can change. The builder is hash-pinned in
`builder.json`; a fresh download fails closed if upstream has replaced it. Keep
the verified local cache for replay until an artifact archive is established. Each
attempt saves the description hash inventory, metalinks, tool versions and logs;
successful builds also record builder checksums and KIWI's result inventory.
Release publication still needs an archived RPM/metadata snapshot, durable
builder artifact storage and repeat-build comparison. Do not confuse a source pin with a package lock.

Package verification: [kde-connect for Fedora 44](https://packages.fedoraproject.org/pkgs/kde-connect/kde-connect/),
GPL-2.0-or-later, checked 2026-09-26. Pairing remains a user action; this does not
implement or certify a UjwalOS phone panel.
