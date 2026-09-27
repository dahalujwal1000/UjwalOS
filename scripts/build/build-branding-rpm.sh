#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
[[ $# -eq 1 && -d $1 ]] || { echo 'Usage: build-branding-rpm.sh EXISTING-OUTPUT-DIR' >&2; exit 2; }
[[ $EUID -ne 0 ]] || { echo 'Run as a normal user' >&2; exit 1; }
run=$(cd -- "$1" && pwd -P)
mkdir -p "$run/rpmbuild"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,tmp}
rpmbuild --define "_topdir $run/rpmbuild" --define "_tmppath $run/rpmbuild/tmp" \
    --define "_sourcedir $ROOT/branding" \
    -bb "$ROOT/packaging/ujwalos-branding.spec"
mapfile -d '' packages < <(find "$run/rpmbuild/RPMS" -type f -name 'ujwalos-branding-*.rpm' -print0)
[[ ${#packages[@]} -eq 1 ]] || { echo 'Expected one branding RPM' >&2; exit 1; }
printf '%s\n' "${packages[0]}"
