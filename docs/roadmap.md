# Roadmap

The full scope and acceptance wording are preserved in [plan.md](../plan.md).
Stages 1 and 2 compose and VM acceptance passed by 2026-09-28;
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

Completed bounded tasks: build the minimal pinned Fedora 44 KDE derivative;
pass its live boot, installer and installed-boot gates; package the desktop,
login and Plymouth identity; and pass fresh-account and update-preservation
validation. Stage 3 optional gaming-setup implementation is complete; acceptance
testing remains pending, including games, baseline comparisons and hardware. Stage 4 has
started with a tested Qt profile editor; its [requirements](gaming-center.md)
track pending monitoring, authorization, restoration and VM gates. Stage 5 now
has a read-only phone status panel; [phone requirements](phone-panel.md) track
pairing, transfers, permissions and real-device acceptance. Hardware and
release-limit reviews remain open.
