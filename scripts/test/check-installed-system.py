#!/usr/bin/env python3
"""Read-only, bounded checks for an explicitly selected installed guest."""

import argparse
import json
import os
import selectors
import subprocess
import sys
import time


TIMEOUT_SECONDS = 5
MAX_OUTPUT_BYTES = 1024 * 1024
OUTPUT_LIMIT = 512
PACKAGES = ("ujwalos-apps", "ujwalos-branding", "ujwalos-gaming-setup")
FORBIDDEN_PORTS = {22, 10022}


def _brief(value):
    """Return short, single-line command diagnostics without raw records."""
    return " ".join(value.split())[:OUTPUT_LIMIT]


def _run(argv):
    process = None
    selector = selectors.DefaultSelector()
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    try:
        process = subprocess.Popen(
            list(argv), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={**os.environ, "LC_ALL": "C", "LANG": "C"},
        )
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        deadline = time.monotonic() + TIMEOUT_SECONDS
        while selector.get_map() or process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                process.wait()
                return None, "timeout"
            if not selector.get_map():
                try:
                    process.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    return None, "timeout"
                break
            for key, _ in selector.select(remaining):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                combined = sum(map(len, streams.values())) + len(chunk)
                if combined > MAX_OUTPUT_BYTES:
                    process.kill()
                    process.wait()
                    return None, "output-limit"
                streams[key.data].extend(chunk)
        return subprocess.CompletedProcess(
            list(argv), process.wait(),
            bytes(streams["stdout"]).decode("utf-8", "replace"),
            bytes(streams["stderr"]).decode("utf-8", "replace"),
        ), None
    except (OSError, subprocess.SubprocessError) as exc:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        return None, _brief(str(exc)) or type(exc).__name__
    finally:
        selector.close()
        if process is not None:
            for stream in (process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    stream.close()


def _check(check_id, status, evidence):
    return {"id": check_id, "status": status, "evidence": evidence}


def _command_error(result, detail):
    if result is None:
        return detail
    return _brief(result.stderr) or _brief(result.stdout) or f"exit {result.returncode}"


def _root_source():
    result, error = _run(("findmnt", "-n", "-o", "SOURCE", "/"))
    if result is None:
        return _check("root_source", "UNKNOWN", {"reason": error})
    if result.returncode != 0:
        return _check("root_source", "UNKNOWN", {
            "reason": _command_error(result, error),
        })
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        return _check("root_source", "UNKNOWN", {
            "reason": "expected exactly one source line",
        })
    source = lines[0].strip()
    if not source or any(character.isspace() for character in source):
        return _check("root_source", "UNKNOWN", {
            "reason": "source must be one nonempty whitespace-free line",
        })
    lowered = source.lower()
    if lowered.startswith(("overlay", "tmpfs")):
        return _check("root_source", "FAIL", {
            "source_type": "overlay-or-tmpfs",
        })
    if source.startswith("/dev/"):
        return _check("root_source", "PASS", {
            "source_type": "device",
            "note": "A /dev source does not prove ISO detachment or VM status.",
        })
    return _check("root_source", "UNKNOWN", {
        "source_type": "other",
        "note": "Source is not a /dev path; guest status is not inferred.",
    })


def _simple_check(check_id, argv, expected):
    result, error = _run(argv)
    if result is None:
        return _check(check_id, "UNKNOWN", {"reason": error})
    if result.returncode != 0:
        return _check(check_id, "UNKNOWN", {
            "reason": _command_error(result, error),
        })
    observed = _brief(result.stdout)
    if observed == expected:
        return _check(check_id, "PASS", {"observed": observed})
    if check_id == "selinux" and observed in {"Permissive", "Disabled"}:
        return _check(check_id, "FAIL", {"observed": observed})
    return _check(check_id, "UNKNOWN", {
        "reason": "empty or unrecognized command output",
    })


def _package_check(package):
    query, error = _run(("rpm", "-q", package))
    if query is None:
        return _check(f"package:{package}", "UNKNOWN", {"reason": error})
    if query.returncode != 0:
        absent_message = f"package {package} is not installed"
        absent = (
            query.returncode == 1
            and (query.stdout.strip(), query.stderr.strip()) in {
                (absent_message, ""), ("", absent_message),
            }
        )
        if absent:
            return _check(f"package:{package}", "FAIL", {
                "installed": False, "reason": "package is not installed",
            })
        return _check(f"package:{package}", "UNKNOWN", {
            "reason": "query-failed",
            "exit_code": query.returncode,
        })
    version = _brief(query.stdout)
    if not version or query.stderr.strip():
        return _check(f"package:{package}", "UNKNOWN", {
            "reason": "empty package query or query diagnostics",
        })
    verify, error = _run(("rpm", "-V", "--noscripts", package))
    if verify is None:
        return _check(f"package:{package}", "UNKNOWN", {
            "installed": True, "version": version, "verify_error": error,
        })
    if verify.returncode != 0:
        return _check(f"package:{package}", "FAIL", {
            "installed": True,
            "version": version,
            "integrity": "mismatch-or-error",
            "exit_code": verify.returncode,
            "stdout_lines": len(verify.stdout.splitlines()),
            "stderr_lines": len(verify.stderr.splitlines()),
        })
    if verify.stdout.strip():
        return _check(f"package:{package}", "FAIL", {
            "installed": True,
            "version": version,
            "integrity": "mismatch",
            "changed_entries": len(verify.stdout.splitlines()),
        })
    if verify.stderr.strip():
        return _check(f"package:{package}", "UNKNOWN", {
            "installed": True, "version": version,
            "reason": "verification diagnostics require review",
        })
    return _check(f"package:{package}", "PASS", {
        "installed": True, "version": version, "integrity": "clean",
    })


def _local_account_check():
    result, error = _run(("getent", "-s", "files", "passwd", "liveuser"))
    if result is None:
        return _check("liveuser_absent", "UNKNOWN", {"reason": error})
    if result.returncode == 2:
        return _check("liveuser_absent", "PASS", {"present": False})
    if result.returncode == 0:
        # Do not include passwd data: it contains account and home details.
        return _check("liveuser_absent", "FAIL", {"present": True})
    return _check("liveuser_absent", "UNKNOWN", {
        "reason": f"getent exit {result.returncode}",
    })


def _firewall_check():
    result, error = _run(("systemctl", "is-active", "firewalld"))
    if result is None:
        return _check("firewall", "UNKNOWN", {"reason": error})
    state = _brief(result.stdout)
    if result.returncode == 0 and state == "active":
        return _check("firewall", "PASS", {"state": state})
    if state in {"inactive", "failed", "activating", "deactivating"}:
        return _check("firewall", "FAIL", {"state": state})
    return _check("firewall", "UNKNOWN", {
        "reason": _command_error(result, error),
    })


def _listeners_check():
    result, error = _run(("ss", "-H", "-l", "-n", "-t", "-u"))
    if result is None:
        return _check("listeners", "UNKNOWN", {"reason": error})
    if result.returncode != 0:
        return _check("listeners", "UNKNOWN", {
            "reason": _command_error(result, error),
        })
    ports = set()
    malformed = False
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 6 or fields[0] not in {"tcp", "udp"}:
            malformed = True
            continue
        local = fields[4]
        if local.startswith("[") and "]:" in local:
            port = local.rsplit("]:", 1)[1]
        elif ":" in local:
            port = local.rsplit(":", 1)[1]
        else:
            malformed = True
            continue
        if not port.isdecimal():
            malformed = True
            continue
        numeric_port = int(port)
        if not 0 <= numeric_port <= 65535:
            malformed = True
            continue
        if numeric_port in FORBIDDEN_PORTS:
            ports.add(numeric_port)
    if ports:
        return _check("listeners", "FAIL", {
            "forbidden_local_ports": sorted(ports),
        })
    if malformed:
        return _check("listeners", "UNKNOWN", {
            "reason": "one or more listener rows could not be parsed",
        })
    return _check("listeners", "PASS", {"forbidden_local_ports": []})


def run_checks():
    checks = [_root_source()]
    checks.append(_simple_check("selinux", ("getenforce",), "Enforcing"))
    checks.append(_firewall_check())
    checks.extend(_package_check(package) for package in PACKAGES)
    checks.extend((_local_account_check(), _listeners_check()))
    statuses = {item["status"] for item in checks}
    overall = "FAIL" if "FAIL" in statuses else (
        "UNKNOWN" if "UNKNOWN" in statuses else "PASS"
    )
    return {"schema_version": 1, "checks": checks, "overall": overall}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--guest-check", action="store_true",
        help="explicitly confirm this command should inspect the current guest",
    )
    args = parser.parse_args(argv)
    if not args.guest_check:
        report = {
            "schema_version": 1,
            "checks": [_check(
                "guest_opt_in", "UNKNOWN",
                {"reason": "required --guest-check flag was not supplied"},
            )],
            "overall": "UNKNOWN",
        }
        print(json.dumps(report, sort_keys=True))
        return 2
    report = run_checks()
    print(json.dumps(report, sort_keys=True))
    return {"PASS": 0, "FAIL": 1, "UNKNOWN": 2}[report["overall"]]


if __name__ == "__main__":
    sys.exit(main())
