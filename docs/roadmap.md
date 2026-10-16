# Roadmap

The full scope and acceptance wording are preserved in [plan.md](../plan.md).
As of 2026-10-16, the accepted apps 0.1-4 ISO passed compose, media, live boot,
fresh installation and disk-only reboot/login checks. Apps 0.1-5 separately
passed installed-VM graphical monitoring checks; its new compose is in progress.
Stages 1 and 2 acceptance passed on earlier recorded images. Separate gate
evidence and remaining release limits are in the
[current acceptance summary](status.md#current-acceptance-summary). The table
below defines target gates, not a claim they all passed.

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
track opt-in system monitoring and pending authorization/restoration gates. Stage 5 now
has a status/battery panel, confirmed unpair requests and native KDE Connect
pairing launcher in apps 0.1-4. Earlier live-VM smoke tests and owner-reported
basic phone linking passed; [phone requirements](phone-panel.md) track remaining
transfers, permissions, revocation and real-device acceptance. Hardware and
release-limit reviews remain open.

Stage 7 started on 2026-09-29 with a local artifact integrity verifier and
[recovery/quality protocol](recovery-and-quality.md). Cold-copy restore, a small
offline update and network-staging failure passed in a VM. Interrupted update,
kernel/rescue, accessibility, dual-boot and repeated hardware tests remain pending.
Stage 6 remains unimplemented; starting Stage 7 does not close earlier gates.

The bounded [security review](security-review-2026-09-30.md) is recorded. Source
remediation and regression checks for its three findings passed on 2026-10-15;
the corrected ISO passed compose, media, live boot and installation.
Signed artifacts, authenticated custom-package updates and a full
distribution/runtime audit remain release work; Stage 8 has not started and
public release readiness is not claimed.
