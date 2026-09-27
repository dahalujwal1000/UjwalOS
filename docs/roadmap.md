# Roadmap

The full scope and acceptance wording are preserved in [plan.md](../plan.md).
Stage 1 compose and VM acceptance passed on 2026-09-27;
separate gate evidence and remaining release limits are in status.md.

| Stage | Deliverable | Gate |
| --- | --- | --- |
| 0 | Architecture, inputs, licenses, threats, hardware targets, build plan | Another developer can reproduce exact inputs and build command |
| 1 | Minimal branded Fedora KDE live/install ISO | Compose, live Plasma boot, installer, blank-disk install and installed boot pass |
| 2 | Packaged desktop, login and Plymouth identity | New-account defaults work; existing preferences survive updates |
| 3 | Optional gaming setup | Reproducible small game matrix versus stock Fedora KDE |
| 4 | Qt/QML Gaming Center and narrow helper | Authorization and restoration on disable, crash and reboot pass |
| 5 | KDE Connect phone panel | Real-device pairing, revoke, reconnect and permission-change tests pass |
| 6 | Optional Waydroid experiment | Hardware/app failures, rights, security and clean removal documented |
| 7 | Recovery and release quality | Install, update, failed-update recovery, dual-boot review and repeated hardware tests pass |
| 8 | Public v1.0 | Installation and recovery tested beyond one laptop; limitations published |

Completed bounded task: build the minimal pinned Fedora 44 KDE derivative and
pass the live boot/installer/installed-boot gate, including login and restart.
The current milestone is packaged desktop identity and fresh-account/update
validation. Custom applications remain deferred. Live GRUB warning diagnosis
and release-limit reviews remain open.
