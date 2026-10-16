import importlib.util
import json
import os
import subprocess
import unittest
from unittest.mock import patch


SOURCE = __import__("pathlib").Path(__file__).resolve().parents[2] / "scripts/test/check-installed-system.py"
SPEC = importlib.util.spec_from_file_location("check_installed_system", SOURCE)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def completed(argv, stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess(argv, returncode, stdout, stderr)


class InstalledSystemTests(unittest.TestCase):
    def setUp(self):
        self.responses = {}

        def run(argv, **kwargs):
            self.assertEqual(kwargs["timeout"], checker.TIMEOUT_SECONDS)
            self.assertFalse(kwargs.get("shell", False))
            self.assertEqual(kwargs["env"]["LC_ALL"], "C")
            self.assertEqual(kwargs["env"]["LANG"], "C")
            self.assertEqual(kwargs["env"].get("PATH"), os.environ.get("PATH"))
            self.assertEqual(kwargs["errors"], "replace")
            key = tuple(argv)
            response = self.responses.get(key)
            if isinstance(response, BaseException):
                raise response
            if response is None:
                self.fail(f"Unexpected subprocess: {key!r}")
            return response

        self.run_mock = patch.object(checker.subprocess, "run", side_effect=run)
        self.run_mock.start()
        self.addCleanup(self.run_mock.stop)
        self.good_responses()

    def good_responses(self):
        self.responses.update({
            ("findmnt", "-n", "-o", "SOURCE", "/"): completed(
                ("findmnt",), "/dev/vda3[/root]\n"),
            ("getenforce",): completed(("getenforce",), "Enforcing\n"),
            ("systemctl", "is-active", "firewalld"): completed(
                ("systemctl",), "active\n"),
            ("getent", "-s", "files", "passwd", "liveuser"): completed(
                ("getent",), "", returncode=2),
            ("ss", "-H", "-l", "-n", "-t", "-u"): completed(("ss",)),
        })
        for package in checker.PACKAGES:
            self.responses[("rpm", "-q", package)] = completed(
                ("rpm",), f"{package}-1.0-1.fc44.noarch\n")
            self.responses[("rpm", "-V", "--noscripts", package)] = completed(
                ("rpm",))

    def test_all_pass(self):
        report = checker.run_checks()
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["overall"], "PASS")
        self.assertTrue(all(c["status"] == "PASS" for c in report["checks"]))
        self.assertIn(("rpm", "-V", "--noscripts", checker.PACKAGES[0]),
                      self.responses)

    def test_empty_query_and_verify_warning_are_unknown(self):
        package = checker.PACKAGES[0]
        self.responses[("rpm", "-q", package)] = completed(("rpm",))
        self.assertEqual(checker._package_check(package)["status"], "UNKNOWN")
        self.good_responses()
        self.responses[("rpm", "-V", "--noscripts", package)] = completed(
            ("rpm",), stderr="warning: cannot establish file state")
        self.assertEqual(checker._package_check(package)["status"], "UNKNOWN")

    def test_missing_opt_in_runs_no_subprocess(self):
        self.run_mock.stop()
        with patch.object(checker.subprocess, "run") as run:
            from contextlib import redirect_stdout
            from io import StringIO
            output = StringIO()
            with redirect_stdout(output):
                result = checker.main([])
            run.assert_not_called()
        self.assertEqual(result, 2)
        report = json.loads(output.getvalue())
        self.assertEqual(report["overall"], "UNKNOWN")

    def test_overlay_root_fails(self):
        self.responses[("findmnt", "-n", "-o", "SOURCE", "/")] = completed(
            ("findmnt",), "overlay\n")
        report = checker.run_checks()
        self.assertEqual(report["checks"][0]["status"], "FAIL")
        self.assertEqual(report["overall"], "FAIL")

    def test_non_device_root_is_unknown(self):
        self.responses[("findmnt", "-n", "-o", "SOURCE", "/")] = completed(
            ("findmnt",), "mapper/root\n")
        self.assertEqual(checker.run_checks()["checks"][0]["status"], "UNKNOWN")

    def test_malformed_root_source_is_unknown(self):
        command = ("findmnt", "-n", "-o", "SOURCE", "/")
        for source in ("/dev/vda3 /dev/vdb1\n", "/dev/mapper/my root\n"):
            self.responses[command] = completed(("findmnt",), source)
            self.assertEqual(checker.run_checks()["checks"][0]["status"], "UNKNOWN")

    def test_exact_forbidden_port_matching(self):
        command = ("ss", "-H", "-l", "-n", "-t", "-u")
        self.responses[command] = completed(("ss",),
            "tcp LISTEN 0 128 0.0.0.0:2222 0.0.0.0:*\n"
            "tcp LISTEN 0 128 [::]:10023 [::]:*\n")
        report = checker.run_checks()
        listeners = next(c for c in report["checks"] if c["id"] == "listeners")
        self.assertEqual(listeners["status"], "PASS")
        self.responses[command] = completed(("ss",),
            "tcp LISTEN 0 128 127.0.0.1:10022 0.0.0.0:*\n")
        report = checker.run_checks()
        listeners = next(c for c in report["checks"] if c["id"] == "listeners")
        self.assertEqual(listeners["status"], "FAIL")
        self.assertEqual(listeners["evidence"]["forbidden_local_ports"], [10022])

    def test_malformed_listener_is_unknown_but_forbidden_port_wins(self):
        command = ("ss", "-H", "-l", "-n", "-t", "-u")
        malformed = "tcp LISTEN 0 128 127.0.0.1:70000 *\n"
        self.responses[command] = completed(("ss",), malformed)
        report = checker.run_checks()
        listeners = next(c for c in report["checks"] if c["id"] == "listeners")
        self.assertEqual(listeners["status"], "UNKNOWN")
        self.responses[command] = completed(("ss",),
            malformed + "udp UNCONN 0 0 [::]:00022 [::]:*\n")
        report = checker.run_checks()
        listeners = next(c for c in report["checks"] if c["id"] == "listeners")
        self.assertEqual(listeners["status"], "FAIL")
        self.assertEqual(listeners["evidence"]["forbidden_local_ports"], [22])

    def test_rpm_integrity_failure(self):
        package = checker.PACKAGES[0]
        self.responses[("rpm", "-V", "--noscripts", package)] = completed(
            ("rpm",), "SM5....T. /usr/bin/example\n")
        report = checker.run_checks()
        item = next(c for c in report["checks"] if c["id"] == f"package:{package}")
        self.assertEqual(item["status"], "FAIL")
        self.assertNotIn("/usr/bin/example", json.dumps(item))

    def test_unknown_command_and_timeout(self):
        self.responses[("getenforce",)] = completed(("getenforce",), "", "missing", 127)
        self.responses[("systemctl", "is-active", "firewalld")] = subprocess.TimeoutExpired(
            ("systemctl",), checker.TIMEOUT_SECONDS)
        report = checker.run_checks()
        statuses = {c["id"]: c["status"] for c in report["checks"]}
        self.assertEqual(statuses["selinux"], "UNKNOWN")
        self.assertEqual(statuses["firewall"], "UNKNOWN")
        self.assertEqual(report["overall"], "UNKNOWN")

    def test_unrecognized_selinux_is_unknown_and_permissive_fails(self):
        command = ("getenforce",)
        self.responses[command] = completed(command, "unexpected\n")
        report = checker.run_checks()
        selinux = next(c for c in report["checks"] if c["id"] == "selinux")
        self.assertEqual(selinux["status"], "UNKNOWN")
        self.responses[command] = completed(command, "Permissive\n")
        report = checker.run_checks()
        selinux = next(c for c in report["checks"] if c["id"] == "selinux")
        self.assertEqual(selinux["status"], "FAIL")

    def test_oserror_is_unknown(self):
        self.responses[("getenforce",)] = FileNotFoundError("getenforce missing")
        report = checker.run_checks()
        selinux = next(c for c in report["checks"] if c["id"] == "selinux")
        self.assertEqual(selinux["status"], "UNKNOWN")

    def test_rpm_verify_nonzero_redacts_raw_diagnostics(self):
        package = checker.PACKAGES[0]
        self.responses[("rpm", "-V", "--noscripts", package)] = completed(
            ("rpm",), "/private/path/file\n", "/private/path/error\n", 1)
        report = checker.run_checks()
        item = next(c for c in report["checks"] if c["id"] == f"package:{package}")
        self.assertEqual(item["status"], "FAIL")
        encoded = json.dumps(item)
        self.assertNotIn("/private/path", encoded)
        self.assertEqual(item["evidence"]["exit_code"], 1)
        self.assertEqual(item["evidence"]["stdout_lines"], 1)

    def test_cli_exit_codes(self):
        from contextlib import redirect_stdout
        from io import StringIO

        for overall, expected in (("PASS", 0), ("FAIL", 1), ("UNKNOWN", 2)):
            report = {"schema_version": 1, "checks": [], "overall": overall}
            output = StringIO()
            with patch.object(checker, "run_checks", return_value=report):
                with redirect_stdout(output):
                    result = checker.main(["--guest-check"])
            self.assertEqual(result, expected)
            self.assertEqual(json.loads(output.getvalue())["overall"], overall)

    def test_inactive_firewall_fails(self):
        command = ("systemctl", "is-active", "firewalld")
        self.responses[command] = completed(("systemctl",), "inactive\n", returncode=3)
        report = checker.run_checks()
        firewall = next(c for c in report["checks"] if c["id"] == "firewall")
        self.assertEqual(firewall["status"], "FAIL")

    def test_liveuser_entry_is_not_exposed(self):
        self.responses[("getent", "-s", "files", "passwd", "liveuser")] = completed(
            ("getent",), "liveuser:x:1000:1000:Private:/home/liveuser:/bin/bash\n")
        report = checker.run_checks()
        item = next(c for c in report["checks"] if c["id"] == "liveuser_absent")
        self.assertEqual(item["status"], "FAIL")
        self.assertNotIn("/home/liveuser", json.dumps(item))


if __name__ == "__main__":
    unittest.main()
