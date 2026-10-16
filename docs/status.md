# Status and unreleased notes

## 2026-10-16 - Monitoring graphical acceptance and compose retry

At resume the recovery VM was no longer running. Its serial evidence was
preserved as `out/vm-recovery-QgQ9GZNd/serial-update-evidence.log` before launch.
`qemu-img check out/vm-recovery-QgQ9GZNd/disk.qcow2` reported no errors.
`UJWALOS_VM_ACCEL=kvm scripts/test/test-iso.sh --installed
out/vm-recovery-QgQ9GZNd --headless` now ran successfully: QMP status running,
branded graphical login, authenticated Plasma desktop, no OS ISO attached.
This also establishes graphical boot after the earlier failed-staging test.

Installed Gaming Center 0.1-5 launched via
`python3 /usr/share/ujwalos/gaming-center/main.py` in the ordinary user's
graphical session. Monitoring was initially off, enabling the switch displayed
CPU and estimated memory usage, and disabling/closing/reopening returned to off.
Screenshots: `kvm-login.png`, `desktop-new.png`, `metrics-window.png`,
`metrics-enabled.png`, `metrics-reopened.png` in that VM directory. Guest
`systemctl poweroff` completed and QEMU exited 0. No host reboot occurred.

The earlier TCG greeter failure is not claimed fixed. Its journal showed KWin
unable to open `/dev/dri/card1` and no suitable DRM device; greeter user units
failed even while the system-level `systemctl --failed` list was empty. The
baseline checker is deliberately scoped and does not establish graphical health.
KVM working on retry does not establish the cause of its earlier entry failure.

