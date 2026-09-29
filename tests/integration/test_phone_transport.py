"""Run only inside dbus-run-session, never against a personal session bus."""

from pathlib import Path
import sys
import unittest
import select
import subprocess

from PySide6.QtCore import QCoreApplication
from PySide6.QtDBus import QDBusConnection

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps/phone-panel"))
from backend import SERVICE, DEVICE, SessionTransport, Unavailable, snapshot, perform_action, device_path


class MissingServiceTests(unittest.TestCase):
    def test_missing_service_does_not_activate(self):
        app = QCoreApplication.instance() or QCoreApplication([])
        bus = QDBusConnection.sessionBus()
        self.assertTrue(bus.isConnected())
        self.assertFalse(bus.interface().isServiceRegistered(SERVICE).value())
        with self.assertRaises(Unavailable):
            snapshot(SessionTransport())
        self.assertFalse(bus.interface().isServiceRegistered(SERVICE).value())

    def test_populated_service_and_void_action_reply(self):
        app = QCoreApplication.instance() or QCoreApplication([])
        bus = QDBusConnection.sessionBus()
        self.assertFalse(bus.interface().isServiceRegistered(SERVICE).value())
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).with_name("phone_service_fixture.py"))],
            stdout=subprocess.PIPE, text=True)
        try:
            self.assertTrue(select.select([process.stdout], [], [], 5)[0], "Fixture not ready")
            self.assertEqual(process.stdout.readline().strip(), "ready")
            row = snapshot(SessionTransport())[0]
            self.assertEqual(row["name"], "Synthetic phone")
            self.assertFalse(row["requested"])
            perform_action(SessionTransport(), "test_device", "pair")
            row = snapshot(SessionTransport())[0]
            self.assertTrue(row["requested"])
            self.assertFalse(row["paired"])
            self.assertEqual(row["verification"], "ABCD 1234")
            # Exercise void unmarshalling separately from the state guard.
            self.assertIsNone(SessionTransport()(device_path("test_device"), DEVICE, "unpair", []))
            self.assertFalse(snapshot(SessionTransport())[0]["requested"])
            with self.assertRaises(Unavailable):
                SessionTransport()(device_path("test_device"), DEVICE, "unknownMethod", [])
        finally:
            process.terminate()
            process.wait(timeout=5)
            process.stdout.close()
        with self.assertRaises(Unavailable):
            snapshot(SessionTransport())
        self.assertFalse(bus.interface().isServiceRegistered(SERVICE).value())


if __name__ == "__main__":
    unittest.main()
