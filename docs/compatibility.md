# Compatibility and dependency review

Initial upstream selection checked 2026-09-26; evidence reconciled 2026-10-15.
The newest ISO passed compose and media checks, but has not been live-booted or
installed. The older 2026-09-30 ISO passed live boot. No supported-hardware or
gaming certification is claimed. This update records existing results, not a
fresh package-availability or full CVE review.

## Dependency status

| Component | Initial disposition | Evidence / remaining work |
| --- | --- | --- |
| Fedora KDE 44 x86-64 | Selected base | Official download page verified; description and builder pinned; RPM repositories moving |
| KIWI / kiwi-cli | Selected image builder | Fedora 44 package availability verified; KIWI 11.0.2 installed; boxed builder available |
| Kernel, firmware, Mesa, PipeWire, Plasma | Inherit base | Exact package set, versions, licenses follow pinned KDE definition |
| KDE Connect | Packaged phone integration | Older live-booted ISO: 26.08.1-1.fc44; live panel/native-launch smoke passed; owner basic linking PASS; broader real-device tests pending |
| Qt 6 / KDE frameworks | Qt/QML previews implemented | PySide6 6.11.2-1.fc44 in newest composed ISO; apps 0.1-4; 13 automated UI tests passed; latest-image boot and full installed/accessibility acceptance pending |
| Steam / Proton | Optional Stage 3 setup | Source and no-bundling review recorded in gaming-setup.md; Steam and real game testing pending |
| GameMode, MangoHud, Gamescope | Optional Stage 3 tools | Fedora 44 packages verified 2026-09-28; install completed in KVM live guest, but GameMode governor self-test failed because guest governor files were absent; real game tests remain pending |
| Heroic | Deferred optional evaluation | Package source, API and distribution review pending |
| NVIDIA | Optional later setup | Hybrid graphics, signed modules and Secure Boot enrollment tests pending |
| Waydroid | Separate feature-gated experiment | Graphics, security, image rights and app compatibility unverified |

Sources: [Fedora KDE](https://www.fedoraproject.org/kde/download/) and
[Fedora kiwi-cli](https://packages.fedoraproject.org/pkgs/kiwi/kiwi-cli/index.html).
Availability does not imply installation, complete license review, or testing.

## Hardware matrix

NT = not tested. Targets below are planned coverage, not known-good systems.

| Hardware target | Boot | Wi-Fi | Audio | Suspend/resume | External display | GPU acceleration | Gaming | Known issues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x86-64 UEFI QEMU VM | PASS | N/A | NT | NT | N/A | Software rendering only | NT | Stage 3 live boot: `out/vm-ck8RbgAm`, KVM CPU, Virtio VGA; see status.md for ISO checksum |
| VirtualBox owner VM | Owner-observed installed boot | N/A | NT | NT | NT | llvmpipe observed | Informal Minecraft run only | About 10 FPS reported; display fit/scrollbars unresolved; exact tested image not independently established |
| Intel integrated graphics | NT | NT | NT | NT | NT | NT | NT | No test machine identified |
| AMD graphics | NT | NT | NT | NT | NT | NT | NT | No test machine identified |
| Intel/NVIDIA RTX 3050 hybrid laptop | NT | NT | NT | NT | NT | NT | NT | Suggested target; exact model and Secure Boot state unknown |

Record model, firmware, image checksum, kernel/driver versions and evidence for
each actual test. VM rendering does not validate physical GPU drivers or gaming.
Measure games against stock Fedora KDE on the same hardware with matching
versions, settings, power conditions and repeated runs. Record anti-cheat and
launcher limitations; do not claim every Windows game or Android APK works.

The latest recorded QEMU live boot passed in `out/vm-XD4lUSCr` for the older
`out/build-9BaEqZ1c/result/` image. The 2026-10-15 image in
`out/build-6KtHtk1p/result/` passed media checks only; its live boot and fresh
installation remain pending. See [status](status.md#current-acceptance-summary) and the bounded
[security review](security-review-2026-09-30.md) for evidence and audit gaps.
