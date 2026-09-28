"""Unprivileged profile editor; no game or privileged process execution."""

import os
from pathlib import Path
import shutil
import sys

from PySide6.QtCore import QObject, Property, QLockFile, QStandardPaths, Signal, Slot
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from profiles import Profile, load_profiles, save_profiles


class Controller(QObject):
    changed = Signal()

    def __init__(self, path):
        super().__init__()
        self.path = Path(path)
        self.items = []
        self.message = ""
        self.writable = True
        self.tools = ""
        try:
            self.items = load_profiles(self.path)
        except (OSError, ValueError) as error:
            self.message = f"Cannot load profiles: {error}"
            self.writable = False
        self.refresh()

    @Property('QVariantList', notify=changed)
    def rows(self):
        return [dict(name=p.name, gamemode=p.gamemode, overlay=p.overlay,
                     options=p.launch_options()) for p in self.items]

    @Property(str, notify=changed)
    def error(self):
        return self.message

    @Property(bool, notify=changed)
    def canEdit(self):
        return self.writable

    @Property(str, notify=changed)
    def toolStatus(self):
        return self.tools

    @Slot()
    def refresh(self):
        self.tools = " | ".join(
            f"{name}: {'available' if shutil.which(command) else 'not found'}"
            for name, command in [("GameMode", "gamemoderun"),
                                  ("MangoHud", "mangohud"), ("Steam", "steam")])
        self.changed.emit()

    @Slot(str, result=bool)
    def hasIcon(self, name):
        return QIcon.hasThemeIcon(name)

    def _commit(self, items):
        if not self.writable:
            return False
        try:
            save_profiles(self.path, items)
        except (OSError, ValueError) as error:
            self.message = f"Cannot save profiles: {error}"
            self.changed.emit()
            return False
        self.items = items
        self.message = ""
        self.changed.emit()
        return True

    @Slot(int, str, bool, bool, result=bool)
    def save(self, index, name, gamemode, overlay):
        if index < -1 or index >= len(self.items):
            return False
        try:
            profile = Profile(name.strip(), gamemode, overlay)
        except ValueError as error:
            self.message = str(error)
            self.changed.emit()
            return False
        items = list(self.items)
        if index == -1:
            items.append(profile)
        else:
            items[index] = profile
        return self._commit(items)

    @Slot(int, result=bool)
    def remove(self, index):
        if not 0 <= index < len(self.items):
            return False
        return self._commit(self.items[:index] + self.items[index + 1:])

    @Slot(int, result=bool)
    def reset(self, index):
        if not 0 <= index < len(self.items):
            return False
        items = list(self.items)
        items[index] = items[index].reset()
        return self._commit(items)


def main():
    if os.geteuid() == 0:
        print("Run Gaming Center as your normal desktop user.", file=sys.stderr)
        return 1
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("UjwalOS")
    app.setApplicationName("GamingCenter")
    directory = Path(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation))
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = QLockFile(str(directory / "profiles.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        print("Gaming Center profile storage is already in use or cannot be locked.", file=sys.stderr)
        return 1
    controller = Controller(directory / "profiles.json")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("center", controller)
    engine.load(str(Path(__file__).with_name("Main.qml")))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
