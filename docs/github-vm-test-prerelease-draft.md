# UjwalOS 0.1 experimental VM image

## Release title

UjwalOS 0.1 experimental VM test image (2026-10-16)

## Suggested tag

`v0.1-vmtest-20261016`

## Classification

Draft pre-release for controlled virtual-machine testing. This is not a stable
release, hardware-certified installer, or public redistribution approval.

## Description

This engineering image provides a Fedora KDE 44 based UjwalOS live/install ISO
for testing in a disposable virtual machine. The compose completed successfully,
and its wrapper and builder guest both exited with status 0.

The image includes:

- Packaged UjwalOS desktop, login and Plymouth branding.
- Optional gaming setup launcher; Steam and proprietary drivers are not bundled.
- Gaming Center profile editor, packaged as `ujwalos-apps` 0.1-4.
- KDE Connect based Phone Panel preview.
- Fedora package-signature enforcement during compose.
- Builder networking without the boxed plugin's SSH host forwarding.
- Bounded, nonblocking Gaming Center profile loading.

Automated source checks passed before the compose: 48 configuration tests,
13 Qt UI tests and two isolated D-Bus tests. Additional libdnf checks rejected
an unsigned RPM and a Fedora-signed RPM when only an unrelated key was trusted,
then accepted the Fedora RPM after the correct Fedora 44 key was imported into
a temporary test root.

## Download verification

File: `UjwalOS-0.1.x86_64-44-0.iso`

Size: 3,834,904,576 bytes

SHA-256:

```text
a1efa6cc0dfb5beb94e64fab11c658a20463980cbc9f8875295a3a6c3cf38775  UjwalOS-0.1.x86_64-44-0.iso
```

Verify on Linux:

```sh
sha256sum UjwalOS-0.1.x86_64-44-0.iso
```

## VM test instructions

Use UEFI firmware, at least 4 GiB RAM, two virtual CPUs and a new 40 GiB virtual
disk. Boot the ISO, test the live desktop, and install only to the disposable
virtual disk. After installation, detach the ISO and verify first-run setup,
login, reboot and a second login.

Repository test command:

```sh
scripts/test/test-iso.sh out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso --headless
```

Report the VM software/version, host CPU, firmware mode, graphics adapter,
whether live Plasma opened, whether installation completed, whether the disk
booted with the ISO detached, and any screenshots or exact error messages.

## Known limitations

- On 2026-10-16 this exact image passed UEFI live Plasma boot, Gaming Center
  and Phone Panel smoke tests, fresh installation to a 40 GiB QCOW2,
  ISO-detached first-run setup/login, reboot and second login.
- Physical USB boot, Secure Boot, GPU acceleration, controller support,
  suspend/resume and dual/triple boot are untested.
- VirtualBox software rendering is not a gaming-performance benchmark.
- Stage 3 gaming acceptance, Stage 4 system integration, remaining phone
  features, Waydroid, recovery and accessibility gates remain incomplete.
- Artifacts are unsigned engineering files. The SHA-256 checksum detects file
  changes only when obtained through an independently trusted channel.
- The image was composed from a working tree based on Git commit
  `78a81bc360fcfc68d76ffb209d46f79d0de34286`; the security fixes were
  uncommitted at build time. The compose directory retains hashes of all generated
  image-description inputs. Repository documentation was finalized after the
  compose, so this artifact is engineering evidence rather than a reproducible
  release tied directly to one clean source commit.
- Project branding packages still use `LicenseRef-UjwalOS-Internal`; licensing
  and Fedora trademark/remix review must be completed before public distribution.

Use this image only in a disposable VM. Do not install it to a physical disk or
rely on it for production data.
