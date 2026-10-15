#!/usr/bin/env python3
"""Check libdnf signature rejection/acceptance without installing any packages.

Supply an unsigned test RPM, a signed Fedora RPM, and local trusted/unrelated
Fedora public keys. Downloads and key trust decisions remain explicit operator
inputs; the script never fetches a key or changes the host RPM database.
"""

import argparse
import hashlib
from pathlib import Path
import tempfile

import libdnf5


def check(unsigned_rpm, signed_rpm, trusted_key, unrelated_key):
    with tempfile.TemporaryDirectory(prefix="ujwalos-signatures-") as directory:
        root = Path(directory)
        base = libdnf5.base.Base()
        config = base.get_config()
        config.installroot = str(root / "root")
        config.cachedir = str(root / "cache")
        config.logdir = str(root / "logs")
        config.persistdir = str(root / "state")
        config.plugins = False
        base.setup()
        verifier = libdnf5.rpm.RpmSignature(base)

        def require_result(package, expected, label):
            result = verifier.check_package_signature(str(package))
            if result != expected:
                raise RuntimeError(f"{label}: expected {expected}, got {result}")
            print(f"PASS: {label}")

        require_result(unsigned_rpm, verifier.CheckResult_FAILED_NOT_SIGNED,
                       "unsigned package rejected")
        require_result(signed_rpm, verifier.CheckResult_FAILED_KEY_MISSING,
                       "signed package rejected with empty keyring")
        unrelated = verifier.parse_key_file(unrelated_key.as_uri())
        trusted = verifier.parse_key_file(trusted_key.as_uri())
        if not unrelated or not trusted:
            raise ValueError("Both supplied public key files must contain keys")
        if {key.get_fingerprint() for key in unrelated} & {
                key.get_fingerprint() for key in trusted}:
            raise ValueError("Unrelated key must differ from trusted key")
        for key in unrelated:
            verifier.import_key(key)
        require_result(signed_rpm, verifier.CheckResult_FAILED_KEY_MISSING,
                       "signed package rejected with only unrelated key trusted")
        for key in trusted:
            verifier.import_key(key)
        require_result(signed_rpm, verifier.CheckResult_OK,
                       "signed package accepted with correct key trusted")
        require_result(unsigned_rpm, verifier.CheckResult_FAILED_NOT_SIGNED,
                       "unsigned package still rejected after key import")

    for path in (unsigned_rpm, signed_rpm, trusted_key, unrelated_key):
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        print(f"SHA256 {digest}  {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("unsigned-rpm", "signed-rpm", "trusted-key", "unrelated-key"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    check(*(path.resolve(strict=True) for path in (
        args.unsigned_rpm, args.signed_rpm, args.trusted_key, args.unrelated_key)))
