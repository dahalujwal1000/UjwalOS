#!/usr/bin/env python3
"""Read-only preparation report; never installs software or starts a build."""

import os
from pathlib import Path
import platform
import shutil


def main():
    root = Path(__file__).resolve().parents[2]
    print("UjwalOS preparation report (not a compose or VM test)")
    print(f"Architecture: {platform.machine()}")
    release = platform.freedesktop_os_release()
    print(f"Environment: {release.get('PRETTY_NAME', 'unknown')}")
    blockers = []
    if platform.machine() != "x86_64":
        blockers.append("Selected target is x86-64; provision a matching builder.")
    if release.get("ID") != "fedora" or release.get("VERSION_ID") != "44":
        blockers.append("Provision a disposable Fedora 44 builder.")
    for name in ("git", "python3", "kiwi-ng", "qemu-system-x86_64", "qemu-img"):
        location = shutil.which(name)
        print(f"{name}: {location or 'MISSING'}")
        if location is None:
            blockers.append(f"{name} unavailable in this environment.")
    usable_kvm = os.access("/dev/kvm", os.R_OK | os.W_OK)
    print(f"KVM accessible: {'yes' if usable_kvm else 'no'}")
    if not usable_kvm:
        print("NOTE: build/test wrappers use slower QEMU software emulation without KVM.")
    free_gib = shutil.disk_usage(root).free / (1024 ** 3)
    print(f"Repository filesystem free: {free_gib:.1f} GiB")
    if free_gib < 80:
        print("NOTE: below the provisional 80 GiB builder disk allowance.")
    print("Pinned description: image/inputs.json; builder: image/builder.json.")
    print("Run scripts/build/build-iso.sh --check for complete build preparation checks.")
    print("Tool presence does not validate versions, firmware, privileges or isolation.")
    for blocker in blockers:
        print(f"BLOCKER: {blocker}")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
