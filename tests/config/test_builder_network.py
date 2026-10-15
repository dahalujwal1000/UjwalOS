"""Regression tests for the boxed builder's QEMU network arguments."""

import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
QEMU_SHIM = ROOT / "scripts/build/qemu-no-forward.sh"


class BuilderNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real_qemu = shutil.which("qemu-system-x86_64")

    def run_shim(self, args):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            fake_qemu = temp / "qemu-real"
            capture = temp / "captured-args"
            fake_qemu.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, sys\n"
                "with open(os.environ['CAPTURE_ARGS'], 'w') as f:\n"
                "    json.dump(sys.argv[1:], f)\n"
            )
            fake_qemu.chmod(0o700)
            environment = os.environ | {
                "UJWALOS_REAL_QEMU": str(fake_qemu),
                "CAPTURE_ARGS": str(capture),
            }
            result = subprocess.run(
                [str(QEMU_SHIM), *args], text=True, capture_output=True, env=environment
            )
            passed = json.loads(capture.read_text()) if capture.exists() else None
            return result, passed

    def test_strips_only_upstream_ssh_forward_and_preserves_qemu_arguments(self):
        try:
            from kiwi_boxed_plugin.defaults import Defaults
        except ImportError:
            self.skipTest("installed kiwi-boxed-plugin source is unavailable")
        network_args = Defaults.get_qemu_network_setup()
        self.assertEqual(network_args, ["-nic", "user,model=virtio,hostfwd=tcp::10022-:22"])
        qemu_args = ["-m", "6G", *network_args, "-fsdev", "local,id=fsdev0,path=/tmp/description"]
        result, passed = self.run_shim(qemu_args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            passed,
            ["-m", "6G", "-nic", "user,model=virtio", "-fsdev",
             "local,id=fsdev0,path=/tmp/description"],
        )
        self.assertFalse(any("hostfwd=" in arg for arg in passed))

    def test_fails_closed_when_upstream_network_arguments_change(self):
        for args in (
            ["-nic", "user,model=virtio"],
            ["-nic", "user,model=virtio,hostfwd=tcp::10022-:22,hostfwd=tcp::2222-:80"],
            ["-nic", "user,model=virtio,hostfwd=tcp::10023-:22"],
            ["-nic", "user,model=virtio,hostfwd=tcp::10022-:22",
             "-nic", "user,model=virtio,hostfwd=tcp::10022-:22"],
        ):
            with self.subTest(args=args):
                result, passed = self.run_shim(args)
                self.assertEqual(result.returncode, 90)
                self.assertIsNone(passed)

    def test_kiwi_qemu_lookup_resolves_the_shim_first(self):
        try:
            from kiwi.path import Path as KiwiPath
        except ImportError:
            self.skipTest("installed KIWI source is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            shim_link = Path(directory) / "qemu-system-x86_64"
            shim_link.symlink_to(QEMU_SHIM)
            environment = os.environ.copy()
            environment["PATH"] = directory + os.pathsep + environment["PATH"]
            self.assertEqual(
                KiwiPath.which("qemu-system-x86_64", custom_env=environment),
                str(shim_link),
            )

    @unittest.skipUnless(shutil.which("ss"), "ss is unavailable")
    def test_real_qemu_has_no_ssh_listener_with_filtered_network_arguments(self):
        if self.real_qemu is None:
            self.skipTest("qemu-system-x86_64 is unavailable")
        port = 10022
        with socket.socket() as probe:
            try:
                probe.bind(("0.0.0.0", port))
            except OSError:
                self.skipTest(f"TCP port {port} is already occupied")

        environment = os.environ | {"UJWALOS_REAL_QEMU": self.real_qemu}
        process = subprocess.Popen(
            [
                str(QEMU_SHIM), "-machine", "none", "-nodefaults", "-display", "none",
                "-monitor", "none", "-serial", "none", "-nic",
                "user,model=virtio,hostfwd=tcp::10022-:22",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        try:
            time.sleep(0.4)
            self.assertIsNone(process.poll(), "minimal QEMU instance exited early")
            listeners = subprocess.run(
                ["ss", "-ltnp"], check=True, capture_output=True, text=True
            ).stdout
            self.assertNotIn(f"pid={process.pid},", listeners)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.stderr:
                process.stderr.close()


if __name__ == "__main__":
    unittest.main()
