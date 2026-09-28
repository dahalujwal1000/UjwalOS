#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
[[ $# -eq 1 && -d $1 ]] || { echo 'Usage: build-apps-rpm.sh EXISTING-OUTPUT-DIR' >&2; exit 2; }
[[ $EUID -ne 0 ]] || { echo 'Run as a normal user' >&2; exit 1; }
run=$(cd -- "$1" && pwd -P)
mkdir -p "$run/apps-rpmbuild"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,tmp}
rpmbuild --define "_topdir $run/apps-rpmbuild" --define "_tmppath $run/apps-rpmbuild/tmp" \
    --define "_sourcedir $ROOT" -bb "$ROOT/packaging/ujwalos-apps.spec"
mapfile -d '' packages < <(find "$run/apps-rpmbuild/RPMS" -type f -name 'ujwalos-apps-*.rpm' -print0)
[[ ${#packages[@]} -eq 1 ]] || { echo 'Expected one apps RPM' >&2; exit 1; }
printf '%s\n' "${packages[0]}"
