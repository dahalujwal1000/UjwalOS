# Status and unreleased notes

## 2026-09-27 - Stage 2 desktop identity in progress

The `ujwalos-branding` 0.2 noarch RPM now contains an original Himalayan dusk
wallpaper, a Plasma global theme with first-run panel, launcher favorites and wallpaper layout,
Plasma Login Manager wallpaper configuration, and a Plymouth two-step theme
with original indicator frames. The package installs only system files; no
home directory files or recurring preference-reset scripts are included.
The generated live `config.sh` installs it into the disposable image root and
selects the Plymouth theme. The image still uses Fedora KDE and RPM updates.

| Gate | Current evidence |
| --- | --- |
| Package code written | PASS: `packaging/ujwalos-branding.spec`, `branding/root/` |
| RPM built | PASS: generated per build under `out/build-*/rpmbuild/RPMS/noarch/` |
| KIWI description validated | PASS: `scripts/build/build-iso.sh --validate`, `out/build-vBjToPyd/` |
| Stage 2 ISO built | Revision 0.2-1 preview compose running in `out/build-Axnn4fY0/`; result not yet known. Source is now 0.2-2. |
| Stage 2 live boot / install / login | Not yet tested |
| New-account defaults / existing-account update | Not yet tested |
| Hardware | Not tested |

`python3 -m unittest discover -s tests/config -v`: 5 tests pass, including RPM
file inventory and the generated image script. The earlier first attempt failed
because `rpmbuild` chose sandboxed `/var/tmp`; `build-branding-rpm.sh` now
directs all RPM temporary files into its fresh output directory. No host
packages or boot settings were changed.

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
