# UjwalOS

A planned Fedora-based x86-64 gaming desktop with KDE Plasma, a familiar
desktop layout, and opt-in Android continuity through KDE Connect.

## Current status

| Stage | Description | Status |
|-------|-------------|--------|
| **0 — Specification** | Architecture, image-strategy decision, security model, compatibility review, build plan | ✅ Complete |
| **1 — Bootable v0.1** | Fedora KDE live ISO with minimal UjwalOS branding | ✅ Complete |
| **2 — Desktop identity** | Taskbar layout, theme, wallpaper, login, boot splash | ✅ Complete |
| 3 — Gaming foundation | Optional gaming setup; game and hardware validation | Implementation complete; testing pending |
| 4 — Gaming Center | Qt/QML app, profiles, per-game settings | In progress: profile editor |
| 5 — Android continuity | KDE Connect phone panel | ⬜ Not started |
| 6 — Android apps | Optional Waydroid experiment | ⬜ Not started |
| 7 — Recovery & release | Updates, recovery, accessibility, hardware testing | ⬜ Not started |
| 8 — Public v1.0 | Final release | ⬜ Not started |

### Stage 1 detail

| Gate | Evidence |
|------|----------|
| KIWI description validated | ✅ PASS — pinned Fedora 44 derivative passes schema/profile validation |
| Package resolution & download | ✅ PASS — all RPMs resolved and installed inside disposable builder |
| SELinux file contexts applied | ✅ PASS |
| ISO filesystem (mkfs.erofs) | PASS: fragments disabled; LZMA compression retained |
| ISO built | PASS: corrected image in `out/build-0QH6om9N/result/` |
| Live boot in VM | PASS: KDE Plasma reached |
| Installer and installation | PASS: fresh 40 GiB file-backed disk |
| Installed system boots | PASS: ISO detached, first-run setup, login, restart and second login |

The EROFS compose failure is resolved. The first VM installation exposed a
build-only GRUB BLS path that prevented installed boot; the corrected ISO clears
that path and passed a fresh installation and disk-only boot test. See
[docs/status.md](docs/status.md) for checksums, logs and separate test gates.
This is an internal engineering image, not a public release. Hardware, Secure
Boot, gaming and phone integration remain untested.

### Stage 2 detail

Stage 2 is complete. The `ujwalos-branding` 0.4-1 RPM packages an original
wallpaper, first-run Plasma global theme and panel template, Plasma Login
Manager background, and a Plymouth theme with original animation and prompt
assets. A new account received the intended wallpaper and panel, while an
existing account retained its selected wallpaper and Plasma configuration
through a package update and reboot. The corrected Plymouth theme rendered in
an installed disk-only VM boot and in the final ISO's live boot.

The accepted Stage 2 image is
`out/build-4MOSl8sm/result/UjwalOS-0.1.x86_64-44-0.iso` (3,791,638,528 bytes,
SHA-256 `261b3a9f24f597ba28391d6684d93cb7fc4728fffa4343c3ce75ae5d3b5f0703`).
It passed the compose result, checksum, ISO9660, UEFI catalog and live Plasma
boot gates. This remains an internal engineering image: hardware, Secure Boot,
gaming, phone integration and public-release licensing are not Stage 2 claims.
See [current evidence](docs/status.md).

### Stage 3 detail

The optional Gaming Setup RPM and KDE launcher are included in the Stage 3
engineering ISO at `out/build-dXo1VHow/result/UjwalOS-0.1.x86_64-44-0.iso`
(SHA-256 `b4110546036fdb87813dc35de25d447cc5e2032821278fa0ed28a1795a71855c`).
The ISO passed media checks, live boot, a fresh 40 GiB VM installation, and
disk-only boot through first-run setup and login. The gaming RPM passed file
verification in the installed guest, and cancelling its PolicyKit request
returned to the menu without installing optional tools. The live-session
launcher also installed Fedora gaming tools successfully. Steam,
Proton and proprietary drivers are not bundled. Stage 3's optional gaming-setup
implementation is **complete; acceptance testing remains pending**. This does
not claim an NVIDIA driver installer or universal game compatibility.
The stock Fedora KDE game matrix, Steam/Proton, real GPU and controller tests
remain open, so the full Stage 3 acceptance gate has not passed. See the [test protocol](docs/gaming-setup.md) and
[gate evidence](docs/status.md).

### Stage 4 detail

Stage 4 has started with [requirements and acceptance gates](docs/gaming-center.md)
and a Qt/QML per-game profile editor: validated settings, private atomic saves,
fixed launch-option previews, local reset and read-only tool availability.
All 14 repository tests and five Qt tests pass, including Qt tests at 200% scale.
Runtime monitoring, authorized system integration and crash/reboot restoration
are not implemented yet. No Stage 4 RPM or ISO has been built;
the existing ISO remains the Stage 3 image. Stage 3 hardware/game gates stay open.

## Project documents

- [Full product specification and original master prompt](plan.md)
- [Architecture](docs/architecture.md) and [image strategy](docs/decisions/0001-image-strategy.md)
- [Build preparation and test gates](docs/build-and-test.md)
- [Security model](docs/security-model.md)
- [Compatibility and dependency review](docs/compatibility.md)
- [Roadmap](docs/roadmap.md) and [release process](docs/release-process.md)
- [Current status / release notes](docs/status.md)
- [Licensing policy](LICENSES/README.md)

## Safe local checks

From the repository root:

```sh
scripts/build/build-iso.sh --validate
python3 -m unittest discover -s tests/config -v
git diff --check
```

These commands validate the pinned description and repository safeguards without
composing an image. To build and boot-test:

```sh
scripts/build/build-iso.sh
scripts/test/test-iso.sh out/build-XXXXXXXX/result/ACTUAL-NAME.iso
```

Use the actual ISO filename printed by the build. Builds run inside a disposable
QEMU VM; tests use a private virtual disk. Both support software emulation when
KVM is unavailable. See [exact prerequisites and commands](docs/build-and-test.md).
