# Build and test Fedora 44 UjwalOS v0.1

## Inputs and scope

Use Fedora 44 x86-64. The pinned upstream source, repositories, profile and
changes are described in [image/README.md](../image/README.md) and
[image/inputs.json](../image/inputs.json). Selection is `Fedora.kiwi`, type `iso`,
profile `KDE-Desktop-Live`, source commit
`dfc49a5a10f69941179fdadd96aa6a5984f7c677`.

The first derivative changes image/media names and explicitly includes
`kde-connect`. Desktop wallpaper, installed Fedora identity, installer,
first-run setup, boot scripts and templates stay upstream. This is an internal
engineering ISO; branding/trademark review is still required before publication.

## Dependencies

The inspected upstream README lists `kiwi`, `kiwi-systemdeps` and
`distribution-gpg-keys`. Upstream CI additionally lists `git-core`,
`kiwi-systemdeps-containers`, `kiwi-systemdeps-disk-images`, and `libselinux-utils`.
The UjwalOS wrapper requires the installed KIWI 11 CLI and boxed plugin,
Python 3.12+ (tar extraction filters), Bash, coreutils, util-linux (`flock`),
curl, RPM, tar, xz and QEMU. The VM tester also needs xorriso and edk2-ovmf.

For a **dedicated Fedora 44 development machine**, after authorizing package
installation there, the provisioning command is:

```sh
sudo dnf install kiwi-cli kiwi-systemdeps kiwi-boxed-plugin distribution-gpg-keys \
  git-core libselinux-utils python3 bash coreutils util-linux curl rpm tar xz \
  qemu-system-x86 qemu-img qemu-ui-gtk edk2-ovmf xorriso
```

The build script never invokes this command or sudo. The packages used here
were already installed before this implementation session. Observed versions:
KIWI 11.0.2, boxed plugin 0.2.60, QEMU 10.2.2, edk2-ovmf 20260213-4.fc44,
distribution-gpg-keys 1.118-1.fc44. Each build records host RPM versions. The pinned universal builder SBOM lists
KIWI system dependencies 11.0.5-1.4, DNF5 5.4.6.0-1.fc46 and
distribution-gpg-keys 1.123-1.fc46; these are builder tools, not Fedora target RPMs.

Budget 80 GiB free space and at least 7 GiB available RAM (6 GiB for the builder).
The space allowance is conservative, not a measured minimum. Builds use an
upstream disposable `universal` builder VM, as in Fedora's isolated workflow,
not a privileged host chroot or a host container. Its userspace is a separate
build appliance; Fedora 44 is the target and wrapper host requirement.

## Exact commands

From the repository root as a normal user:

```sh
# Offline verification and KIWI schema/profile validation:
scripts/build/build-iso.sh --validate

# Also check tools, host release, disk/RAM, and Fedora repository network access:
scripts/build/build-iso.sh --check

# Compose in an isolated QEMU builder (default mode):
scripts/build/build-iso.sh
```

Every invocation creates a fresh `out/build-XXXXXXXX/` directory. It never reuses
a partially built root tree. The shared builder download cache is in
`out/box-cache/`. `image/builder.json` pins all three builder artifacts; downloads
use HTTPS and verified hashes. If upstream replaces them, the build fails rather
than silently changing inputs. Preserve the cache for replay. A lock prevents concurrent builds from corrupting that cache.
Repository paths with spaces or shell metacharacters are rejected because the
upstream boxed plugin constructs shell commands internally.

Expected validation output:

```text
Prepared UjwalOS-0.1 from dfc49a5a10f69941179fdadd96aa6a5984f7c677
Description validated: .../out/build-XXXXXXXX/description-validation.log
```

On successful compose (not yet a boot certification):

```text
ISO built: .../out/build-XXXXXXXX/result/<KIWI-generated-name>.iso
<sha256>  <KIWI-generated-name>.iso
Live boot, installer launch and installation remain UNTESTED.
```

The script records the actual generated filename in `iso-path.txt`, with
`SHA256SUMS` beside the ISO. It requires both guest `result.code = 0` and exactly
one nonempty ISO. A successful QEMU/plugin exit alone cannot satisfy this check.
Errors return nonzero, preserve logs and write `exit-code`.

The KIWI invocation is recorded verbatim in each run's `command.sh`. Its form is:

