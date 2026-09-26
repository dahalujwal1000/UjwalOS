#!/usr/bin/env bash
# Compose only inside KIWI's disposable QEMU box. Never run system build on host.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
die() { echo "ERROR: $*" >&2; exit 1; }
mode=${1:---build}
[[ $# -le 1 && $mode =~ ^(--build|--check|--validate|--help)$ ]] || die "Use --build, --check, --validate or --help"
if [[ $mode == --help ]]; then
    echo 'Usage: scripts/build/build-iso.sh [--build|--check|--validate]'
    echo '--validate checks the pinned description offline; --check adds resources/network checks.'
    echo 'Default: build in a disposable QEMU VM. Outputs: out/build-*/'
    exit 0
fi
[[ $EUID -ne 0 ]] || die "Run as your normal user; the builder VM supplies guest root. Do not use sudo."
# The upstream boxed plugin constructs a shell command internally: reject shell
# metacharacters in every path it receives, even though our calls use arrays.
[[ $ROOT =~ ^/[a-zA-Z0-9_./-]+$ ]] || die "Repository path must contain only letters, digits, /, _, . and - (boxed plugin limitation)"
for tool in python3 kiwi-ng sha256sum flock tee; do command -v "$tool" >/dev/null || die "Missing tool: $tool"; done
[[ $(uname -m) == x86_64 ]] || die "An x86-64 builder host is required"
source /etc/os-release
[[ $ID == fedora && $VERSION_ID == 44 ]] || die "This entry point is validated for Fedora 44 hosts only"
python3 - <<'PY'
from importlib.metadata import version
if version('kiwi').split('.')[0] != '11':
    raise SystemExit('ERROR: this wrapper requires KIWI 11 CLI syntax; see docs/build-and-test.md')
PY
mkdir -p "$ROOT/out"
exec 9>"$ROOT/out/.build.lock"
flock -n 9 || die "Another build/check holds out/.build.lock"
run=$(mktemp -d "$ROOT/out/build-XXXXXXXX")
mkdir "$run/tmp"
export TMPDIR="$run/tmp"
exec > >(tee "$run/build.log") 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > "$run/exit-code"; if ((rc)); then echo "FAILED ($rc). Evidence: $run"; fi' EXIT
cp "$ROOT/image/inputs.json" "$run/inputs.json"
python3 "$ROOT/scripts/build/prepare-description.py" "$run/description"
kiwi=(kiwi-ng --config "$ROOT/image/compose/kiwi.yml" --temp-dir "$run/tmp" --type iso --profile KDE-Desktop-Live --kiwi-file Fedora.kiwi)
"${kiwi[@]}" image info --description "$run/description" --print-xml > "$run/description-validation.log" 2>&1
echo "Description validated: $run/description-validation.log"
[[ $mode != --validate ]] || exit 0
for tool in curl qemu-system-x86_64 qemu-img rpm tar xz; do
    command -v "$tool" >/dev/null || die "Missing tool: $tool; see documented builder dependencies"
done
python3 -c 'import kiwi_boxed_plugin' || die "Missing kiwi-boxed-plugin"
free_kib=$(df -Pk "$ROOT/out" | awk 'END {print $4}')
((free_kib >= 80 * 1024 * 1024)) || die "Need at least 80 GiB free in out/ (planning allowance)"
available_kib=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
((available_kib >= 7 * 1024 * 1024)) || die "Need 7 GiB available RAM for a 6 GiB builder VM"
for repo in fedora-44 updates-released-f44; do
    curl --fail --location --silent --show-error --retry 2 --connect-timeout 15 --max-time 90 \
        "https://mirrors.fedoraproject.org/metalink?repo=$repo&arch=x86_64" -o "$run/$repo.metalink"
done
echo "Fedora 44 repository network checks passed (individual mirrors may still fail)."
rpm -qa --qf '%{NEVRA}\n' | sort > "$run/host-rpms.txt"
python3 -c 'from importlib.metadata import version; print(version("kiwi"))' > "$run/kiwi-version.txt"
qemu-system-x86_64 --version > "$run/qemu-version.txt"
[[ $mode != --check ]] || { echo "Preparation checks passed; no compose started."; exit 0; }
mkdir -p "$ROOT/out/box-cache"
export KIWI_BOXED_CACHE_DIR="$ROOT/out/box-cache"
python3 "$ROOT/scripts/build/fetch-box.py" "$KIWI_BOXED_CACHE_DIR"
cp "$ROOT/image/builder.json" "$run/builder.json"
accel=(--cpu host)
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
    echo 'KVM unavailable: building with QEMU software emulation (TCG); this will be much slower.'
    accel=(--no-accel --cpu max)
fi
cmd=("${kiwi[@]}" --debug system boxbuild --box universal --no-update-check
     --9p-sharing --box-memory 6G --box-smp-cpus 4 "${accel[@]}" kiwi
     --description "$run/description" --target-dir "$run/result"
     --set-type-attr volid=UjwalOS-0.1-KDE-Live-44
     --set-type-attr application_id=UjwalOS-0.1-KDE_Desktop-Live-44
     --set-type-attr publisher=UjwalOS)
printf '%q ' "${cmd[@]}" > "$run/command.sh"
printf '\n' >> "$run/command.sh"
echo "Starting isolated compose. Log: $run/build.log"
"${cmd[@]}"
# The plugin can return zero even if QEMU exits before the guest writes results.
[[ -f $run/result/result.code ]] || die "Builder did not report completion; no success inferred from plugin exit status"
[[ $(cat "$run/result/result.code") == 0 ]] || die "Guest compose failed; inspect result/result.log"
mapfile -d '' isos < <(find "$run/result" -maxdepth 1 -type f -name '*.iso' -print0)
[[ ${#isos[@]} -eq 1 && -s ${isos[0]} ]] || die "Expected exactly one nonempty ISO in result/"
iso=${isos[0]}
(cd "$run/result" && sha256sum -- "$(basename "$iso")" > SHA256SUMS)
printf '%s\n' "$iso" > "$run/iso-path.txt"
find "$ROOT/out/box-cache" -type f \( -name '*.qcow2' -o -name '*.tar.xz' -o -name '*.json' \) \
    -exec sha256sum {} + > "$run/builder-inputs.sha256"
echo "ISO built: $iso"
cat "$run/result/SHA256SUMS"
echo 'Live boot, installer launch and installation remain UNTESTED.'
