# UjwalOS engineering rules

Read README.md, plan.md, docs/status.md, and the relevant architecture decision
before making changes. The product specification lives in plan.md.

- The owner has authorized Stage 1 implementation, including isolated image builds
  and file-backed QEMU tests. Do not repeatedly request the same approval.
- Verify release-sensitive commands, package names, APIs, and build tooling
  against current upstream documentation. Record sources and verification dates.
- Use one image/update strategy. No kernel, bootloader, desktop, or runtime forks.
- Build in a disposable environment. Never alter host boot entries, overwrite
  physical disks, reboot the host, or install system packages without explicit
  host-change authorization. Preserve SELinux, thermal controls, and updates.
- Package desktop defaults; never repeatedly overwrite existing user preferences.
- Keep proprietary software optional. No mandatory account or cloud upload.
- Run UI code unprivileged. Future privileged operations must be narrowly scoped,
  PolicyKit-authorized, and recoverable after crashes and reboot.
- Report code written, image built, VM booted, installation tested, and hardware
  tested separately. Never infer successful boot from a successful compose.
- Keep changes focused. Do not create empty feature directories or claim planned
  features exist. Preserve upstream licenses and document redistribution review.
- Run relevant checks and record exact commands/results in docs/status.md.
  Do not publish releases before the documented gates pass.
