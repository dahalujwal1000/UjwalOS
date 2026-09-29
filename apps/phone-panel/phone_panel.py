"""User-run Qt/QML phone status panel. Refresh is explicitly requested."""

import os
from pathlib import Path
import sys

from PySide6.QtCore import QObject, Property, QProcess, QThread, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend import SessionTransport, Unavailable, snapshot, perform_action


class Refresh(QThread):
    result = Signal(list, str)

    def run(self):
        try:
            self.result.emit(snapshot(SessionTransport()), "")
        except (Unavailable, TypeError, ValueError):
            self.result.emit([], "KDE Connect unavailable. No current device status.")


class Action(QThread):
    result = Signal(list, str)

    def __init__(self, identifier, action, parent):
        super().__init__(parent)
        self.identifier = identifier
        self.action = action

    def run(self):
        try:
            perform_action(SessionTransport(), self.identifier, self.action)
        except (Unavailable, TypeError, ValueError):
            # A transport timeout can occur after the daemon received the request.
            self.result.emit([], "Action could not be confirmed. Refresh before retrying.")
            return
        self.result.emit([], "Unpair request sent. Refresh to verify device status.")


class PhonePanel(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self._rows = []
        self._busy = False
        self._message = "Not refreshed"
        self.worker = None

    @Property('QVariantList', notify=changed)
    def devices(self):
        return self._rows

    @Property(bool, notify=changed)
    def busy(self):
        return self._busy

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Slot()
    def refresh(self):
        if self._busy:
            return
        self._busy = True
        self._rows = []
        self._message = "Refreshing"
        self.changed.emit()
        self.worker = Refresh(self)
        self.worker.result.connect(self.accept)
        self.worker.finished.connect(self.finished)
        self.worker.start()

    @Slot(str, str)
    def act(self, identifier, action):
        if self._busy or action != "unpair":
            return
        if not any(row.get("id") == identifier for row in self._rows):
            return
        self._busy = True
        self._rows = []
        self._message = "Checking current device state"
        self.changed.emit()
        self.worker = Action(identifier, action, self)
        self.worker.result.connect(self.accept)
        self.worker.finished.connect(self.finished)
        self.worker.start()

    @Slot()
    def openSettings(self):
        if self._busy:
            return
        started, _ = QProcess.startDetached("/usr/bin/kdeconnect-app", [])
        self._rows = []
        self._message = ("KDE Connect launch requested. Refresh after changing pairing."
                         if started else "KDE Connect could not be opened.")
        self.changed.emit()

    @Slot(list, str)
    def accept(self, rows, error):
        self._rows = [] if error else rows
        self._message = error or ("Refresh complete" if rows else "No devices found")
        self.changed.emit()

    @Slot()
    def finished(self):
        self._busy = False
        self.worker.deleteLater()
        self.worker = None
        self.changed.emit()

    def shutdown(self):
        if self.worker is not None:
            self.worker.wait()


def main():
    if os.geteuid() == 0:
        print("Run Phone Panel as your normal desktop user.", file=sys.stderr)
        return 1
    app = QGuiApplication(sys.argv)
    app.setApplicationName("UjwalOS Phone Panel")
    controller = PhonePanel()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("phone", controller)
    engine.load(str(Path(__file__).with_name("Main.qml")))
    if not engine.rootObjects():
        return 1
    app.aboutToQuit.connect(controller.shutdown)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