Independent lower-cost read-only review found no concrete monitoring bugs;
eight metrics and six Gaming Center UI tests passed. Parent reran
`python3 -m unittest discover -s tests/config -q`: 75 passed.
`scripts/build/build-iso.sh --validate` passed in `out/build-9K9HoH5I`.
An isolated `scripts/build/build-iso.sh` run was then started; no new ISO
success or VM acceptance is inferred until its result is recorded.
Build command options rechecked 2026-10-16 against
[KIWI boxbuild](https://osinside.github.io/kiwi/commands/system_boxbuild.html).

## 2026-10-16 - Monitoring and recovery work in progress

New source adds opt-in, read-only aggregate CPU/memory monitoring to Gaming
Center (off by default, two-second samples, no telemetry storage or privileged
changes). Apps RPM release advances to 0.1-5; the existing ISO remains 0.1-4.
A lower-cost agent handles the bounded metrics parser/tests; parent integration
handles Qt controls, packaging, review and isolated VM testing.

The guest checker now caps combined command output at 1 MiB, kills/reaps timed
out or overflowing commands and reports UNKNOWN. RPM query failures are no
longer confused with an explicitly absent package. The VM launcher now supports
`UJWALOS_VM_ACCEL=auto|kvm|tcg`, including explicit TCG for hosts where accessible
KVM fails at runtime. Neither change modifies host virtualization settings.

Checks run (guest update follow-up still in progress):

- `python3 -m unittest discover -s tests/config -q`: final run 75 passed,
  including individual CPU counter decreases and oversized numeric values.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software UJWALOS_UI_SCREENSHOTS=out/metrics-ui out/stage4-venv/bin/python -m unittest discover -s tests/ui -q`:
  14 passed; screenshot at 560x500 inspected, scrollable form rendered.
- Same Qt command with `QT_SCALE_FACTOR=2`: 14 passed.
- `dbus-run-session -- out/stage4-venv/bin/python tests/integration/test_phone_transport.py -q`:
  two passed.
- A first UI attempt with system Python failed because PySide6 is absent;
  reruns above use the existing repository-local environment, no host install.
- `bash scripts/build/build-apps-rpm.sh out/apps-metrics-Ui5ngRd0`: built
  `apps-rpmbuild/RPMS/noarch/ujwalos-apps-0.1-5.fc44.noarch.rpm`.
  Direct script execution first returned permission denied (tracked mode 0644);
  explicit Bash succeeded. RPM warned about missing changelog/source epoch.
  This preliminary RPM precedes final parser review and is not an ISO build.
- Final reviewed rebuild: `bash scripts/build/build-apps-rpm.sh
  out/apps-final-NrizDYKE` exited 0. RPM at
  `out/apps-final-NrizDYKE/apps-rpmbuild/RPMS/noarch/ujwalos-apps-0.1-5.fc44.noarch.rpm`,
  SHA-256 `4e23432c885cad195a4a51a30d8c082220c3741a2ad7ad477ff69f286536d412`.
  `rpm -qpl` confirms metrics.py; image-generation tests also assert its presence.
  UI tests additionally exercise the QML monitoring switch and status binding.
  `bash -n scripts/test/test-iso.sh scripts/build/build-apps-rpm.sh` and
  `git diff --check` passed. Guest installation evidence follows below.

Recovery evidence: while the original VM was stopped, its disk and UEFI variables
were copied to `out/recovery-baseline-e8nyY0u4`, then restored to
`out/vm-recovery-QgQ9GZNd` using `cp --reflink=auto --sparse=always` for each disk
and `cp` for `OVMF_VARS.fd`. `qemu-img compare -f qcow2 -F qcow2
out/recovery-baseline-e8nyY0u4/disk.qcow2 out/vm-recovery-QgQ9GZNd/disk.qcow2`
reported identical images; `cmp` on both variables files exited 0.
Cold backup SHA-256: disk
`7017f94d8e2202fd0321bf459dca9f94c256f8fd0a67e9f40c22dd85e753fa69`, variables
`50e35c6b79b6f4145a8d1c733881f8fa351f38e787d4e690894cb891ccb0c045`.

The restored copy failed KVM entry with hardware error 0x0; software-emulated
TCG boot reached an authenticated installed-system TTY. Graphical acceptance
of this restored TCG session is not yet established. Auxiliary read-only media
`out/guest-tools-ieixL7rS.iso` supplied the checker snapshot from commit 16134f8
(before current output-cap changes), not an OS boot image. In the guest,
`sudo mount -o ro /dev/sr0 /mnt` then
`python3 /mnt/check-installed-system.py --guest-check | tee baseline.json`
reported all eight checks PASS, including apps 0.1-4 integrity. Report exported
through guest serial with `sudo tee /dev/ttyS0 < baseline.json`; retained in
`out/vm-recovery-QgQ9GZNd/serial.log`. No SSH/host forwarding was introduced.

Guest DNF5 5.4.6.0: `sudo dnf5 upgrade --refresh --offline --assumeno`
previewed a two-package OpenH264 transaction replacing noopenh264. Then
`sudo dnf5 upgrade --offline -y` staged it successfully and
`sudo dnf5 offline status` confirmed pending work. `sudo dnf5 offline reboot`
was confirmed; the VM rebooted and accepted TTY login. `dnf5 history info last`
reported transaction 3, `Status: Ok`, with the expected two installs and one
replacement. `dnf5 offline status` reported no stored transaction; `rpm -q
openh264 mozilla-openh264 noopenh264` confirmed the expected state. However,
`sudo dnf5 offline log --number=-1` returned `Cannot find logs with this index`;
the history/package evidence, not that log command, establishes completion.
The original checker again returned all eight PASS after the reboot. This is
a small codec transaction, not kernel-update or general rollback acceptance.
The original VM and cold backup remain untouched. No new ISO, physical hardware
test, signing approval or public-release clearance is claimed.

The reviewed checker and apps RPM were copied onto auxiliary data media
`out/guest-final-tools-b0o6IoE1.iso` using `xorriso -as mkisofs -R -J
-V UJWAL_TEST_TOOLS -o out/guest-final-tools-b0o6IoE1.iso
out/guest-final-tools-b0o6IoE1`. QMP `query-block` identified the empty second
CD drive; `blockdev-change-medium` attached that media read-only using its QOM
device path. Inside the guest, `sudo mount -o ro /dev/sr1 /media` and
`python3 /media/check-installed-system.py --guest-check` returned all eight PASS.
`sudo rpm -Uvh /media/ujwalos-apps-0.1-5.fc44.noarch.rpm` then upgraded the app
package successfully (existing explicit unsigned-local-engineering exception,
not a signed update acceptance). The checker subsequently reported clean
0.1-5 integrity with all eight PASS.

As the ordinary guest user, Python imported `MetricsCollector` from the installed
`/usr/share/ujwalos/gaming-center`, sampled, slept two seconds and sampled again.
First CPU was unavailable as designed; second CPU was 51.74%, memory estimate
16.05%, with no errors. These transient VM values are functional evidence only,
not a performance benchmark or graphical application acceptance.

Failed-staging test inside that disposable guest:

```sh
sudo dnf5 --setopt=proxy=http://127.0.0.1:9 --setopt=timeout=3 --setopt=retries=1 --setopt='*.skip_if_unavailable=False' upgrade --refresh --offline -y 2>&1 | sudo tee /dev/ttyS0
printf 'DNF_EXIT=%s\n' "${PIPESTATUS[0]}" | sudo tee /dev/ttyS0
sudo dnf5 offline status
python3 /media/check-installed-system.py --guest-check
```

The deliberately unreachable per-command proxy caused metadata connection errors,
`DNF_EXIT=1`, no stored offline transaction, and all eight baseline checks PASS.
No persistent repository/proxy/security settings were changed. This covers
pre-transaction network failure only; interrupted RPM installation, kernel
fallback, full rescue and post-failure reboot acceptance remain separate gates.

Upstream references checked 2026-10-16:
[DNF5 offline](https://dnf5.readthedocs.io/en/latest/commands/offline.8.html),
[DNF5 upgrade](https://dnf5.readthedocs.io/en/latest/commands/upgrade.8.html),
[QEMU image tools](https://www.qemu.org/docs/master/tools/qemu-img.html),
[Linux procfs](https://www.kernel.org/doc/html/latest/filesystems/proc.html),
[Qt timers](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTimer.html).
Also verified: [QMP removable media](https://www.qemu.org/docs/master/interop/qemu-qmp-ref.html#command-blockdev-change-medium)
and [DNF5 configuration](https://dnf5.readthedocs.io/en/latest/dnf5.conf.5.html).

## 2026-10-16 - Installed guest baseline checker

Implemented `scripts/test/check-installed-system.py` with an explicit
`--guest-check` acknowledgement, fixed read-only commands, five-second command
timeouts, locale-stable parsing and JSON PASS/FAIL/UNKNOWN results. It checks
root-source shape, SELinux, firewalld, the three installed UjwalOS packages and
their file integrity, local `liveuser` absence and TCP/UDP ports 22/10022.
RPM verification suppresses verification scripts; account lookup uses local
files. Reports omit account records and full listener lists. Reported diagnostics
are truncated; subprocess capture itself is not a hard memory-bound interface.

A lower-cost implementation agent wrote the checker and tests; integration review
added stricter parsing, locale handling, redaction and ambiguous-output cases.
The recovery guide now includes the command and limits and corrects stale
installation status. Upstream command sources and verification date are recorded
in [the recovery guide](recovery-and-quality.md#sources).

Verification: `python3 -m unittest discover -s tests/config -q` passed all
64 tests (48 existing plus 16 checker tests). `git diff --check` passed.
Checker tests use mocked command responses, including timeout, absent tools,
malformed records, integrity failures, account privacy and CLI exit status.
UI and D-Bus suites were not rerun for this standalone tooling change.

Code and automated checks are complete for this milestone. The new checker has
not yet run in a guest and is not included in the existing ISO. No new compose,
VM boot, installation or hardware test is claimed. Next: collect its baseline
inside the installed guest, preserve a cold VM backup, verify restoration, then
exercise normal and failed-update recovery on disposable copies. Signing,
licensing and the wider runtime/release gates remain open.

## 2026-10-16 - Corrected ISO VM installation acceptance

The corrected ISO `out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso`
(3,834,904,576 bytes; SHA-256
`a1efa6cc0dfb5beb94e64fab11c658a20463980cbc9f8875295a3a6c3cf38775`)
completed its isolated QEMU/KVM acceptance sequence. The VM used UEFI firmware,
a newly created 40 GiB file-backed QCOW2 disk, QEMU user networking and local
Unix sockets. No physical disk, host boot entry or host package was changed.

Exact commands and recorded results:

- `cd out/build-6KtHtk1p/result && sha256sum -c SHA256SUMS`: passed.
- `scripts/test/test-iso.sh out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso --check-only`:
  passed SHA-256, ISO9660 and UEFI boot-catalog checks.
- `scripts/test/test-iso.sh out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso --headless`:
  UEFI GRUB rendered and the live session reached usable KDE Plasma. Gaming
  Center and Phone Panel both launched. In the live guest, `rpm -q` reported
  `ujwalos-apps-0.1-4.fc44.noarch`, `ujwalos-branding-0.4-1.fc44.noarch` and
  `ujwalos-gaming-setup-0.1-1.fc44.noarch`; `rpm -V` emitted no differences,
  `getenforce` returned `Enforcing`, and `systemctl is-active firewalld`
  returned `active`. `ss -lntup` showed no SSH or port 10022 listener.
- Anaconda selected only the 42.9 GB Virtio device (`vda`), completed the fresh
  installation and displayed `Successfully installed`. The VM directory is
  `out/vm-oU7JxgZx`; screenshots are retained there as local test evidence.
- `scripts/test/test-iso.sh --installed out/vm-oU7JxgZx --headless`: booted the
  same QCOW2 with no ISO attached. Plasma Initial System Setup created a
  disposable account, login reached the branded desktop, and `/` was mounted
  from `/dev/vda3[/root]`. Installed package versions and `rpm -V`, SELinux,
  firewall and listener results matched the live checks. A reboot returned to
  the login screen and the second login reached Plasma successfully.
- Post-documentation regression run: `python3 -m unittest discover -s
  tests/config -v` passed 48 tests; `QT_QPA_PLATFORM=offscreen
  QT_QUICK_BACKEND=software out/stage4-venv/bin/python -m unittest discover -s
  tests/ui -v` passed 13 tests; and `dbus-run-session --
  out/stage4-venv/bin/python tests/integration/test_phone_transport.py -v`
  passed two tests. The relative Markdown file-link check and
  `git diff --check` also passed.

This closes the latest image's VM live/install/reboot gates only. Display-resize
acceptance was not separately exercised. Physical hardware, USB installation,
Secure Boot, dual/triple boot, gaming performance, full advisory/runtime review,
signed custom-package updates, licensing and Fedora trademark/remix review
remain open. No public release is approved.

## 2026-10-15 - Security remediation and corrected compose

Implemented the three findings from the September security review:

- Fedora repositories now explicitly require package signatures, with global
  RPM signature checking enabled too. The generated description retains the
  Fedora signing keys and metalinks. The unsigned local UjwalOS RPM installation
  remains an explicit, separate engineering exception.
- A private QEMU launcher removes the boxed plugin's exact SSH host-forward
  argument, preserving outbound networking and 9p sharing. Unexpected forwarding
  arguments fail before QEMU launches. The actual builder process has
  `-nic user,model=virtio` and no host forward; `ss -ltnp` showed no QEMU listener
  and no port 10022 listener during this compose.
- Gaming Center reads profiles with nonblocking/no-follow opens, checks for a
  regular file, limits input to 256 KiB and 256 profiles, and applies matching
  save limits. Rejected files are preserved. The apps RPM is now 0.1-4.

The networking and profile changes were independently implemented and reviewed;
signature enforcement was integrated with them. Existing owner documentation
edits and `opencode.md` were preserved.

Verification commands/results:

- `python3 -m unittest discover -s tests/config -v`: 48 passed. Includes real
  KIWI-generated DNF configuration checks, real libdnf unsigned-RPM rejection
  in a temporary install root, QEMU argument/lookup/listener checks, and profile
  FIFO, symlink, directory, byte/count limit, malformed UTF-8/JSON and preservation
  regressions. The FIFO check runs in a subprocess with a three-second timeout.
- `python3 -m unittest discover -s tests/config -p test_builder_network.py -v`:
  four passed again after extending changed-port and duplicate-forward cases.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software out/stage4-venv/bin/python -m unittest discover -s tests/ui -v`:
  13 passed.
- `dbus-run-session -- out/stage4-venv/bin/python tests/integration/test_phone_transport.py -v`:
  two passed on a synthetic isolated bus.
- `scripts/build/build-iso.sh --validate`: passed in `out/build-YA5E5UtF`.
  Expanded XML contains both repository checks and `rpm-check-signatures=true`.
  The final pre-push repeat also passed in `out/build-IMkKVQNJ`.
- `bash -n scripts/build/qemu-no-forward.sh`: passed; configuration tests also
  checked existing shell entry points. `git diff --check`: passed.
- `scripts/build/build-iso.sh`: passed in `out/build-6KtHtk1p`; description,
  Fedora metalink preflight and all three pinned builder hashes passed. Builder
  guest and wrapper both exited 0. The ISO is 3,834,904,576 bytes with SHA-256
  `a1efa6cc0dfb5beb94e64fab11c658a20463980cbc9f8875295a3a6c3cf38775`.
- `scripts/test/test-iso.sh out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso --check-only`:
  passed SHA-256, ISO9660 and UEFI boot-catalog checks. This is not a boot test.
- Prepared [GitHub VM-test pre-release draft](github-vm-test-prerelease-draft.md)
  with artifact details, verification, VM instructions and limitations. Public
  distribution remains blocked by the internal license placeholder and pending
  Fedora trademark/remix review; controlled VM testing remains the draft scope.
- `python3 tests/integration/check_rpm_signatures.py --unsigned-rpm out/build-6KtHtk1p/description/root/image/ujwalos-apps.rpm --signed-rpm out/signature-check-OAMeKmX8/fedora-release-common-44-18.noarch.rpm --trusted-key /usr/share/distribution-gpg-keys/fedora/RPM-GPG-KEY-fedora-44-primary --unrelated-key /usr/share/distribution-gpg-keys/fedora/RPM-GPG-KEY-fedora-43-primary`:
  all five checks passed. A real signed Fedora RPM is rejected with an empty
  keyring and with only the unrelated Fedora 43 key trusted; importing Fedora
  44's correct key makes it pass. The unsigned apps RPM remains rejected before
  and after imports. All key imports occur in a temporary install root.
  This extra check followed an independent read-only review, which found no
  concrete code regression and identified the missing wrong-key case.
  Fixture download command:
  `curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 15 --max-time 45 https://dl.fedoraproject.org/pub/fedora/linux/updates/44/Everything/x86_64/Packages/f/fedora-release-common-44-18.noarch.rpm -o out/signature-check-OAMeKmX8/fedora-release-common-44-18.noarch.rpm`.
  Verified fixture SHA-256:
  `ea06ce5597746df56a5cc7c3bd184a8e0b05eec048f60456b0b9469fc59a0cdc`.

Code, local RPM preparation and corrected ISO compose/media checks are complete;
the 2026-10-16 entry records its live boot, fresh installation and disk-only
reboot. No hardware test or public release is claimed. Host packages, physical
disks and boot entries were not changed.
A full distribution advisory/runtime audit remains pending. Signed artifacts
and custom-package updates remain open.

Sources verified 2026-10-15: [signature policy](../image/README.md),
[boxed networking](build-and-test.md), and
[Python file-descriptor APIs](https://docs.python.org/3/library/os.html#os.open).

## Current acceptance summary

Baseline reconciled 2026-10-16; see the newest entries above for source,
package and VM evidence. PASS applies only to the
recorded artifact and test scope, not automatically to newer images. Documentation
updates do not constitute new implementation, security fixes or test execution.

| Stage | Completed implementation / evidence | Remaining implementation or testing |
| --- | --- | --- |
| 0 | Specification, architecture decision, initial threat model and build plan | Release input snapshots, licensing and complete dependency audit remain open |
| 1 | Pinned compose; newest corrected ISO passed UEFI live Plasma, blank-disk install, ISO-detached boot, first login, reboot and second login | Resolve live GRUB warnings; hardware and Secure Boot |
| 2 | Packaged desktop/login/Plymouth identity; new-account and existing-preference preservation tests passed | Repeat relevant regressions on release candidate; broader scaling/accessibility/hardware coverage |
| 3 | Optional setup RPM/launcher; live tools installation and installed-guest authorization cancellation passed | Steam/Proton, native-game baseline, controller, GameMode restoration, overlays, Gamescope and real GPU/driver tests; no NVIDIA installer implemented |
| 4 | Profile editor, private atomic saves, fixed previews, reset, instance lock; apps 0.1-5 adds opt-in aggregate CPU/memory monitoring with installed-VM graphical acceptance | New ISO integration, per-game applied state, authorized settings/restoration and accessibility remain open |
| 5 | Status/battery snapshots, confirmed unpair requests, native pairing launcher; automated and current live-VM smoke tests passed; basic phone link owner-tested PASS | Notifications/clipboard/transfers integration; real revocation, rejection, reconnect, permissions, multi-user and current installed-session tests |
| 6 | No implementation | Optional Waydroid evaluation, implementation and all acceptance tests |
| 7 | Manifest/checker tools, cold-copy restore, codec offline update, failed-network staging, local app RPM upgrade and subsequent graphical boot passed | Signing/authenticated delivery, full CVE/runtime audit, interrupted installation, kernel/rescue, accessibility, multi-OS and hardware gates |
| 8 | No public release | Prior gates, licensing/trademark clearance, supported-system evidence and authorized publication |

### Latest image gates

Newest artifact: `out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso`.
It is the newest composed, media-checked and VM-tested image.

| Gate | Recorded result |
| --- | --- |
| Compose and media checks | PASS: wrapper/guest exit 0, checksum, ISO9660, UEFI catalog |
| Unsigned artifact manifest | PENDING for this ISO; checksum exists but no source-revision manifest was created from the dirty build worktree |
| Live VM | PASS 2026-10-16: UEFI GRUB, Plasma, Gaming Center and Phone Panel |
| Fresh install and disk-only reboot | PASS 2026-10-16: 40 GiB QCOW2, ISO detached, setup/login/reboot/second login |
| Basic real-phone linking | Owner reports PASS; exact image/device/feature scope unspecified |
| Gaming performance | PENDING acceptance; owner reported about 10 FPS in VirtualBox with llvmpipe, not a physical GPU benchmark |
| Display scaling | OPEN: owner reported VirtualBox scrollbars/fit issues; no confirmed resolution |
| USB/hardware, Secure Boot, dual/triple boot | PENDING; no physical installation safety certification |

### Remaining test order

1. Complete remaining corrected-image security validation. Source fixes,
   regression checks, compose/media checks and scoped runtime checks passed.
2. Finish the untested runtime scope: display resize/scaling, live-account
   cleanup, permissions, update sources and complete package advisories.
3. Repeat relevant VM gates for any later release-candidate image; results do
   not transfer automatically between artifacts.
4. Run real-phone rejection/revocation/reconnect/permission/multi-user tests and
   the documented gaming/controller/driver matrix against stock Fedora.
5. Complete Stage 4-6 missing functionality before claiming their full gates.
   Run Stage 7 normal/failed updates, backup restore, older-kernel/rescue,
   accessibility and isolated multi-OS tests before physical triple-boot testing.
6. Finish signed distribution/custom-package updates, reproducibility, licensing
   and repeated hardware testing before any public release.

Latest recorded automated run (2026-10-16): 75 configuration,
14 Qt UI and 2 synthetic D-Bus tests passed. Earlier libdnf signature checks
and current 200% high-DPI smoke coverage are
recorded separately; none of these results closes the pending runtime gates.

## 2026-09-30 - Documentation reconciliation

Updated README, roadmap, build/test, compatibility, gaming, phone, recovery and
security/release guides to distinguish implementation, tested behavior and open
gates. Corrected stale apps RPM version, phone capabilities and test-count text.
Preserved historical evidence and the original product specification. No code,
ISO, host configuration or user-owned probe files were changed. Documentation
verification: `git diff --check` passed, and a read-only Python link check found
all relative Markdown file targets present (external URLs/anchors not checked);
application/VM tests were not rerun for these prose-only changes.

## 2026-09-30 - Security review, prioritized findings

Completed a first-party source/configuration review and selected upstream checks;
see [security review](security-review-2026-09-30.md) for scope, evidence and limits.
Priorities: P1 missing Fedora RPM signature enforcement during compose; P2
unnecessary wildcard-bound builder SSH forwarding (remote compromise not proven);
P3 local Gaming Center profile-file blocking. Unsigned distribution artifacts and
the missing custom-package update channel remain separate release security gaps.

Verification: `python3 -m unittest discover -s tests/config -v` passed 35 tests;
`QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software out/stage4-venv/bin/python -m unittest discover -s tests/ui -v`
passed 13; `dbus-run-session -- out/stage4-venv/bin/python tests/integration/test_phone_transport.py -v`
passed 2 on an isolated synthetic bus after sandbox socket restrictions required
a permitted rerun. A temporary FIFO profile-load reproducer confirmed blocking;
its subprocess was terminated/reaped and its fixture removed. No personal data
or host settings were changed. A nested-JSON probe did not reproduce a crash.

This is not a complete ISO CVE scan or runtime security certification. No fixes,
new ISO, installation tests or GitHub publication were performed in this review.

## 2026-09-30 - Current ISO verified; owner phone-link test passed

The owner reports basic phone linking works: PASS (owner-tested). Exact phone,
Android version, image and feature coverage were not provided. Mark this bounded
test done, not all Stage 5 features or revocation/permission/multi-user gates.

The requested fresh ISO was composed on 2026-09-29 from source commit
`0054c00423b5cf81d01d1846ec1273695fd37f21`:
`out/build-9BaEqZ1c/result/UjwalOS-0.1.x86_64-44-0.iso`.
Size: 3,788,185,600 bytes. SHA-256:
`c1d38ba327802c95b6fc00ad8f5dfc8e6a00de43a6eca1cf037f49ec2c760563`.
Both wrapper `exit-code` and guest `result/result.code` are 0. SELinux contexts
and LZMA EROFS compose completed. The package manifest confirms `ujwalos-apps`
0.1-3.fc44, KDE Connect 26.08.1-1.fc44 and PySide6 6.11.2-1.fc44.

Verification commands/results:

- `python3 -m unittest discover -s tests/config -v`: 35 passed before compose.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software
  out/stage4-venv/bin/python -m unittest discover -s tests/ui -v`: 13 passed.
- `scripts/build/build-iso.sh`: passed in `out/build-9BaEqZ1c`.
  Earlier `out/build-mOvX2Zty` failed repository preflight with curl exit 28;
  `out/build-UaG8r8M0` disappeared during interruption with no ISO. Logs retained.
- `scripts/test/test-iso.sh
  out/build-9BaEqZ1c/result/UjwalOS-0.1.x86_64-44-0.iso --check-only`: passed
  SHA-256, ISO9660 and UEFI boot catalog. Compose reports hybrid MBR/GPT layout.
- `python3 scripts/release/artifacts.py create out/build-9BaEqZ1c/result
  --revision 0054c00423b5cf81d01d1846ec1273695fd37f21
  --artifact UjwalOS-0.1.x86_64-44-0.iso
  --artifact UjwalOS-0.1.x86_64-44-0.packages`: passed.
  `python3 scripts/release/artifacts.py verify out/build-9BaEqZ1c/result`:
  passed, including a repeat on 2026-09-30. Manifest is unsigned engineering data.
- `scripts/test/test-iso.sh
  out/build-9BaEqZ1c/result/UjwalOS-0.1.x86_64-44-0.iso --headless`: created
  `out/vm-XD4lUSCr`, KVM/UEFI, 4 GiB, two vCPUs, private 40 GiB virtual disk.
  Branded Plasma reached (`boot.png`); updated Phone Panel opened (`phone.png`).
  After interruption and checking no QEMU remained, restarted with
  `bash out/vm-XD4lUSCr/qemu-command.sh`. Plasma booted again (`resumed.png`).
  Phone Panel's Open KDE Connect button opened the actual native app
  (`native-kdeconnect.png`); Refresh returned "No devices found"
  (`phone-refreshed.png`). No real phones were paired in this isolated test.
  Guest shutdown was requested through its launcher with `systemctl poweroff`;
  a subsequent process check confirmed no QEMU remained. `git diff --check` passed.

Known live GRUB syntax warnings remain in serial output despite successful boot.
Fresh installation/disk-only boot of this particular ISO, physical USB boot,
Secure Boot, hardware gaming and Windows/Fedora/UjwalOS triple boot are NOT
validated. Shared EFI-partition coexistence requires separate review because
installed Fedora identity is retained. No host partitions, boot entries, packages
or USB devices were altered. This is a local engineering image, not a public release.

## 2026-09-29 - Stage 7 started: artifact integrity and recovery protocol

Owner authorized starting Stage 7. Added [requirements and acceptance gates](recovery-and-quality.md)
for updates, failed-update recovery, older-kernel/rescue paths, dual-boot review,
accessibility and repeated hardware tests. All operational gates remain pending;
this does not complete Stages 3-6 or authorize public release.

`scripts/release/artifacts.py` creates/verifies local unsigned engineering JSON
manifests with SHA-256, size and an operator-supplied full source revision. It
rejects duplicate fields/names, unsafe paths, malformed schemas, symlinks and
non-regular artifacts, detects files changing during hashing, bounds memory use,
and refuses manifest overwrite. It does not attest provenance, sign, upload,
approve a release or prove recovery. An interrupted manifest write can leave an
invalid manifest; the guide requires inspection and fresh staging in that case.

`python3 -m unittest discover -s tests/config -v`: 35 passed, including eight new
artifact tests for round trip, tampering/missing files, traversal, duplicates,
revision/schema validation, symlink/FIFO refusal, overwrite protection, manifest
size limits and CLI exit status. `git diff --check`: passed.

The new `fingerprint` function was also invoked read-only via `runpy.run_path`
against `out/build-ikTd4NhE/result/UjwalOS-0.1.x86_64-44-0.iso`. It returned
3,788,128,256 bytes and SHA-256
`1861207ad9ed51eab00f6d54b2ad4dcd6c9618ef6c7b86a6cc36860196880e0a`,
matching the recorded build. No manifest was retroactively attributed to the
current source revision for this older image.

The update guidance was checked against DNF5 upstream upgrade/offline docs on
2026-09-29. Fedora's GRUB quick-doc page was blocked during review; no unverified
version-specific repair commands are included. No host package, disk, boot or
service changes were made. No ISO build, VM update/recovery, accessibility or
hardware testing was performed for this milestone.

## 2026-09-29 - Native pairing delegation safety correction

Follow-up review found that KDE Connect's `requestPairing` can accept an inbound
request that arrives after our state check. The previous 0.1-2 implementation
therefore could not guarantee its claimed inbound-acceptance boundary. Direct
pair/accept/cancel calls are now blocked; the panel explicitly opens KDE Connect's
native UI instead. `cancelPairing` also changes state unconditionally, so the
planned direct cancel/reject controls were not added. Native UI behavior still
requires real-phone testing; this change removes our extra check-then-call path.

The fixed-command launcher uses no shell or device arguments, reports launch
failure, and clears stale rows. Refresh alone remains non-activating; explicitly
opening KDE Connect may activate its service. Confirmed, revalidated online or
offline unpair requests remain available. `ujwalos-apps` is now 0.1-3.

Verification commands/results:

- `python3 -m unittest discover -s tests/config -v`: 27 passed, including
  RPM build checks and blocking direct pairing before any D-Bus import/call.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software
  out/stage4-venv/bin/python -m unittest discover -s tests/ui -v`: 13 passed;
  also 13 passed with `QT_SCALE_FACTOR=2`. Launcher success/failure is mocked;
  no host service or phone was activated. UI tests exercise the launcher button,
  unpair consent, busy guards and refusal of direct pairing workers.
- `dbus-run-session -- out/stage4-venv/bin/python
  tests/integration/test_phone_transport.py -v`: two passed on a private bus,
  including a synthetic paired-to-unpaired transition and unknown-property error.
- `git diff --check`: passed. Narrow 200% screenshot inspected in
  `out/stage5-native-ui-2x/phone-420.png`.

Source verification on 2026-09-29:
[v26.08.1 pairing handler](https://github.com/KDE/kdeconnect-kde/blob/v26.08.1/core/backends/pairinghandler.cpp)
and [native app launcher](https://github.com/KDE/kdeconnect-kde/blob/master/app/org.kde.kdeconnect.app.desktop).
No new ISO, VM or hardware test was run. The existing ISO still contains 0.1-1;
Stage 5 and remaining Stage 3/4 gates are not complete.

## 2026-09-29 - Stage 5 pairing-request controls

Added explicit pair/unpair confirmation dialogs and fresh device-state checks.
Offline paired devices can request revocation. Pending or inbound requests block
new pair requests; inbound acceptance and cancellation remain in KDE Connect.
The panel displays public verification codes for pending requests and does not
read private keys, change plugin settings, persist identifiers or activate the
service. A sent request is not reported as completed pairing or revocation;
transport failures require a refresh before retrying.

`ujwalos-apps` release is now 0.1-2. The existing ISO remains 0.1-1 and has not
been rebuilt. Real-phone acceptance, new-package live/installed testing and
Stage 3/4 outstanding gates remain open. No host or phone settings were changed.

Verification:

- `python3 -m unittest discover -s tests/config -v`: 26 passed, including
  the RPM build/integration checks and five new pairing backend tests.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software
  out/stage4-venv/bin/python -m unittest discover -s tests/ui -v`: 11 passed.
  Repeated with `QT_SCALE_FACTOR=2`: 11 passed. Coverage includes confirmation
  cancellation/acceptance, duplicate-action prevention and uncertain failures.
  A dialog implicit-height binding warning was fixed before the passing runs.
- `dbus-run-session -- out/stage4-venv/bin/python
  tests/integration/test_phone_transport.py -v`: two passed on an isolated bus.
  Synthetic populated-service tests exercise real Qt property decoding, void
  method replies and unknown-method errors; they do not establish real-phone
  compatibility. Missing-service tests verify no activation.
- Synthetic screenshots in `out/stage5-pairing-ui-2x/` include narrow-window
  confirmation rendering at 200% scale; manually inspected.

Interface evidence: [KDE Connect v26.08.1 device header](https://github.com/KDE/kdeconnect-kde/blob/v26.08.1/core/device.h),
checked 2026-09-28. This is the version packaged in the existing image.

## 2026-09-28 - Current-apps ISO built and live-tested

`scripts/build/build-iso.sh` completed in `out/build-ikTd4NhE` with wrapper
exit 0 and guest `result/result.code` 0. The resulting ISO is
`out/build-ikTd4NhE/result/UjwalOS-0.1.x86_64-44-0.iso`, 3,788,128,256 bytes.
SHA-256: `1861207ad9ed51eab00f6d54b2ad4dcd6c9618ef6c7b86a6cc36860196880e0a`.
The manifest includes `ujwalos-apps` 0.1-1.fc44, `ujwalos-branding` 0.4-1.fc44,
`ujwalos-gaming-setup` 0.1-1.fc44, PySide6 6.11.2-1.fc44 and KDE Connect
26.08.1-1.fc44. EROFS compression and SELinux file contexts completed.

`scripts/test/test-iso.sh
out/build-ikTd4NhE/result/UjwalOS-0.1.x86_64-44-0.iso --check-only` passed
SHA-256, ISO9660 and UEFI catalog checks. The `--headless` invocation created
`out/vm-bLNLCaDo` with KVM, 4 GiB RAM, two vCPUs and a private 40 GiB disk.
That process disappeared during a session interruption. After checking that no
QEMU process remained, `bash out/vm-bLNLCaDo/qemu-command.sh` restarted the
same live test. The guest media check passed (`desktop.png`), branded Plasma
booted (`live2.png`), and both packaged desktop launchers worked:

- Gaming Center opened (`gaming.png`) and saved a requested GameMode profile
  (`gaming-saved.png`). No performance mode was applied or claimed.
- Phone Panel opened (`phone.png`). Refresh reached the real KDE Connect
  service's empty-device result, "No devices found" (`phone-refreshed.png`).
  This tests the empty device list only, not properties from a paired phone.
- `rpm -q ujwalos-apps python3-pyside6 kde-connect` showed the expected versions.
  `rpm -V ujwalos-apps` returned 0 (`rpm-verification.png`).

The guest was asked to shut down via `systemctl poweroff`. This is a successful
compose and live-session smoke test, not a fresh installation acceptance test.
Installation of this particular ISO, real phones, game/hardware performance,
Secure Boot and the remaining Stage 4/5 features are still untested or incomplete.

## 2026-09-28 - Current-apps ISO packaging

Added `ujwalos-apps` 0.1-1, containing the Stage 4 profile editor, Stage 5
read-only phone panel and two desktop launchers. Only application files under
`/usr/share` are installed; no scriptlets, autostart, home-directory writes or
privileged helper. The KDE image explicitly resolves Fedora's `python3-pyside6`
and `qt6-qtdeclarative`, with `kde-connect` already selected. Development wheels
and virtual environments are not copied into the image.

`python3 -m unittest discover -s tests/config -v`: 21 passed, including the
real apps RPM build, dependency/file checks and generated-image integration.
The nine offscreen Qt tests passed. Both desktop files passed
`desktop-file-validate` (Gaming Center has a non-fatal multiple-category hint).
`scripts/build/build-iso.sh --validate` passed in `out/build-xmJPC7Eu`.

The first compose, `out/build-astc1nKz`, has no ISO. After the session interruption,
its execution handle and builder process were absent; `result.code` is 1 and
logs end during package downloads without an established cause. A fresh isolated
compose was started in `out/build-ikTd4NhE`. No completion or boot is inferred
from the package/description checks above. Build results are recorded separately.

## 2026-09-28 - Stage 5 read-only phone panel started

Owner requested Stage 5 while Stage 3 acceptance and Stage 4 implementation
remain open. [Requirements and real-device gates](phone-panel.md) are recorded.
`apps/phone-panel/` adds a user-run Qt/QML panel with explicit refresh, device
pairing/reachability snapshots and optional battery values. The adapter uses
KDE Connect's session D-Bus interface, bounded background queries and no service
activation. Unknown battery remains unavailable; failed refresh clears old data.
Names are plain text and no device IDs, pairing keys or phone content are logged
or persisted. No host packages, firewall rules or phone settings were changed.

Verification commands/results:

- `python3 -m unittest discover -s tests/config -v`: 21 passed, including seven
  phone-backend tests for read-only calls, offline/unpaired devices, malformed
  values, path validation and missing service/plugin handling.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software
  UJWALOS_UI_SCREENSHOTS=out/stage5-ui out/stage4-venv/bin/python
  -m unittest discover -s tests/ui -v`: nine passed, including four phone-panel
  tests for idle privacy, stale-data clearing, worker failure and QML rendering.
- The Qt suite with `QT_SCALE_FACTOR=2`: nine passed.
- `dbus-run-session -- out/stage4-venv/bin/python
  tests/integration/test_phone_transport.py -v`: one passed. Private-bus socket
  creation initially failed inside the sandbox; the authorized isolated-bus
  run verified missing-service failure and no KDE Connect service activation.
- `git diff --check`: passed. Synthetic screenshots at 720x520 and 420x340 were
  generated; the narrow view was inspected for wrapping and plaintext names.

`kdeconnect-cli --help` reports command not found on this host. No actual
KDE Connect success path, Android device, pairing, revoke, reconnect or phone
permission test was performed. Pairing controls, notifications, clipboard and
file transfer remain unimplemented. No Stage 5 RPM/image was built, and no VM
boot/install or hardware acceptance is claimed. Next verify the adapter against
the image's KDE Connect service, then add explicit pairing and revocation.

## Stage 3 summary - implementation complete; testing pending

The optional gaming-setup implementation is complete: packaged launcher,
explicit Fedora-tools installation, optional Steam installation from an already
enabled repository, diagnostics, ISO integration and recorded VM installation
checks. Remaining acceptance tests are the Steam/Proton game matrix, stock
Fedora KDE baseline comparisons, physical GPU and controller checks, and
physical-hardware performance-tool validation. The full Stage 3 gate remains
open until these tests pass. This status does not claim an implemented NVIDIA
driver installer or tested compatibility. Stage 4 implementation is underway.

This wording separates implementation completion from acceptance completion;
the dated evidence and limitations below remain unchanged. Documentation-only
update: `git diff --check` passed; no new build or runtime tests were performed.

## 2026-09-28 - Stage 4 Qt profile editor

Implemented `apps/gaming-center/main.py` and `Main.qml`: unprivileged Qt/QML
profile create/edit/save, confirmed deletion, local reset, launch-option preview
and read-only tool availability. Invalid input and storage errors are visible;
corrupt storage disables editing instead of replacing data. QLockFile prevents
concurrent editor instances. Missing theme icons fall back to text. The UI
does not launch processes, apply Steam options or change system settings.

Verification:

- `python3 -m unittest discover -s tests/config -v`: 14 passed.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software out/stage4-venv/bin/python
  -m unittest discover -s tests/ui -v`: five passed, including real QML load/save,
  CRUD persistence, failed-save preservation, corrupt storage and lock exclusion.
- The same Qt command with `QT_SCALE_FACTOR=2`: five passed.
- Screenshots at 840x600 and 560x500 inspected in `out/stage4-ui/`; missing icons
  found and fixed with text fallbacks. No QML warnings in the final smoke test.
- `git diff --check`: passed.

Dependencies were downloaded only into `out/stage4-venv` after the sandbox's
network lookup failed; PySide6-Essentials and shiboken6 versions are 6.11.2.
No host system packages changed. This is development evidence, not Fedora RPM
dependency/license clearance, Plasma/Wayland acceptance or a new ISO result.
System monitoring, privileged integration and crash/reboot restoration remain
unimplemented. Stage 3 implementation/ISO/installation evidence remains valid,
but its game/baseline, physical graphics and controller gates remain untested;
the phase cannot yet be truthfully reported as fully complete.

## 2026-09-28 - Stage 4 profile backend started

The owner requested the next phase. Requirements and acceptance gates are in
[gaming-center.md](gaming-center.md); Stage 3 is not marked complete.
`apps/gaming-center/profiles.py` now validates per-game requested settings,
generates fixed GameMode/MangoHud launch-option previews, resets local requested
values, and reads/writes versioned JSON with private temporary files and atomic
replacement. It executes no commands and makes no system or Steam changes.
Malformed/unknown documents are rejected without rewriting them. Multiple UI
instances and power-loss durability are not validated by this backend milestone.

`python3 -m unittest discover -s tests/config -v` exited 0: 14 tests passed,
including seven new tests covering validation, reset, fixed command tokens,
private save permissions, round-trip persistence, duplicate rejection and
preservation of the old file when replacement fails. `git diff --check` exited 0.

No Qt frontend, helper or runtime monitoring is implemented. PySide6 is absent
on the host; no host packages were installed. No Stage 4 RPM/ISO, VM boot,
installation or hardware test was performed. The next bounded milestone is
the unprivileged Qt/QML profile editor and read-only status adapter.
The goal tracker refused a new goal while Stage 3 remains unfinished; the new
requirements are recorded in the repository rather than falsely completing it.

## 2026-09-28 - Stage 3 gaming foundation in progress

The new `ujwalos-gaming-setup` 0.1-1 RPM packages a user-run terminal setup
wizard and KDE application launcher. It offers an explicit PolicyKit-authorized
DNF5 transaction for Fedora's `gamemode`, `mangohud`, `gamescope` and
`vulkan-tools`; a separate Steam transaction is available only from an already
enabled repository after another explicit confirmation. The wizard reports
graphics, Vulkan and joystick-device status. It does not bundle games, Steam,
Proton or proprietary drivers, alter user preferences, or enable repositories.
The source and redistribution boundary is documented in
[gaming-setup.md](gaming-setup.md).

| Gate | Current evidence |
| --- | --- |
| Setup code and RPM | PASS: `scripts/build/build-gaming-rpm.sh out/stage3-gaming-check` built `ujwalos-gaming-setup-0.1-1.fc44.noarch.rpm`; `prepare-description.py` adds it only to the KDE live profile |
| KIWI description validation | PASS: `scripts/build/build-iso.sh --validate`, `out/build-EFhgGr52/description-validation.log` |
| Repository tests | PASS: `python3 -m unittest discover -s tests/config -v`, 7 tests including fixed install command, explicit Steam confirmation and VM memory bounds |
| Stage 3 ISO | PASS: `out/build-dXo1VHow/result/UjwalOS-0.1.x86_64-44-0.iso`, wrapper and guest exit 0, gaming RPM in manifest, media integrity passed |
| Candidate RPM in installed VM | PASS: installed in existing Stage 2 Fedora KDE VM `out/vm-St43Uqg6`; plan/status worked and absent Steam/GameMode paths failed without installing anything |
| Stage 3 live boot and setup | PASS: `out/vm-ck8RbgAm` reached Plasma; KDE launcher opened wizard; optional Fedora tools transaction completed in live VM |
| Stage 3 fresh install and disk-only boot | PASS: `out/vm-m1CAtNu1`, fresh 40 GiB disk, Anaconda success, ISO detached, first-run setup and branded Plasma login; installed gaming RPM verification exit 0 |
| Installed setup authorization cancellation | PASS: normal-account PolicyKit prompt names the fixed DNF transaction; cancellation returns to the wizard menu and optional packages remain absent |
| Steam/Proton and game matrix | Not tested; stock Fedora KDE baseline still required |
| Physical graphics and controller tests | Not tested |

Read-only host inventory on 2026-09-28 showed Intel Raptor Lake-P UHD
graphics and an NVIDIA RTX 3050 6GB laptop GPU. `rpm -q` found GameMode
1.8.2-4.fc44 installed on the host, but no Steam, MangoHud, Gamescope or
Vulkan tools; no joystick device node was present. No host packages were
installed or changed by this work. This inventory is not a hardware validation
result for the UjwalOS image.

`gaming/root/usr/bin/ujwalos-gaming-setup --status` ran as an unprivileged
user and reported the same package/GPU inventory and no joystick nodes.
`desktop-file-validate gaming/root/usr/share/applications/ujwalos-gaming-setup.desktop`
exited 0. `rpm -qplv` showed only the executable setup script and one launcher;
`rpm -qp --scripts` showed no scriptlets. The candidate RPM SHA-256 is
`3848b4f3460c8ee23d4de85ece9fd7835bf3599c8830459f978cc3c4c3d5a760`.
The package was included in the validated KIWI description. At the failed
compose check, `/proc/meminfo` reported about 3.8 GiB available and the wrapper
required 7 GiB for its 6 GiB builder. This was a host resource gate; the builder
VM did not launch. After shutting down the test VM, available memory rose to
about 7.8 GiB and the fresh compose completed. No host packages were changed.

`scripts/build/build-iso.sh` accepted `out/build-dXo1VHow` with wrapper
`exit-code` 0 and guest `result/result.code` 0. Its ISO is
`result/UjwalOS-0.1.x86_64-44-0.iso` (3,791,642,624 bytes; SHA-256
`b4110546036fdb87813dc35de25d447cc5e2032821278fa0ed28a1795a71855c`).
The package manifest lists `ujwalos-gaming-setup|0.1|1.fc44|noarch` and
`ujwalos-branding|0.4|1.fc44|noarch`.
`scripts/test/test-iso.sh out/build-dXo1VHow/result/UjwalOS-0.1.x86_64-44-0.iso
--check-only` passed SHA-256, ISO9660 and UEFI catalog checks. The first live
QEMU launch hit a sandbox Unix-socket bind denial; the second launch, under the
approved VM permission, booted the same ISO in `out/vm-ck8RbgAm`.

The live VM reached the branded Plasma desktop (`stage3-desktop.png`), the KDE
launcher found "UjwalOS Gaming Setup" (`stage3-launcher.png`), and clicking it
opened the interactive wizard in Konsole (`stage3-wizard.png`). Choice 2 invoked
PolicyKit/DNF5. DNF showed a 10-package transaction and waited for confirmation
(`stage3-tools-transaction.png`). After confirmation, it installed `gamemode`,
`mangohud` and `gamescope` with dependencies; `vulkan-tools` was already
installed. DNF reported `Complete!` and the wizard returned to its menu
(`stage3-tools-result.png`). Choice 5 ran `gamemoded -t`: basic checks passed,
but its CPU-governor feature check failed because the VM exposes no CPU
governor files (`stage3-gamemode.png`). Its recorded `qemu-command.sh` uses
`-accel kvm -cpu host`; this is CPU virtualization with software-rendered
graphics, not TCG CPU emulation. This is not a GameMode validation
pass on physical hardware. The VM was cleanly shut down. No game was launched,
and this live-boot test is not a fresh installation test.

The existing Stage 2 installed Fedora KDE VM was booted with
`UJWALOS_VM_MEMORY_MIB=2048 scripts/test/test-iso.sh --installed
out/vm-St43Uqg6 --headless`. `sudo rpm -Uvh /tmp/ujwalos-gaming-setup.rpm`
installed the candidate RPM successfully (`stage3-install-result.png`).
`rpm -q ujwalos-gaming-setup` and `ujwalos-gaming-setup --plan` completed;
`--status` found software Vulkan rendering through llvmpipe and a virtual
joystick node (`stage3-status.png`). `--install-steam` found no `steam` package
in enabled repositories and exited 1 without adding a repository or package;
`--test-gamemode` reported the optional tools absent and exited 1
(`stage3-optional2.png`). The VM was cleanly powered off. This verifies the
candidate RPM on an installed guest, not its inclusion in a new ISO, a Steam
transaction, physical GPU acceleration or real controller input.

### Stage 3 fresh installation and authorization check

On 2026-09-28, `scripts/test/test-iso.sh
out/build-dXo1VHow/result/UjwalOS-0.1.x86_64-44-0.iso --headless` created
`out/vm-m1CAtNu1` with a fresh 40 GiB private disk, 4096 MiB RAM, two virtual
CPUs, KVM and Virtio VGA. The initial retry process disappeared before
installation began; after confirming its process handle was missing, its
socket refused connections and no QEMU process remained, it was restarted
with `bash out/vm-m1CAtNu1/qemu-command.sh`. Anaconda's review screen selected
only the Virtio disk (`review.png`). It completed the installation and showed
"Successfully installed" (`progress8.png`). The live session shut down cleanly.

`scripts/test/test-iso.sh --installed out/vm-m1CAtNu1 --headless` then booted
the same disk with no CD-ROM in the recorded QEMU command. Plasma first-run
setup created the disposable `stg3test` account (`setup7.png`); login reached
the branded desktop (`installed-desktop.png`). In that account:

```sh
rpm -q ujwalos-gaming-setup ujwalos-branding
rpm -V ujwalos-gaming-setup
ujwalos-gaming-setup --plan
```

The versions were `ujwalos-gaming-setup-0.1-1.fc44.noarch` and
`ujwalos-branding-0.4-1.fc44.noarch`. RPM verification returned 0 without
reporting file differences, and the plan displayed its expected optional
packages and launch options (`installed-rpm.png`). Running the interactive
wizard and selecting choice 2 opened a PolicyKit password prompt naming
`/usr/bin/dnf5 install gamemode mangohud gamescope vulkan-tools`
(`installed-polkit.png`). Cancelling it reported that installation did not
complete and returned to the menu (`installed-cancel.png`). After exiting the
wizard, `rpm -q gamemode mangohud gamescope steam` confirmed all four remained
absent (`cancel-packages.png`). The installed VM shut down via
`systemctl poweroff`, and QEMU exited 0.

The earlier attempt in `out/vm-CDsyeKOE` stopped unexpectedly at 35% of the
software-copy stage: wrapper exit 143, empty QEMU stderr, refused QMP socket.
Its partial disk is retained. The termination cause was not established, and
that attempt is not counted as a successful installation. The successful
retry above used a different disk. No physical disks or host packages changed.

Controller protocol coverage was expanded from device-node detection to
per-game mapping, rumble and reconnect checks, with Valve source links and a
verification date in `gaming-setup.md`. Those controller tests and the actual
game/baseline matrix remain unrun. This update changes documentation only;
the seven passing repository tests recorded above apply to the unchanged code.
`git diff --check` exited 0 for this documentation update.

## 2026-09-28 - Stage 2 desktop identity complete

The `ujwalos-branding` 0.4-1 noarch RPM contains an original Himalayan dusk
wallpaper, a Plasma global theme with first-run panel, launcher favorites and wallpaper layout,
Plasma Login Manager wallpaper configuration, and a Plymouth two-step theme
with original indicator, prompt and wordmark assets. The package installs only
system files; no home directory files, package scriptlets or recurring
preference-reset scripts are included. The generated live `config.sh` installs it into the
disposable image root and selects the Plymouth theme, and now restricts that
installation to the `KDE-Desktop-Live` profile; the GRUB `blsdir` cleanup still
applies to every live profile. The image still uses Fedora KDE and RPM updates.

| Gate | Current evidence |
| --- | --- |
| Package code written | PASS: `packaging/ujwalos-branding.spec` 0.4-1, `branding/root/` |
| RPM built | PASS: `out/build-4MOSl8sm/rpmbuild/RPMS/noarch/ujwalos-branding-0.4-1.fc44.noarch.rpm`, built by `prepare-description.py` inside the run directory |
| KIWI description validated | PASS: `scripts/build/build-iso.sh --validate`, `out/build-hLBYHE0T/` |
| Stage 2 ISO built | PASS: `out/build-4MOSl8sm/`, wrapper and guest exit 0, `SHA256SUMS` and `iso-path.txt` present. 3,791,638,528-byte ISO, SHA-256 `261b3a9f24f597ba28391d6684d93cb7fc4728fffa4343c3ce75ae5d3b5f0703`. Manifest lists `ujwalos-branding 0.4-1.fc44`. |
| Stage 2 live boot | PASS: `out/vm-EmDO1nQz` booted the 0.4-1 ISO, visibly rendered the UjwalOS Plymouth splash, and reached the branded Plasma live desktop. |
| Stage 2 install / installed login | PASS: Anaconda reported successful installation; the same VM booted its private disk with the ISO detached, completed first-run setup, and reached a branded login and Plasma desktop. |
| New-account defaults / existing-account update | PASS in `out/vm-St43Uqg6`: new account received wallpaper and bottom panel; after downgrading the RPM to 0.2-2, the account selected the Fedora wallpaper, upgraded to 0.3-1, and retained the wallpaper and panel configuration through reboot and login. |
| Installed Plymouth splash | PASS in `out/vm-St43Uqg6`: 0.4-1 was installed, the initramfs was regenerated, and a disk-only reboot visibly rendered the UjwalOS ring, wordmark and background. |
| Hardware | Not tested |

All Stage 2 gates pass. Hardware and broader release qualification remain for
later stages; this is not a public release.

### Final 0.4-1 image

`scripts/build/build-iso.sh` accepted `out/build-4MOSl8sm` with wrapper
`exit-code` 0 and guest `result/result.code` 0. The ISO is
`result/UjwalOS-0.1.x86_64-44-0.iso` (3,791,638,528 bytes, SHA-256
`261b3a9f24f597ba28391d6684d93cb7fc4728fffa4343c3ce75ae5d3b5f0703`).
Its package manifest lists `ujwalos-branding|0.4|1.fc44|noarch`.
`scripts/test/test-iso.sh out/build-4MOSl8sm/result/UjwalOS-0.1.x86_64-44-0.iso
--check-only` passed SHA-256, ISO9660 and UEFI catalog checks.
`python3 -m unittest discover -s tests/config -v` passed all 5 tests; `bash -n
scripts/build/build-iso.sh scripts/build/build-branding-rpm.sh
scripts/build/generate-plymouth-prompts.sh scripts/test/test-iso.sh` and
`git diff --check` exited 0.

`out/vm-EmDO1nQz` then booted that exact ISO. Recorded frame
`stage2-live-0020.png` shows the UjwalOS boot wordmark on the intended dark
background; later frames show the Himalayan wallpaper and the complete live
Plasma desktop. This is a live-boot check, not a second installation test. The
0.3-1 image had already passed a fresh blank-disk installation and installed
login test, and the 0.4-1 branding RPM was separately verified in that
installed VM before this final compose.

### Plymouth fallback diagnosis and 0.4 VM verification

On 2026-09-27, an installed boot frame capture of `out/vm-St43Uqg6`
showed Fedora's gray fallback dots even though `plymouth-set-default-theme`
reported `ujwalos`, `/etc/plymouth/plymouthd.conf` selected it, and the active
initramfs contained the theme and `two-step.so`. A manual Plymouth preview
with `sudo plymouthd --debug --debug-file=/tmp/plymouth-debug.log
--tty=/dev/tty4` and `sudo plymouth --show-splash` reproduced the fallback.
The debug log shows `two-step` loading the UjwalOS theme, failing at
`show_splash_screen: loading lock image` with `No such file or directory`,
then loading the distribution `bgrt` theme. This is an asset omission, not a
theme-selection problem. Evidence is in
`out/vm-St43Uqg6/theme-transition.png` and `plymouth-preview.png`.

`ujwalos-branding` 0.4-1 adds original `lock.png`, `entry.png`, and
`bullet.png` prompt sprites for Plymouth's two-step plugin, generated by
`bash scripts/build/generate-plymouth-prompts.sh
branding/root/usr/share/plymouth/themes/ujwalos`. The RPM was built with
`bash scripts/build/build-branding-rpm.sh out/stage2-fix` and upgraded inside
the same disposable installed VM using `sudo rpm -Uvh
/tmp/branding-0.4.rpm`; the package transaction passed. A new manual preview
rendered the UjwalOS background and wordmark
(`out/vm-St43Uqg6/plymouth-fix-preview.png`). After `sudo dracut -f`,
`sudo lsinitrd /boot/initramfs-7.2.7-200.fc44.x86_64.img` listed all three
sprites (`initrd-sprites.png`). A disk-only reboot then visibly rendered the
teal progress ring, UjwalOS wordmark, and intended dark background
(`fixed-boot-0060.png`) before the branded login. The fresh 0.4 ISO build and
live boot are recorded in the preceding section.

The manual `dracut -f` was performed only inside the disposable VM. The
branding RPM has no scriptlets and does not rebuild an existing installation's
initramfs on package update; a later normal kernel/initramfs regeneration is
needed for the new splash assets to take effect on that path. No host boot
settings, packages, or disks were changed.

### Existing-account update preservation

Inside the installed `out/vm-St43Uqg6` VM, `curl -fLo /tmp/old.rpm
http://10.0.2.2:8123/ujwalos-branding-0.2-2.fc44.noarch.rpm` downloaded the
previous package from the local test server. `sudo rpm -Uvh --oldpackage
/tmp/old.rpm` installed 0.2-2. As `stg2test`,
`plasma-apply-wallpaperimage /usr/share/wallpapers/Fedora/` changed the
wallpaper visibly (`custom-before.png`). `sha256sum
~/.config/plasma-org.kde.plasma.desktop-appletsrc` recorded
`ed56d206e1c584faa527d5e2f7e123c26c4d59b996e793548a506954204178b2`.
The installed `plasma-apply-wallpaperimage --help` confirmed that it accepts an
installed wallpaper package path.

`curl -fLo /tmp/new.rpm
http://10.0.2.2:8123/ujwalos-branding-0.3-1.fc44.noarch.rpm` and
`sudo rpm -Uvh /tmp/new.rpm` completed successfully (`update-result.png`).
`rpm -q ujwalos-branding` then reported `0.3-1.fc44.noarch`, and the per-user
Plasma configuration hash remained exactly the same (`update-verified.png`).
After `systemctl reboot` and login, the Fedora wallpaper and bottom panel were
still visible (`post-reboot-desktop.png`). This tests one customized account
and one package update path in a VM; it does not prove every Plasma preference
or hardware configuration.

### Corrected 0.3-1 image and installation (superseded)

`scripts/build/build-iso.sh` accepted `out/build-8bD6L764` with wrapper
`exit-code` 0 and guest `result/result.code` 0. The ISO is
`result/UjwalOS-0.1.x86_64-44-0.iso` (3,791,599,616 bytes, SHA-256
`18f1b66d3579d25b43cea4c9437885979c7a7b8860310b94848f22ad4b1417da`).
The package manifest lists `ujwalos-branding|0.3|1.fc44|noarch`. On 2026-09-27,
`scripts/test/test-iso.sh out/build-8bD6L764/result/UjwalOS-0.1.x86_64-44-0.iso --check-only`
passed SHA-256, ISO9660 and UEFI catalog checks. `python3 -m unittest discover
-s tests/config -v` passed all 5 tests; `bash -n
scripts/build/build-iso.sh scripts/build/build-branding-rpm.sh
scripts/test/test-iso.sh` and `git diff --check` exited 0.

`out/vm-St43Uqg6` booted that ISO and Anaconda showed "Successfully installed"
(`current.png`). `scripts/test/test-iso.sh --installed out/vm-St43Uqg6 --headless`
then booted its 40 GiB file-backed disk without the ISO. Fedora first-run setup
created `stg2test`; the login screen displayed the packaged UjwalOS wallpaper
(`login.png`), and the new account's first desktop displayed that wallpaper and
the bottom panel (`desktop.png`). `rpm -q ujwalos-branding` inside the account
reported `ujwalos-branding-0.3-1.fc44.noarch` (`rpm-before.png`). The live
session was terminated after Anaconda completion to detach the ISO. No host
disk or boot setting was changed.

At this earlier checkpoint, the generated live initrd contained and selected
the UjwalOS Plymouth theme, but the installed splash had not yet been proven.
That gap is closed by the 0.4-1 evidence above. Hardware remains untested. The
upstream Fedora first-run and Welcome Center screens remain visible.

`python3 -m unittest discover -s tests/config -v`: 5 tests pass. They cover the
RPM file inventory (including the watermark and prompt sprites), the absence of package
scriptlets and of `/home/` or `/root/` paths, the generated image script with
both profile gates, and the ISO/QEMU refusal paths. `bash -n
scripts/build/build-iso.sh scripts/build/build-branding-rpm.sh
scripts/test/test-iso.sh` and `git diff --check`: exit 0. The earlier first RPM
attempt failed because `rpmbuild` chose sandboxed `/var/tmp`;
`build-branding-rpm.sh` now directs all RPM temporary files into its fresh
output directory. No host packages or boot settings were changed.

### Accepted Stage 2 build

`scripts/build/build-iso.sh` produced an accepted 0.2-2 image in
`out/build-3UNby9k7`. Started 14:58, guest finished 15:27.

- Wrapper `exit-code` 0, guest `result/result.code` 0.
- `result/SHA256SUMS`, `iso-path.txt` and `builder-inputs.sha256` all present,
  so unlike `out/build-Axnn4fY0` this run reached wrapper-level acceptance.
- Artifact `out/build-3UNby9k7/result/UjwalOS-0.1.x86_64-44-0.iso`,
  3,791,595,520 bytes, SHA-256
  `30a7fe8e603e99ad6dc0dcb036eaf19a0a53486f3be2c052efc5b22c9ebc8d25`.
  Re-verified after the fact with `sha256sum -c SHA256SUMS`: `OK`.
- `UjwalOS-0.1.x86_64-44-0.packages` lists
  `ujwalos-branding|0.2|2.fc44|noarch`.
- `result/result.log` shows `+ plymouth-set-default-theme ujwalos` succeeding
  and dracut including the `plymouth` module, so the boot theme was selected in
  the image root.

### Stage 2 live boot, partial

`out/vm-2mGTBmPY` booted the 3UNby9k7 ISO headless via
`scripts/test/test-iso.sh ... --headless` (launched 15:29) and reached a Plasma
desktop. Observed, from the recorded frames:

- UjwalOS Himalayan-dusk wallpaper applied, replacing the stock Fedora image.
- Panel at the bottom with the packaged launcher favorites row
  (`out/vm-2mGTBmPY/panel-left.jpg`).
- krunner search opened and functional (`krunner2.png`).
- Installer launched to its first screen (`anaconda1.png`).
- GRUB offered `Start UjwalOS-0.1`, `Test this media & start UjwalOS-0.1` and
  `Troubleshooting` (`boot/frame-01.png`). The boot menu is intentionally
  unbranded; the branding package does not touch GRUB templates.
- Stock "Welcome to Fedora Linux!" Welcome Center still present in the live
  session. Re-branding the live-session welcome flow is out of Stage 2 scope
  and is not recorded as a pass.

Limits of that run, stated explicitly:

- No installation was performed. `disk.qcow2` was still 197,248 bytes, so the
  target disk was untouched and there is no installed system.
- The session was the live user, whose shell configuration already existed.
  This shows the packaged defaults render, but it does **not** show that a new
  account inherits them, which is the actual Stage 2 gate.
- The Plymouth splash was not captured. The frame burst began after the
  desktop was already up; the theme's appearance on a real boot is unverified
  even though the theme is installed and selected.
- The VM was left running and idle at "Display output is not active"
  (`current.png`, 15:50). It held the `disk.qcow2` write lock.

### Wrapper aborted after a successful compose

Superseded by `out/build-3UNby9k7` above; retained because it explains why that
run was repeated. `out/build-Axnn4fY0` is not a compose failure. The guest wrote `Box build done`
with `result.code` 0, and the resulting package manifest lists
`ujwalos-branding 0.2-1.fc44` together with the stock
`plasma-login-manager 6.7.5`, `plasma-workspace 6.7.5`,
`plymouth`/`plymouth-plugin-two-step` 24.004.60 and `kde-connect 26.08.1`
(2212 packages). The wrapper process, started at 14:20, was edited at 14:21:46
(the `rpmbuild` tool check). Bash re-reads an executing script, so the shifted
byte offsets produced
`scripts/build/build-iso.sh: line 89: unexpected EOF while looking for matching '"'`
followed by `FAILED (2)`. The script itself is valid: `bash -n` exits 0 and all
5 repository tests pass. Because the wrapper exited before its checksum step,
`result/SHA256SUMS`, `iso-path.txt` and `exit-code` are absent, and
`test-iso.sh --check-only` refuses that ISO by design. Do not edit the wrapper
while a compose is running; wait for exit or execute a copy of it.

Upstream sources checked 2026-09-27: [KDE Plasma first-run scripting](https://develop.kde.org/docs/plasma/scripting/),
[KDE global themes](https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/),
[KDE KConfig cascading defaults](https://develop.kde.org/docs/administration/kiosk/introduction/),
[Plasma Login Manager configuration](https://github.com/KDE/plasma-login-manager#configuration),
[KDE menu defaults](https://develop.kde.org/docs/administration/menu/),
[KIWI overlay behavior](https://osinside.github.io/kiwi/overview/workflow.html),
and the pinned Fedora 44 image's existing theme and login defaults. The
`LicenseRef-UjwalOS-Internal` placeholder needs an owner licensing decision
before redistribution; see `LICENSES/README.md`.

## 2026-09-27 - Successful compose and installation debugging

Stage 1 VM acceptance passed. This is not a release or hardware certification.

| Gate | Current evidence |
| --- | --- |
| Code / description | Implemented; KIWI validation and 5 repository tests pass |
| ISO built | PASS: `out/build-0QH6om9N`, wrapper and guest exit 0 |
| Live UEFI boot | PASS: Plasma, pointer/keyboard input and browser networking |
| Installer / blank-disk installation | PASS: `out/vm-kufXItM3/result.png` |
| Installed disk boot / setup / login | PASS: ISO detached; first-run account setup and Plasma login |
| Restart / second login | PASS: `out/vm-kufXItM3/reboot-desktop.png` |
| Hardware / Secure Boot / gaming / phone | Not tested |

Two bounded generated-description fixes were implemented: disable x86-64
EROFS fragments while retaining LZMA level 6 and 1 MiB clusters, and clear
GRUB's build-only `blsdir` at the end of live-image `config.sh`. A local QMP
Unix socket was added to the test launcher for precise installer input.

- `out/build-jQavkfpi` failed committing an EROFS fragment with
  `mkfs.erofs 1.9.4` (I/O error). A CLI override attempt in
  `out/build-z1T7HOw8` failed because boxed-plugin split the space-containing
  argument. The option is now set in generated `components/liveinstall.xml`.
- `scripts/build/build-iso.sh --validate`: passed in `out/build-36revb6W`
  and, after the GRUB fix, `out/build-FIGIDJis`.
- `scripts/build/build-iso.sh`: first successful ISO in `out/build-ZF7Z22aY`,
  wrapper exit 0 and guest result.code 0. SHA-256:
  `961f0f8623dba26c7435a05356d45c66c9d6bc661d28d6938adbe83018298bb7`.
- `scripts/test/test-iso.sh out/build-ZF7Z22aY/result/UjwalOS-0.1.x86_64-44-0.iso --check-only`:
  passed checksum, ISO9660 and UEFI checks.
- The same command with `--headless` reached Plasma and the installer in
  `out/vm-Cprdo79e` and `out/vm-6a2eEXXf`. Installation to the latter's
  40 GiB file-backed disk completed (`progress-7.png`).
- `scripts/test/test-iso.sh --installed out/vm-6a2eEXXf --headless`:
  FAILED installed boot; GRUB offered only firmware settings. Read-only
  `qemu-img convert`, `sfdisk`, `mtype`, and `debugfs` inspection of copies
  found intact kernels/BLS entries but
  `blsdir=/result/build/image-root/boot/loader/entries`. `dump.erofs` confirmed
  this path originated in the live image, not the installer UI.
- `scripts/build/build-iso.sh`: corrected ISO in `out/build-0QH6om9N`,
  wrapper exit 0 and guest result.code 0. Artifact:
  `out/build-0QH6om9N/result/UjwalOS-0.1.x86_64-44-0.iso`.
  SHA-256: `192b6aee1ab30466cbb6292726e36b714fec8c2f6e2cd979228520766005793a`.
- `scripts/test/test-iso.sh out/build-0QH6om9N/result/UjwalOS-0.1.x86_64-44-0.iso --check-only`:
  passed. `xorriso -osirrox on -indev out/build-0QH6om9N/result/UjwalOS-0.1.x86_64-44-0.iso -extract /LiveOS/squashfs.img out/build-0QH6om9N/live-root.erofs`
  and `dump.erofs --cat --path=/boot/grub2/grubenv out/build-0QH6om9N/live-root.erofs`
  confirmed no `blsdir` remains. Normal and rescue BLS entries are present.
- `scripts/test/test-iso.sh out/build-0QH6om9N/result/UjwalOS-0.1.x86_64-44-0.iso --headless`:
  live Plasma and installer reached in `out/vm-kufXItM3` (`live.png`,
  `wizard.png`, `review.png`). Installation succeeded (`result.png`) on its
  sole 40 GiB QCOW2 disk: EFI, ext4 /boot and Btrfs root/home, no encryption.
  Pointer and keyboard worked; Firefox loaded Fedora Discussion over HTTPS
  (`shutdown.png`). No feedback or other content was submitted.
- `scripts/test/test-iso.sh --installed out/vm-kufXItM3 --headless`:
  PASS. Recorded `qemu-command.sh` has no CD-ROM. First-run setup appeared
  (`installed-boot.png`), a disposable `vmtest` account was created, and login
  reached Plasma (`desktop.png`). A normal desktop Restart returned to login
  (`reboot-login2.png`); second login reached Plasma (`reboot-desktop.png`).
  Final desktop shutdown completed, QEMU exit 0. The VM is stopped.
  The test account exists only on this disposable disk, not in the ISO.
- `python3 -m unittest discover -s tests/config -v`: 5 tests passed.
  `bash -n scripts/build/build-iso.sh scripts/test/test-iso.sh out/build-FIGIDJis/description/config.sh`
  and `git diff --check`: exit 0. The bounded-derivative test also checks the
  entire liveinstall XML tree against upstream with only the x86-64 option
  change, plus the exact generated config.sh change and QMP socket arguments.

All VM disks are disposable files. No host packages, physical disks, host boot
entries or host security settings were changed. Live GRUB syntax warnings were
observed despite successful live boot; they remain a diagnostic follow-up.
No hardware, Secure Boot, gaming or phone validation has been performed.

### Upstream verification

Checked 2026-09-27:

- [KIWI image schema](https://osinside.github.io/kiwi/image_description/elements.html):
  EROFS creation and compression attributes.
- [KIWI script phases](https://osinside.github.io/kiwi/concept_and_workflow/shell_scripts.html):
  `config.sh` executes after package installation during prepare.
- [Fedora BLS behavior](https://fedoraproject.org/wiki/Changes/BootLoaderSpecByDefault):
  default loader entries and boot-relative `blsdir` override.
- [QEMU QMP reference](https://www.qemu.org/docs/master/interop/qemu-qmp-ref.html):
  absolute input events use the range 0 through 0x7fff.
- [EROFS changelog](https://github.com/erofs/erofs-utils/blob/dev/ChangeLog):
  reviewed 1.9.4 history; no claim that it establishes this failure's root cause.

The earlier attempt history below is retained for traceability, not current gate status.

## 2026-09-27 — Stage 1 implementation and compose attempts

The owner explicitly authorized Stage 1 after the fundamentals task.

| Gate | Current evidence |
| --- | --- |
| Description validated | PASS: pinned Fedora 44 derivative passes KIWI schema/profile validation |
| ISO built | Build in progress; no successful ISO yet |
| Live boot tested | Not run |
| Installer launched | Not run |
| Installation / installed boot | Not run |
| Hardware / gaming / phone tests | Not run |

Implemented: pinned upstream archive and builder hashes under image/, minimal
UjwalOS name/package derivative, isolated build entry point, ISO verification and
QEMU launcher with TCG fallback, and documented build/test commands.
No host packages were installed by this task. No host partitions, boot entries,
or physical disks were changed or passed into QEMU.

### Commands and concrete failures

- `scripts/build/build-iso.sh --validate`: exit 0; evidence under
  `out/build-t3HphTF3/description-validation.log`.
- `scripts/build/build-iso.sh`: sandbox network DNS failure; retried with approved
  network access. Evidence: `out/build-aw6AGq8j/`.
- Approved retry: version capture stopped because KIWI 11.0.2's `--version`
  prints its version but exits 1. Fixed by reading Python package metadata.
  Evidence: `out/build-RHvqLfHY/`.
- Retry reached and booted the disposable builder but failed reading
  `/description/repositories/core.xml`: native symlink visibility under mapped
  9p. Fixed by materializing that alias with identical bytes.
  Evidence: `out/build-Q0B1IFZI/result/result.log`.
- Retry failed its media-check prerequisite (`tagmedia` missing). Configured the
  builder's supported `boxroot` hook to select Fedora's `isomd5sum` backend,
  retaining media checking. Evidence: `out/build-JoT2ZhFI/result/result.log`.
- Current retry reached Fedora package resolution/download/installation inside
  the builder. Evidence: `out/build-jQavkfpi/result/result.log`.

The sandbox hides /dev/kvm; the approved build execution has access and uses
KVM. The scripts select software emulation where KVM is actually unavailable.
The disposable builder boot is not a UjwalOS live-image boot test.

### Repository verification

`python3 -m unittest discover -s tests/config -v`: 5 tests pass. They cover
pinned archive integrity, unchanged upstream boot/installer files, the repository
alias workaround, overwrite refusal, shell syntax, invalid ISO/checksum refusal,
and QEMU launch arguments/installed-disk mode using synthetic media and a fake
QEMU process. The fallback test exercises TCG selection in the sandbox; it is
not an emulated OS boot test. `git diff --check`: passed.

`python3 scripts/build/fetch-box.py out/box-cache`: all 3 cached builder artifacts
match pinned SHA-256 values. Builder hashes were added while the current compose
was running; that compose uses those same already-downloaded artifacts.

### Remaining release limits

Fedora RPM repositories/group metadata still move, so no bit-for-bit reproduction
claim is made. Preserve input cache and archive a package/metadata snapshot before
release. Desktop branding remains stock except image/media naming. Secure Boot,
physical hardware, real phone pairing and gaming remain untested. Upstream
installed recovery-menu defaults are retained for this baseline and require a
separate recovery review before public release. Original-code licensing and
Fedora trademark review remain open.

## 2026-09-26 — Fundamentals

Inspected an existing Git repository containing only a short README. Added the
full master specification, architecture decision, security/compatibility/build
and release plans, contributor rules and a read-only preflight. No compose or VM
was run in that setup task. At that time KIWI was missing; it was already
installed when Stage 1 work began. Recorded environment: Fedora 44 Workstation,
x86-64, about 15 GiB RAM and 271 GiB free filesystem space.
