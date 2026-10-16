# UjwalOS

A planned Fedora-based x86-64 gaming desktop with KDE Plasma, a familiar
desktop layout, and opt-in Android continuity through KDE Connect.

## Current status

Newest built engineering ISO (apps 0.1-4, including the 2026-10-15 security
source fixes):
`out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso`
(3,834,904,576 bytes; SHA-256
`a1efa6cc0dfb5beb94e64fab11c658a20463980cbc9f8875295a3a6c3cf38775`).
Compose, checksum, ISO9660 and UEFI catalog/media checks passed. On 2026-10-16
this exact ISO passed a UEFI live Plasma boot, both custom-app smoke tests, a
fresh installation to a 40 GiB file-backed disk, ISO-detached boot, first-run
setup, login, reboot and second login. Triple boot with Windows and Fedora,
shared EFI-partition coexistence, hardware and Secure Boot are not validated.
See [status](docs/status.md) for separate image and test evidence.

Documentation reconciled 2026-10-16. The latest monitoring milestone passed
**91 tests: 75 configuration, 14 Qt UI and 2 isolated D-Bus tests**. These are
not hardware or security certification. The [security review](docs/security-review-2026-09-30.md)
is complete within its stated scope. Source fixes for its three findings—compose
signature enforcement, builder SSH exposure and profile-file blocking—now pass
regression checks; the newest ISO above contains these source changes and passed
the VM sequence described above. See the
[acceptance summary](docs/status.md#current-acceptance-summary) for completed work,
pending implementation and remaining testing.

The subsequent guest checker passed all eight baseline checks inside a restored
file-backed VM. New source adds bounded command capture, explicit VM accelerator
selection and opt-in CPU/memory monitoring; see the latest status entry for
test results and package-versus-ISO scope.

| Stage | Description | Status |
|-------|-------------|--------|
| **0 — Specification** | Architecture, image-strategy decision, security model, compatibility review, build plan | ✅ Complete |
| **1 — Bootable v0.1** | Fedora KDE live ISO with minimal UjwalOS branding | ✅ Complete |
| **2 — Desktop identity** | Taskbar layout, theme, wallpaper, login, boot splash | ✅ Complete |
| 3 — Gaming foundation | Optional gaming setup; game and hardware validation | Implementation complete; testing pending |
| 4 — Gaming Center | Qt/QML app, profiles, per-game settings | In progress: profiles and opt-in system metrics |
| 5 — Android continuity | KDE Connect phone panel | Basic phone link passed (owner-tested); remaining features/gates open |
| 6 — Android apps | Optional Waydroid experiment | ⬜ Not started |
| 7 — Recovery & release | Updates, recovery, accessibility, hardware testing | In progress: artifact verifier and recovery protocol |
| 8 — Public v1.0 | Final release | ⬜ Not started |

### Stage 1 detail

| Gate | Evidence |
|------|----------|
| KIWI description validated | ✅ PASS — pinned Fedora 44 derivative passes schema/profile validation |
| Package resolution & download | ✅ PASS — all RPMs resolved and installed inside disposable builder |
| SELinux file contexts applied | ✅ PASS |
| ISO filesystem (mkfs.erofs) | PASS: fragments disabled; LZMA compression retained |
| ISO built | PASS: newest corrected image in `out/build-6KtHtk1p/result/` |
| Live boot in VM | PASS (2026-10-16): UEFI GRUB and KDE Plasma reached |
| Installer and installation | PASS (2026-10-16): fresh 40 GiB file-backed disk |
| Installed system boots | PASS (2026-10-16): ISO detached, first-run setup, login, restart and second login |

The EROFS compose failure is resolved. The first VM installation exposed a
build-only GRUB BLS path that prevented installed boot; corrected images clear
that path. The newest security-remediated ISO passed a fresh installation and
disk-only boot test on 2026-10-16. See
[docs/status.md](docs/status.md) for checksums, logs and separate test gates.
This is an internal engineering image, not a public release. Hardware, Secure
Boot and gaming acceptance remain open; phone-test scope is recorded below.

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
The latest combined automated results are recorded above; earlier Qt smoke tests
also passed at 200% scale. These do not establish full accessibility acceptance.
Opt-in aggregate CPU/memory monitoring is implemented in newer source;
authorized system integration and crash/reboot restoration are not implemented.
The earlier editor is packaged in `ujwalos-apps` 0.1-4
and included in the newest built ISO above; it launched successfully in that
ISO's live session on 2026-10-16.
Stage 3 hardware/game gates stay open.

### Stage 5 detail

The [phone panel](docs/phone-panel.md) has a Qt/QML view for device
pairing/reachability status and battery snapshots through KDE Connect's session
bus. Refresh is explicit and does not start the service. Automated tests cover
simulated states and failures. The owner confirmed basic phone linking works on
2026-09-30; that test is marked passed, not universal phone compatibility. Source
now includes confirmed unpair requests, fresh state checks, public verification-code
display and an explicit KDE Connect launcher. Pairing, acceptance and cancellation
use KDE Connect's UI; direct pairing calls were removed after upstream review
identified a race with incoming requests. Notifications, clipboard, transfers and
broader real-device acceptance remain pending. The updated RPM is `ujwalos-apps`
0.1-4 in the newest built ISO; the panel launched successfully in that ISO's
live session, and the ISO completed installation and disk-only boot.

### Stage 7 detail

Stage 7 has started with [requirements and recovery test gates](docs/recovery-and-quality.md).
An offline engineering-artifact manifest tool records and verifies SHA-256 and
sizes without signing, publishing or claiming release readiness. Update/recovery,
accessibility, dual-boot and repeated hardware acceptance remain pending.
This work does not close the unfinished Stage 3-6 gates; recovery tooling/docs
remain repository tools.

A read-only installed-guest baseline checker is available at
`scripts/test/check-installed-system.py --guest-check`. It reports scoped
SELinux, firewall, package-integrity, local live-account and listener checks as
JSON. See the [guest-check protocol](docs/recovery-and-quality.md#installed-guest-baseline-checker)
for execution context, exit codes and limits. This tool is not included in the
previously built ISO; a copy was supplied on read-only auxiliary media and
passed inside the restored installed guest. A small offline codec update and
pre-transaction network-failure test passed; kernel/rescue and interrupted-update
recovery acceptance remain open.

## Project documents

- [Full product specification and original master prompt](plan.md)
- [Architecture](docs/architecture.md) and [image strategy](docs/decisions/0001-image-strategy.md)
- [Build preparation and test gates](docs/build-and-test.md)
- [Security model](docs/security-model.md)
- [Security review and remediation status](docs/security-review-2026-09-30.md)
- [Compatibility and dependency review](docs/compatibility.md)
- [Roadmap](docs/roadmap.md) and [release process](docs/release-process.md)
- [Recovery and release-quality protocol](docs/recovery-and-quality.md)
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