```sh
kiwi-ng --config image/compose/kiwi.yml --temp-dir "$run/tmp" --type iso --profile KDE-Desktop-Live \
  --kiwi-file Fedora.kiwi --debug system boxbuild --box universal --no-update-check \
  --9p-sharing --box-memory 6G --box-smp-cpus 4 --cpu host kiwi \
  --description "$run/description" --target-dir "$run/result" \
  --set-type-attr volid=UjwalOS-0.1-KDE-Live-44 \
  --set-type-attr application_id=UjwalOS-0.1-KDE_Desktop-Live-44 \
  --set-type-attr publisher=UjwalOS
```

`run` above represents the fresh directory created by the script. Without usable
KVM the wrapper replaces `--cpu host` with `--no-accel --cpu max`. Software
emulation is much slower. Do not use the older KIWI 10 `boxbuild -- ...` syntax
with this KIWI 11 wrapper; KIWI 11 uses the `kiwi` subcommand.

The generated description materializes the upstream repository alias because
mapped 9p sharing does not reliably expose host symlinks. The supported `boxroot`
hook installs a builder-only KIWI drop-in selecting `isomd5sum`; this preserves
Fedora's live media check rather than disabling it.

The VM sees the generated description and result directory, plus its disposable
builder disk. No physical host disks or host bootloader paths are passed to it.
The upstream builder's guest configuration is independent of host security
settings and the Fedora target image's security settings.

## Test the ISO

Use the actual path printed by the successful build:

```sh
scripts/test/test-iso.sh out/build-XXXXXXXX/result/ACTUAL-NAME.iso --check-only
scripts/test/test-iso.sh out/build-XXXXXXXX/result/ACTUAL-NAME.iso
```

The first command checks the selected file's SHA-256, ISO9660 signature and UEFI
El Torito boot entry. These checks do not establish a successful boot.
The second creates `out/vm-XXXXXXXX/`, a 40 GiB sparse QCOW2 disk and private UEFI
variables, then opens QEMU with 4 GiB RAM. Install only to that virtual disk.
Without KVM it prints `using -accel tcg` and uses the emulated `max` CPU.
Firmware paths follow this Fedora 44 edk2-ovmf package; missing firmware fails
explicitly. The initial test uses ordinary UEFI, not Secure Boot certification. GTK needs
a graphical session; use `--headless` when DISPLAY/Wayland is unavailable.

For a headless session:

```sh
scripts/test/test-iso.sh out/build-XXXXXXXX/result/ACTUAL-NAME.iso --headless
```

QEMU exposes VNC only through `out/vm-XXXXXXXX/vnc.sock` and a monitor through
`monitor.sock`. Use a Unix-socket-capable VNC client or the monitor to capture
screenshots. The script records the command, QEMU stderr and serial output.
Graphical Plasma may not write useful serial output; lack of serial output is
not evidence that it failed or passed.

After installing, shut down the guest and boot its disk without the ISO:

```sh
scripts/test/test-iso.sh --installed out/vm-XXXXXXXX
```

## Acceptance and diagnostics

Record separately, with logs/screenshots and image checksum:

1. Description validated by KIWI.
2. Nonempty ISO built with checksum.
3. Live UEFI boot reaches usable Plasma; verify keyboard, mouse and networking.
4. Stock installer launches.
5. Installation onto the blank virtual disk completes; eject ISO, boot that disk,
   complete first-run account setup, log in and reboot successfully.

Only step 5 completes Stage 1. Physical hardware, Secure Boot, hybrid NVIDIA,
phone pairing and game performance remain separate tests.

For failures, inspect `build.log`, `description-validation.log`, guest
`result/result.log` and `result.code`. A failure before guest completion must
not be treated as a compose success. Fix the concrete cause and rerun; every
attempt gets a new output directory. Do not disable host security to work around
a build failure. Build logs can contain local paths; review before sharing.

Repository checks:

```sh
python3 -m unittest discover -s tests/config -v
bash -n scripts/build/build-iso.sh scripts/test/test-iso.sh
git diff --check
```

## Reproducibility limits

The source archive and derivative are pinned and hash-checked. RPM repositories still evolve; builder downloads are hash-pinned but may cease
to be available from upstream. Save `inputs.json`, description hashes,
metalinks, host RPM inventory, tool versions, KIWI result inventory, and builder
checksums with each attempt. A public release needs an archived repository/RPM
snapshot and durable builder artifact storage, with repeat-build evidence. The present
workflow does not claim bit-for-bit reproducibility.

Sources inspected: the pinned upstream README, VARIANTS.md, Fedora.kiwi,
repositories/core.xml, teams/kde.xml, components/liveinstall.xml, upstream
kiwi-build, local KIWI 11/boxed-plugin help and implementation, and installed
QEMU help/firmware files. See [status.md](status.md) for actual results.
