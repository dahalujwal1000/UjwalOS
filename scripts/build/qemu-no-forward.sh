#!/usr/bin/env bash
# Remove only KIWI's default SSH host forward while preserving user networking.
set -Eeuo pipefail

real_qemu=${UJWALOS_REAL_QEMU:?missing real QEMU path}
args=()
removed=0
for arg in "$@"; do
    if [[ $arg == 'user,model=virtio,hostfwd=tcp::10022-:22' ]]; then
        ((removed == 0)) || { echo 'ERROR: duplicate boxed SSH forwarding argument' >&2; exit 90; }
        removed=1
        args+=('user,model=virtio')
    elif [[ $arg == *hostfwd=* ]]; then
        echo "ERROR: unexpected QEMU host forwarding argument: $arg" >&2
        exit 90
    else
        args+=("$arg")
    fi
done
((removed == 1)) || { echo 'ERROR: expected boxed SSH forwarding argument was not found' >&2; exit 90; }
exec "$real_qemu" "${args[@]}"
