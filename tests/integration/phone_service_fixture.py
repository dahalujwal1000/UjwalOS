"""Synthetic KDE Connect contract fixture, only for a private test bus."""

from PySide6.QtCore import ClassInfo, QObject, Property, QCoreApplication, QTimer, Slot
from PySide6.QtDBus import QDBusConnection


@ClassInfo(**{"D-Bus Interface": "org.kde.kdeconnect.daemon"})
class Daemon(QObject):
    @Slot(bool, bool, result="QStringList")
    def devices(self, paired, reachable):
        return ["test_device"]


@ClassInfo(**{"D-Bus Interface": "org.kde.kdeconnect.device"})
class Device(QObject):
    def __init__(self):
        super().__init__()
        self.paired = True

    name = Property(str, lambda self: "Synthetic phone")
    isPaired = Property(bool, lambda self: self.paired)
    isReachable = Property(bool, lambda self: True)
    isPairRequested = Property(bool, lambda self: False)
    isPairRequestedByPeer = Property(bool, lambda self: False)
    verificationKey = Property(str, lambda self: "ABCD 1234")

    @Slot()
    def unpair(self):
        self.paired = False


if __name__ == "__main__":
    app = QCoreApplication([])
    bus = QDBusConnection.sessionBus()
    daemon, device = Daemon(), Device()
    assert bus.registerObject("/modules/kdeconnect", daemon, QDBusConnection.ExportAllSlots)
    assert bus.registerObject("/modules/kdeconnect/devices/test_device", device,
                              QDBusConnection.ExportAllSlots | QDBusConnection.ExportAllProperties)
    assert bus.registerService("org.kde.kdeconnect")
    QTimer.singleShot(30000, app.quit)
    print("ready", flush=True)
    app.exec()
