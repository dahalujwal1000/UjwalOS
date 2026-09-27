#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
[[ $# -eq 1 && -d $1 ]] || { echo 'Usage: build-gaming-rpm.sh EXISTING-OUTPUT-DIR' >&2; exit 2; }
[[ $EUID -ne 0 ]] || { echo 'Run as a normal user' >&2; exit 1; }
run=$(cd -- "$1" && pwd -P)
mkdir -p "$run/gaming-rpmbuild"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,tmp}
rpmbuild --define "_topdir $run/gaming-rpmbuild" --define "_tmppath $run/gaming-rpmbuild/tmp" \
    --define "_sourcedir $ROOT/gaming" \
    -bb "$ROOT/packaging/ujwalos-gaming-setup.spec"
mapfile -d '' packages < <(find "$run/gaming-rpmbuild/RPMS" -type f -name 'ujwalos-gaming-setup-*.rpm' -print0)
[[ ${#packages[@]} -eq 1 ]] || { echo 'Expected one gaming RPM' >&2; exit 1; }
printf '%s\n' "${packages[0]}"
