import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

SOURCE = Path(__file__).resolve().parents[2] / "apps/phone-panel"
sys.path.insert(0, str(SOURCE))
from phone_panel import PhonePanel
from backend import Unavailable


class PhonePanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_idle_does_not_access_service(self):
        with patch("phone_panel.SessionTransport") as transport:
            panel = PhonePanel()
            self.assertEqual(panel.message, "Not refreshed")
            self.assertEqual(panel.devices, [])
            transport.assert_not_called()

    def test_error_clears_old_data(self):
        panel = PhonePanel()
        panel.accept([{"name": "Old phone"}], "")
        panel.accept([], "Service unavailable")
        self.assertEqual(panel.devices, [])
        self.assertEqual(panel.message, "Service unavailable")

    def test_worker_failure_and_repeat_refresh(self):
        panel = PhonePanel()
        with patch("phone_panel.snapshot", side_effect=Unavailable("private detail")) as query:
            panel.refresh()
            panel.refresh()
            for _ in range(100):
                QTest.qWait(10)
                if not panel.busy:
                    break
            panel.shutdown()
            self.assertFalse(panel.busy)
            self.assertEqual(query.call_count, 1)
            self.assertEqual(panel.devices, [])
            self.assertNotIn("private detail", panel.message)

    def test_qml_states_and_rendering(self):
        panel = PhonePanel()
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda errors: warnings.extend(str(e) for e in errors))
        engine.rootContext().setContextProperty("phone", panel)
        engine.load(str(SOURCE / "Main.qml"))
        self.assertTrue(engine.rootObjects(), warnings)
        window = engine.rootObjects()[0]
        self.assertIsInstance(window, QQuickWindow)
        panel.accept([
            {"name": "Test Android phone", "paired": True, "reachable": True, "battery": "42%"},
            {"name": "<b>Untrusted name</b> " + "x" * 120, "paired": True,
             "reachable": False, "battery": "Unavailable"},
        ], "")
        for width, height in [(720, 520), (420, 340)]:
            window.setWidth(width)
            window.setHeight(height)
            QTest.qWait(100)
            screenshot = window.grabWindow()
            self.assertFalse(screenshot.isNull())
            if os.environ.get("UJWALOS_UI_SCREENSHOTS"):
                destination = Path(os.environ["UJWALOS_UI_SCREENSHOTS"])
                destination.mkdir(parents=True, exist_ok=True)
                self.assertTrue(screenshot.save(str(destination / f"phone-{width}.png")))
        panel.accept([], "KDE Connect unavailable")
        QTest.qWait(50)
        self.assertEqual(warnings, [])
        window.close()
        del engine
