# Compatibility and dependency review

Checked 2026-09-26. No supported-hardware or gaming certification is claimed.

## Dependency status

| Component | Initial disposition | Evidence / remaining work |
| --- | --- | --- |
| Fedora KDE 44 x86-64 | Selected base | Official download page verified; description and builder pinned; RPM repositories moving |
| KIWI / kiwi-cli | Selected image builder | Fedora 44 package availability verified; KIWI 11.0.2 installed; boxed builder available |
| Kernel, firmware, Mesa, PipeWire, Plasma | Inherit base | Exact package set, versions, licenses follow pinned KDE definition |
| KDE Connect | First phone integration | kde-connect verified for Fedora 44 and explicitly selected; phone tests pending |
| Qt 6 / KDE frameworks | Future UI | Resolve exact development packages when an application is scoped |
| Steam / Proton | Optional Stage 3 setup | Source and no-bundling review recorded in gaming-setup.md; Steam and real game testing pending |
| GameMode, MangoHud, Gamescope | Optional Stage 3 tools | Fedora 44 packages verified 2026-09-28; install completed in live VM, but GameMode governor self-test failed under emulation and real game tests remain pending |
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
| x86-64 UEFI QEMU VM | NT | N/A | NT | NT | N/A | NT | NT | KVM hidden in sandbox; available in approved build execution |
| Intel integrated graphics | NT | NT | NT | NT | NT | NT | NT | No test machine identified |
| AMD graphics | NT | NT | NT | NT | NT | NT | NT | No test machine identified |
| Intel/NVIDIA RTX 3050 hybrid laptop | NT | NT | NT | NT | NT | NT | NT | Suggested target; exact model and Secure Boot state unknown |

Record model, firmware, image checksum, kernel/driver versions and evidence for
each actual test. VM rendering does not validate physical GPU drivers or gaming.
Measure games against stock Fedora KDE on the same hardware with matching
versions, settings, power conditions and repeated runs. Record anti-cheat and
launcher limitations; do not claim every Windows game or Android APK works.
