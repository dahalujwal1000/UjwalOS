# 0001 — Conventional Fedora KDE live/install image with RPM updates

Date: 2026-09-26. Status: selected; compose and VM installation/boot acceptance
passed 2026-09-27. Hardware and release gates remain separate.

## Decision

Use Fedora KDE 44 x86-64, KIWI and Fedora's release-specific image definitions,
the Fedora installer, and conventional RPM updates. Do not mix in an OSTree or
bootc update path for v0.1. Preserve Fedora's supported kernel and boot chain.

Fedora's [KDE download page](https://www.fedoraproject.org/kde/download/)
currently identifies release 44. Fedora's
[build guide](https://fedoraproject.org/wiki/Building_a_Fedora) identifies KIWI
as the tool for most variants and points to the
[release-engineering image definitions](https://forge.fedoraproject.org/releng/kiwi-descriptions).
The [KIWI CLI package](https://packages.fedoraproject.org/pkgs/kiwi/kiwi-cli/index.html)
lists Fedora 44 availability. Checked 2026-09-26.

The historical livemedia-creator instructions are not our implementation path.
The Fedora 44 checkout was subsequently inspected and pinned to
`dfc49a5a10f69941179fdadd96aa6a5984f7c677`. Its `Fedora.kiwi` selects
`KDE-Desktop-Live`, type `iso`, DNF5, release 44. See [image inputs](../../image/README.md).

## Rationale and tradeoffs

Conventional RPMs keep configuration packages and optional third-party gaming
software close to the normal Fedora KDE administration model. Reusing the KDE
definition reduces independent boot/installer integration work.

An image-based alternative offers stronger deployment rollback, but would add
another integration surface for drivers, system extensions, and application
delivery. Its advantages have not been demonstrated for this project, so it
is not selected. Revisit only through a new decision and measured prototype.

Conventional updates do not provide transactional whole-system rollback.
Retaining older kernels, verified backups, and tested rescue procedures are
required; package downgrade is not a universal recovery strategy.

## Reproducibility requirements

Before the first compose, pin the image-description commit, builder/tool RPM
versions, Fedora repositories and metadata, package NEVRAs and checksums,
UjwalOS source commit, configuration hashes, and firmware/VM versions.
Archive redistributable inputs and record source/license obligations. Moving
Fedora mirrors alone cannot provide repeatable historical builds. Do not claim
bit-for-bit reproducibility until two clean builds have been compared.

Source and builder hashes now exist, with an isolated compose entry point.
RPM/metadata snapshots and repeated-build evidence remain release blockers.
See [status](../status.md) for actual build/boot/install results.
