"""Run only inside dbus-run-session, never against a personal session bus."""

from pathlib import Path
import sys
import unittest

from PySide6.QtCore import QCoreApplication
from PySide6.QtDBus import QDBusConnection

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps/phone-panel"))
from backend import SERVICE, SessionTransport, Unavailable, snapshot


class MissingServiceTests(unittest.TestCase):
    def test_missing_service_does_not_activate(self):
        app = QCoreApplication.instance() or QCoreApplication([])
        bus = QDBusConnection.sessionBus()
        self.assertTrue(bus.isConnected())
        self.assertFalse(bus.interface().isServiceRegistered(SERVICE).value())
        with self.assertRaises(Unavailable):
            snapshot(SessionTransport())
        self.assertFalse(bus.interface().isServiceRegistered(SERVICE).value())


if __name__ == "__main__":
    unittest.main()
