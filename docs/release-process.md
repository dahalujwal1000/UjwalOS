# Release process

Internal engineering ISOs exist; no public release is approved. Build, live-boot
and installation evidence is recorded separately in [status](status.md).

Stage 7's [artifact verifier and recovery protocol](recovery-and-quality.md) are
the first release-quality milestone. `scripts/release/artifacts.py` creates and
verifies local unsigned manifests; it does not sign, upload or authorize release.

Status updated 2026-10-16: corrected ISO
`out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso` (3,834,904,576 bytes;
SHA-256 `a1efa6cc0dfb5beb94e64fab11c658a20463980cbc9f8875295a3a6c3cf38775`)
passed compose and media checks. The 48 configuration, 13 Qt UI and 2 isolated
D-Bus tests passed. This exact ISO also passed UEFI live Plasma and custom-app
smoke tests, fresh installation to a file-backed disk, ISO-detached setup/login,
reboot and second login. The three findings in the [security review](security-review-2026-09-30.md)
have source fixes, regression evidence and a corrected compose; these do not
complete runtime security acceptance. Authenticated updates for custom UjwalOS
RPMs, full distribution/runtime review, licensing and Fedora trademark/remix
review remain open. This engineering artifact is not a public release, and
redistribution clearance is not established. See the
[acceptance summary](status.md#current-acceptance-summary).

Before a release candidate:

1. Lock source, builder, package/repository and configuration inputs; archive logs.
2. Complete package/asset license and Fedora trademark review. Select licenses
   for original work. Keep proprietary installers separate from base artifacts.
3. Build in isolation. Record image checksum, package manifest, source revision,
   builder identity/version and known limitations. Compare repeat builds.
4. Pass Stage 1's VM install gate and the applicable later-stage tests. Record
   each result separately. Do not publish Secure Boot or hardware claims without
   corresponding tests.
5. Publish versioned ISO, SHA-256 file, input/package manifest and release notes
   through an authenticated channel. A checksum alone does not authenticate its
   publisher. Establish a signing and key-verification process before public use;
   signing keys must never be committed.
6. Document normal updates, backups, older-kernel boot, rescue and failed-update
   recovery. Test each supported recovery path. RPM updates are not atomic
   whole-system rollback.

v1.0 additionally needs multiple hardware configurations, accessibility checks,
dual-boot safety review and repeat install/recovery tests. Public publishing and
distribution are not authorized by the initial repository setup task.
