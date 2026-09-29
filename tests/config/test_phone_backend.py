import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "apps/phone-panel/backend.py"
SPEC = importlib.util.spec_from_file_location("phone_backend", SOURCE)
backend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backend)


class PhoneBackendTests(unittest.TestCase):
    def transport(self, paired=True, reachable=True, battery=42, requested=False, incoming=False):
        calls = []

        def call(path, interface, method, args):
            calls.append((path, interface, method, args))
            if method == "devices":
                return ["test_device"]
            if method in ("requestPairing", "unpair"):
                return None
            return {"name": "Test phone", "isPaired": paired,
                    "isPairRequested": requested, "isPairRequestedByPeer": incoming,
                    "verificationKey": "ABCD 1234",
                    "isReachable": reachable, "hasBattery": True, "charge": battery}[args[1]]
        return call, calls

    def test_snapshot(self):
        call, calls = self.transport()
        row = backend.snapshot(call)[0]
        self.assertEqual(row["battery"], "42%")
        self.assertTrue(row["paired"])
        self.assertTrue(all(c[2] in ("Get", "devices") for c in calls))
        self.assertEqual(row["id"], "test_device")

    def test_offline_and_unpaired_do_not_read_battery(self):
        for paired, reachable in [(True, False), (False, True), (False, False)]:
            call, calls = self.transport(paired, reachable)
            self.assertEqual(backend.snapshot(call)[0]["battery"], "Unavailable")
            self.assertEqual(len(calls), 6)

    def test_pair_request_is_explicit_and_never_accepts(self):
        call, calls = self.transport(paired=False)
        backend.perform_action(call, "test_device", "pair")
        self.assertEqual(calls[-1], (backend.device_path("test_device"),
                                    backend.DEVICE, "requestPairing", []))

    def test_stale_and_pending_pair_requests_are_rejected(self):
        for settings in ({}, {"paired": False, "reachable": False},
                         {"paired": False, "requested": True},
                         {"paired": False, "incoming": True}):
            call, calls = self.transport(**settings)
            with self.assertRaises(backend.Unavailable):
                backend.perform_action(call, "test_device", "pair")
            self.assertTrue(all(c[2] in ("Get", "devices") for c in calls))

    def test_unpair_works_offline(self):
        call, calls = self.transport(reachable=False)
        backend.perform_action(call, "test_device", "unpair")
        self.assertEqual(calls[-1][2], "unpair")

    def test_invalid_action_and_missing_target_cannot_mutate(self):
        for identifier, action in [("test_device", "acceptPairing"), ("gone", "unpair"),
                                   ("../invalid", "pair")]:
            call, calls = self.transport()
            with self.assertRaises(backend.Unavailable):
                backend.perform_action(call, identifier, action)
            self.assertTrue(all(c[2] in ("Get", "devices") for c in calls))

    def test_pending_request_has_verification_code(self):
        call, _ = self.transport(paired=False, requested=True)
        row = backend.snapshot(call)[0]
        self.assertEqual(row["verification"], "ABCD 1234")
        self.assertTrue(row["requested"])

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
