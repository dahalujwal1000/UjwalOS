"""Run with PySide6 available and QT_QPA_PLATFORM=offscreen."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QObject, QLockFile
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

SOURCE = Path(__file__).resolve().parents[2] / "apps/gaming-center"
sys.path.insert(0, str(SOURCE))
from main import Controller


class CenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_crud_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            center = Controller(path)
            self.assertTrue(center.save(-1, "Game", True, True))
            self.assertEqual(Controller(path).rows[0]["options"],
                             "gamemoderun mangohud %command%")
            self.assertTrue(center.save(0, "Renamed", False, True))
            self.assertTrue(center.reset(0))
            self.assertEqual(Controller(path).rows[0]["options"], "%command%")
            self.assertTrue(center.remove(0))
            self.assertEqual(Controller(path).rows, [])
            self.assertFalse(center.remove(-1))

    def test_corrupt_storage_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text("broken")
            center = Controller(path)
            self.assertFalse(center.canEdit)
            self.assertFalse(center.save(-1, "Game", False, False))
            self.assertEqual(path.read_text(), "broken")

    def test_failed_save_preserves_model(self):
        with tempfile.TemporaryDirectory() as directory:
            center = Controller(Path(directory) / "profiles.json")
            with patch("main.save_profiles", side_effect=OSError("read only")):
                self.assertFalse(center.save(-1, "Game", False, False))
            self.assertEqual(center.rows, [])
            self.assertIn("read only", center.error)

    def test_second_lock_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            first = QLockFile(str(Path(directory) / "lock"))
            second = QLockFile(str(Path(directory) / "lock"))
            self.assertTrue(first.tryLock(0))
            self.assertFalse(second.tryLock(0))
            first.unlock()
            self.assertTrue(second.tryLock(0))
            second.unlock()

    def test_qml_load_and_save(self):
        with tempfile.TemporaryDirectory() as directory:
            center = Controller(Path(directory) / "profiles.json")
            engine = QQmlApplicationEngine()
            warnings = []
            engine.warnings.connect(lambda errors: warnings.extend(str(e) for e in errors))
            engine.rootContext().setContextProperty("center", center)
            engine.load(str(SOURCE / "Main.qml"))
            self.assertTrue(engine.rootObjects(), warnings)
            window = engine.rootObjects()[0]
            self.assertIsInstance(window, QQuickWindow)
            window.findChild(QObject, "nameField").setProperty("text", "UI game")
            window.findChild(QObject, "mode").setProperty("checked", True)
            window.findChild(QObject, "saveButton").clicked.emit()
            QTest.qWait(100)
            self.assertEqual(center.rows[0]["name"], "UI game")
            self.assertTrue(center.rows[0]["gamemode"])
            for width, height in [(840, 600), (560, 500)]:
                window.setWidth(width)
                window.setHeight(height)
                QTest.qWait(100)
                screenshot = window.grabWindow()
                self.assertFalse(screenshot.isNull())
                if os.environ.get("UJWALOS_UI_SCREENSHOTS"):
                    destination = Path(os.environ["UJWALOS_UI_SCREENSHOTS"])
                    destination.mkdir(parents=True, exist_ok=True)
                    self.assertTrue(screenshot.save(str(destination / f"center-{width}.png")))
            self.assertEqual(warnings, [])
            window.close()
            del engine


if __name__ == "__main__":
    unittest.main()
