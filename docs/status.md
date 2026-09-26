# Status and unreleased notes

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
