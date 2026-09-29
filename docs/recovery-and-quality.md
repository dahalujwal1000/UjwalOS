# Stage 7 recovery and release quality

Started 2026-09-29 at the owner's request. Stages 3-5 retain open gates; Stage 6
is not implemented. No public release is authorized by starting this stage.
The conventional RPM strategy in decision 0001 remains unchanged.

## Requirements and milestones

1. Document updates, verified backups, older-kernel boot and failed-update triage.
2. Verify engineering artifacts locally without confusing integrity with signing,
   provenance, reproducibility, successful installation or release approval.
3. Test clean installation, normal updates and failed-update recovery on disposable
   file-backed VM disks. Preserve evidence and report each gate independently.
4. Review dual-boot safety without touching host partitions or boot entries.
5. Test keyboard navigation, focus, screen reader support, contrast, scaling and
   multi-monitor behavior. Automated QML screenshots alone are insufficient.
6. Repeat install/update/recovery and hardware smoke tests beyond one laptop.
   Clear licensing, signing/key distribution and reproducibility before release.

First milestone implements local artifact manifests and this protocol. No updater,
rollback engine, bootloader repair script or privileged helper is added.

## Local artifact integrity

In a trusted staging directory containing explicitly selected files:

```sh
python3 scripts/release/artifacts.py create STAGING_DIRECTORY \
  --revision FULL_BUILD_SOURCE_COMMIT \
  --artifact ACTUAL-NAME.iso --artifact packages.txt
python3 scripts/release/artifacts.py verify STAGING_DIRECTORY
```

Use the actual 40-character source commit recorded for that build, not today's
HEAD for an older ISO. The revision is operator-supplied metadata, not attestation.
The tool records SHA-256 and byte size, uses bounded-memory hashing, rejects
symlinks/non-regular artifacts and unsafe names, and never overwrites an existing
`artifact-manifest.json`. Create against completed, immutable build output only.
An interrupted manifest write may leave an invalid file; inspect it and use a fresh
staging directory. Verification checks only listed files, not unrelated contents.

The manifest is explicitly unsigned engineering metadata. Anyone who can replace
both it and an artifact can forge a matching result. Obtain manifests through a
trusted channel; signing and independently verifiable keys remain release gates.
Do not include private logs, phone content or credentials in staging artifacts.
This tool never uploads files, signs artifacts or decides whether tests passed.

## Update protocol for an installed test guest

These are manual steps inside a disposable installed UjwalOS VM, not commands to
run on the development host. Confirm the ISO is detached and the virtual disk
boots independently. Shut down the guest and preserve a copy of its file-backed
disk and firmware variables before testing. Never copy a running VM disk as a
consistent backup. Verify recovery from the backup before testing failures.

Record the image checksum, package versions, free space, baseline boot/login and
test-user preferences. Ensure reliable power and working networking. Review the
transaction; do not bypass RPM signature checks or enable unknown repositories.

```sh
sudo dnf5 upgrade --refresh --offline
dnf5 offline status
```

Only after reviewing the staged transaction and saving work, in the guest:

```sh
sudo dnf5 offline reboot
```

This reboots and changes the guest. After login inspect `dnf5 offline status` and
`dnf5 offline log --number=-1`; retain logs privately and redact before sharing.
Verify boot, networking, desktop preferences and app launches. Offline RPM updates
are not atomic whole-system rollback. The commands are upstream-documented but
have not yet passed UjwalOS Stage 7 VM acceptance.

## Failure and rescue protocol

- If staging fails, do not force a reboot or add dependency-erasing flags blindly.
  Record the error, check space/network and inspect the offline status.
- If boot fails, test selection of a previously installed kernel from the guest
  boot menu. A successful older-kernel boot is a temporary recovery path, not
  proof that the update transaction or proprietary drivers are repaired.
- If no installed kernel boots, use known-good rescue media to inspect the
  virtual disk and recover data. Disk layout, encryption and firmware determine
  repair steps; no generic `grub-install`, formatting or partition rewrite is
  authorized by this guide. Restore the verified cold VM backup when appropriate.
- Inject download/network or transaction interruption failures only into a
  disposable cloned VM. Keep the working baseline and original evidence intact.
- For hardware, preserve independently tested external backups and any disk
  encryption recovery material before updates. Hardware recovery and dual-boot
  repair procedures remain unvalidated; do not infer safety from VM results.

## Acceptance record (all pending)

| Gate | Required evidence |
| --- | --- |
| Current image clean install | Blank virtual disk, ISO detached, two logins/reboots |
| Normal update | Before/after package records, transaction log, boot and app checks |
| Failed-update recovery | Failure injected in clone, recovery steps, restored boot/data |
| Older-kernel/rescue | Boot menu access, older-kernel boot, rescue access and data recovery |
| Dual boot | Layout/firmware review and isolated multi-OS VM test; no host edits |
| Accessibility | Keyboard/focus, screen reader, contrast, scaling and external display results |
| Hardware | Repeated checks on multiple systems with limitations recorded |
| Public artifacts | Licensing, input archive/repeat builds, signing and trusted key distribution |

## Sources

Verified 2026-09-29: [DNF5 upgrade](https://dnf5.readthedocs.io/en/latest/commands/upgrade.8.html)
documents offline staging; [DNF5 offline](https://dnf5.readthedocs.io/en/latest/commands/offline.8.html)
documents status, transaction logs and reboot execution. Fedora's GRUB quick-doc
page was access-blocked during review, so no version-specific bootloader repair
commands are prescribed here. Installed-guest command/version checks remain open.
