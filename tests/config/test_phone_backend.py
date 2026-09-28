import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "apps/phone-panel/backend.py"
SPEC = importlib.util.spec_from_file_location("phone_backend", SOURCE)
backend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backend)


class PhoneBackendTests(unittest.TestCase):
    def transport(self, paired=True, reachable=True, battery=42):
        calls = []

        def call(path, interface, method, args):
            calls.append((path, interface, method, args))
            if method == "devices":
                return ["test_device"]
            return {"name": "Test phone", "isPaired": paired,
                    "isReachable": reachable, "hasBattery": True, "charge": battery}[args[1]]
        return call, calls

    def test_snapshot(self):
        call, calls = self.transport()
        row = backend.snapshot(call)[0]
        self.assertEqual(row["battery"], "42%")
        self.assertTrue(row["paired"])
        self.assertTrue(all(c[2] in ("Get", "devices") for c in calls))
        self.assertNotIn("id", row)

    def test_offline_and_unpaired_do_not_read_battery(self):
        for paired, reachable in [(True, False), (False, True), (False, False)]:
            call, calls = self.transport(paired, reachable)
            self.assertEqual(backend.snapshot(call)[0]["battery"], "Unavailable")
            self.assertEqual(len(calls), 4)

    def test_invalid_battery_is_unknown(self):
        for charge in [-1, 101, True, "42"]:
            call, _ = self.transport(battery=charge)
            self.assertEqual(backend.snapshot(call)[0]["battery"], "Unavailable")

    def test_path_validation(self):
        for identifier in ["../other", "a/b", "", None, "a" * 129]:
            with self.assertRaises(backend.Unavailable):
                backend.device_path(identifier)

    def test_missing_plugin_is_unknown(self):
        call, _ = self.transport()

        def missing(path, interface, method, args):
            if path.endswith("/battery"):
                raise backend.Unavailable("disabled")
            return call(path, interface, method, args)
        self.assertEqual(backend.snapshot(missing)[0]["battery"], "Unavailable")

    def test_missing_service_is_not_empty_success(self):
        def missing(*args):
            raise backend.Unavailable("no service")
        with self.assertRaises(backend.Unavailable):
            backend.snapshot(missing)

    def test_bad_device_property_is_rejected(self):
        call, _ = self.transport(paired="true")
        with self.assertRaises(backend.Unavailable):
            backend.snapshot(call)
