# UjwalOS

A planned Fedora-based x86-64 gaming desktop with KDE Plasma, a familiar
desktop layout, and opt-in Android continuity through KDE Connect.

## Current status

| Stage | Description | Status |
|-------|-------------|--------|
| **0 — Specification** | Architecture, image-strategy decision, security model, compatibility review, build plan | ✅ Complete |
| **1 — Bootable v0.1** | Fedora KDE live ISO with minimal UjwalOS branding | ✅ Complete |
| 2 — Desktop identity | Taskbar layout, theme, wallpaper, login, boot splash | ⬜ Not started |
| 3 — Gaming foundation | Steam/Proton validation, driver flow, gaming tools | ⬜ Not started |
| 4 — Gaming Center | Qt/QML app, profiles, per-game settings | ⬜ Not started |
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
