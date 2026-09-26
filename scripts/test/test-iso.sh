#!/usr/bin/env bash
# UEFI VM with a private file-backed disk; no host disk passthrough.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
die() { echo "ERROR: $*" >&2; exit 1; }
usage() {
    echo 'Usage: test-iso.sh ISO [--check-only|--headless]'
    echo '       test-iso.sh --installed out/vm-XXXXXXXX [--headless]'
    echo 'Headless uses a local Unix VNC socket; see docs/build-and-test.md.'
}
[[ $# -ge 1 ]] || { usage; exit 1; }
[[ $1 != --help ]] || { usage; exit 0; }
[[ $EUID -ne 0 ]] || die "Run QEMU as a normal user"
for tool in python3 qemu-system-x86_64 qemu-img xorriso; do command -v "$tool" >/dev/null || die "Missing: $tool"; done
installed=false
if [[ $1 == --installed ]]; then
    [[ $# -ge 2 && $# -le 3 ]] || die "Specify the VM directory"
    installed=true
    vm=$(realpath -- "$2")
    option=${3:-}
    [[ $vm == "$ROOT/out/"vm-* && -d $vm ]] || die "VM must be an existing out/vm-* directory"
    [[ -f $vm/disk.qcow2 && ! -L $vm/disk.qcow2 && -f $vm/OVMF_VARS.fd ]] || die "VM disk or UEFI state missing"
    [[ -z $option || $option == --headless ]] || die "Unknown option: $option"
else
    [[ $# -le 2 ]] || die "Too many arguments"
    option=${2:-}
    [[ -z $option || $option == --headless || $option == --check-only ]] || die "Unknown option: $option"
    [[ -f $1 && ! -b $1 ]] || die "ISO must be an existing regular file, never a device"
    iso=$(realpath -- "$1")
    [[ $iso != *,* ]] || die "ISO path cannot contain a comma (QEMU option separator)"
    # Validate only the selected file; do not follow arbitrary paths in a sums file.
    python3 - "$iso" <<'PY'
import hashlib
from pathlib import Path
import sys
iso = Path(sys.argv[1])
sums = iso.parent / 'SHA256SUMS'
if not sums.is_file():
    raise SystemExit('ERROR: expected SHA256SUMS beside ISO')
entries = [line.split(maxsplit=1) for line in sums.read_text().splitlines()]
matches = [digest for digest, name in entries if name.lstrip('*') == iso.name]
with iso.open('rb') as stream:
    actual = hashlib.file_digest(stream, 'sha256').hexdigest()
if matches != [actual]:
    raise SystemExit('ERROR: ISO checksum mismatch or ambiguous/missing checksum entry')
with iso.open('rb') as stream:
    stream.seek(32769)
    if stream.read(5) != b'CD001':
        raise SystemExit('ERROR: not an ISO9660 image')
print('SHA-256 and ISO9660 signature: PASS')
PY
    report=$(xorriso -indev "$iso" -report_el_torito plain 2>&1)
    [[ $report == *'UEFI'* ]] || die "ISO has no reported UEFI El Torito boot entry"
    echo 'UEFI boot catalog: present (does not prove a successful boot)'
    [[ $option != --check-only ]] || exit 0
    mkdir -p "$ROOT/out"
    vm=$(mktemp -d "$ROOT/out/vm-XXXXXXXX")
    [[ $(df -Pk "$vm" | awk 'END {print $4}') -ge $((45 * 1024 * 1024)) ]] || die "Need 45 GiB free for VM installation"
    qemu-img create -f qcow2 "$vm/disk.qcow2" 40G
    cp /usr/share/edk2/ovmf/OVMF_VARS.fd "$vm/OVMF_VARS.fd"
    printf '%s\n' "$iso" > "$vm/source-iso.txt"
fi
[[ $vm != *,* ]] || die "VM path cannot contain a comma"
firmware=/usr/share/edk2/ovmf/OVMF_CODE.fd
[[ -f $firmware ]] || die "Missing edk2-ovmf firmware: $firmware"
accel=(-accel kvm -cpu host)
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
    echo 'KVM unavailable: using -accel tcg; live boot and installation will be slower.'
    accel=(-accel tcg -cpu max)
fi
display=(-display gtk)
if [[ $option == --headless ]]; then
    display=(-display none -vnc "unix:$vm/vnc.sock")
fi
media=()
if ! $installed; then media=(-drive "file=$iso,media=cdrom,format=raw,readonly=on" -boot order=d); fi
cmd=(qemu-system-x86_64 -name UjwalOS-v0.1-test -machine q35 "${accel[@]}"
     -m 4096 -smp 2 -device virtio-vga -device qemu-xhci -device usb-tablet
     -drive "if=pflash,format=raw,readonly=on,file=$firmware"
     -drive "if=pflash,format=raw,file=$vm/OVMF_VARS.fd"
     -drive "file=$vm/disk.qcow2,format=qcow2,if=virtio"
     "${media[@]}" -nic user,model=virtio-net-pci "${display[@]}"
     -monitor "unix:$vm/monitor.sock,server=on,wait=off"
     -serial "file:$vm/serial.log")
printf '%q ' "${cmd[@]}" > "$vm/qemu-command.sh"
printf '\n' >> "$vm/qemu-command.sh"
echo "VM: $vm"
echo 'Observe Plasma, launch the installer, select only the 40 GiB virtual disk.'
echo 'QEMU exit status is NOT a boot or installation test result. Record observations separately.'
"${cmd[@]}" 2> >(tee "$vm/qemu-stderr.log" >&2)
