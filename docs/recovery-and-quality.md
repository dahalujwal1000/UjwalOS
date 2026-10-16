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
are not atomic whole-system rollback. A small codec transaction passed on
2026-10-16, followed by baseline checks and graphical KVM boot/app checks.
The offline-log lookup returned no log; DNF history and installed package state
provided the recorded evidence instead. This does not close the wider Stage 7
kernel/rescue or interrupted-installation gates.

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

## Installed guest baseline checker

Inside a disposable installed test guest with the ISO detached, run a reviewed
copy of the repository script as the normal desktop user:

```sh
python3 scripts/test/check-installed-system.py --guest-check
```

The explicit flag acknowledges the intended guest context; it does not detect a
VM or prove the ISO is detached. The checker emits JSON to stdout, with separate
PASS, FAIL or UNKNOWN results for the root mount source, SELinux enforcement,
firewalld activity, the three UjwalOS packages and their RPM file verification,
local `liveuser` cleanup, and listening TCP/UDP ports 22 and 10022. Exit codes are
0 for all checks passing, 1 for any failure, and 2 for incomplete evidence.
Missing tools, timeouts and unrecognized output require investigation.

Commands are read-only and have time limits. Combined command output is capped
at 1 MiB; overflow and timeout terminate the command and report UNKNOWN without
using partial results. RPM verification uses `--noscripts`
to suppress package verification scriptlets; account lookup uses the local files
database. No privilege escalation or repair is performed. A port check covers
only the specified ports; it cannot identify SSH on an arbitrary port or establish
firewall policy correctness. RPM verification compares installed files to the
local package database and does not authenticate the publisher. Retain the JSON
with the ISO checksum and VM evidence, reviewing it before sharing.

This checker supports baseline collection before and after update/recovery tests.
It does not execute those tests or certify hardware, update sources, package
advisories, multi-user permissions, signing or release readiness.
It does not check the display manager's user units: an all-PASS baseline can
coexist with a failed graphical login. Always observe desktop login separately.

## Acceptance record

The table below covers operational/release gates, not the completed artifact-tool
milestone. As of 2026-10-16, artifact-tool unit tests and the recorded manifest
verification passed. The corrected ISO passed compose, media checks, live boot,
fresh installation, ISO-detached setup/login, reboot and second login. The bounded
security review's three findings have source fixes and passing regression
checks; runtime and installed-image acceptance remain separate. See the
[consolidated evidence](status.md#current-acceptance-summary).

| Gate | Required evidence |
| --- | --- |
| Current image clean install | PASS 2026-10-16: blank virtual disk, ISO detached, first login, reboot and second login; see status |
| Normal update | PASS for the recorded small codec transaction; kernel/core updates remain untested |
| Failed-update recovery | Pre-transaction network failure and subsequent KVM boot passed; interrupted installation/rescue remains open |
| Older-kernel/rescue | Boot menu access, older-kernel boot, rescue access and data recovery |
| Dual boot | Layout/firmware review and isolated multi-OS VM test; no host edits |
| Accessibility | Keyboard/focus, screen reader, contrast, scaling and external display results |
| Hardware | Repeated checks on multiple systems with limitations recorded |
| Public artifacts | Licensing, input archive/repeat builds, signing and trusted key distribution |
| Security remediation | Source regression tests and corrected ISO VM checks passed; broader runtime security gates remain open |
| Custom-package updates | Local engineering 0.1-4 to 0.1-5 update and app launch passed; authenticated delivery/signing remains open |
| Runtime security | Full package advisory review, SELinux, firewall/listeners, account cleanup and multi-user tests |

## Sources

Checker command semantics verified 2026-10-16 against upstream
[RPM verification](https://rpm.org/docs/6.0.x/man/rpm.8),
[getent](https://man7.org/linux/man-pages/man1/getent.1.html),
[findmnt](https://man7.org/linux/man-pages/man8/findmnt.8.html),
[ss](https://man7.org/linux/man-pages/man8/ss.8.html),
[getenforce](https://man7.org/linux/man-pages/man8/getenforce.8.html), and
[systemctl source documentation](https://github.com/systemd/systemd/blob/main/man/systemctl.xml).
The rendered systemd manual was access-blocked; its upstream source was used.

Verified 2026-09-29: [DNF5 upgrade](https://dnf5.readthedocs.io/en/latest/commands/upgrade.8.html)
documents offline staging; [DNF5 offline](https://dnf5.readthedocs.io/en/latest/commands/offline.8.html)
documents status, transaction logs and reboot execution. Fedora's GRUB quick-doc
page was access-blocked during review, so no version-specific bootloader repair
commands are prescribed here. DNF5 5.4.6.0 guest command checks and the limited
transaction evidence are recorded in [status](status.md); wider recovery remains open.
