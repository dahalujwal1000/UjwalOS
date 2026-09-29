"""Explicit KDE Connect operations; never log device data or activate services."""

import re
import time

SERVICE = "org.kde.kdeconnect"
ROOT = "/modules/kdeconnect"
DEVICE = SERVICE + ".device"


class Unavailable(RuntimeError):
    pass


def device_path(identifier):
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_]{1,128}", identifier):
        raise Unavailable("KDE Connect returned an invalid device identifier")
    return ROOT + "/devices/" + identifier


def snapshot(call):
    """The injected transport returns decoded D-Bus values, not CLI text."""
    identifiers = call(ROOT, SERVICE + ".daemon", "devices", [False, False])
    if (not isinstance(identifiers, list) or len(identifiers) > 64
            or any(not isinstance(identifier, str) for identifier in identifiers)):
        raise Unavailable("Unexpected KDE Connect device list")
    rows = []
    for identifier in dict.fromkeys(identifiers):
        path = device_path(identifier)

        def get(interface, property_name, object_path=path):
            return call(object_path, "org.freedesktop.DBus.Properties", "Get",
                        [interface, property_name])

        name = get(DEVICE, "name")
        paired = get(DEVICE, "isPaired")
        reachable = get(DEVICE, "isReachable")
        requested = get(DEVICE, "isPairRequested")
        incoming = get(DEVICE, "isPairRequestedByPeer")
        if not isinstance(name, str) or type(paired) is not bool or type(reachable) is not bool:
            raise Unavailable("Unexpected KDE Connect device properties")
        if type(requested) is not bool or type(incoming) is not bool:
            raise Unavailable("Unexpected KDE Connect pairing state")
        verification = ""
        if requested or incoming:
            verification = get(DEVICE, "verificationKey")
            if (not isinstance(verification, str) or len(verification) > 512
                    or any(not c.isprintable() for c in verification)):
                raise Unavailable("Unexpected verification code")
        battery = "Unavailable"
        if paired and reachable:
            try:
                has_battery = get(DEVICE + ".battery", "hasBattery", path + "/battery")
                charge = get(DEVICE + ".battery", "charge", path + "/battery")
                if has_battery is True and type(charge) is int and 0 <= charge <= 100:
                    battery = f"{charge}%"
            except Unavailable:
                pass
        # Names are untrusted display text, never a rich-text document or a path.
        name = "".join(c for c in name if c.isprintable())[:160] or "Unnamed device"
        rows.append({"id": identifier, "name": name, "paired": paired,
                     "reachable": reachable, "battery": battery,
                     "requested": requested, "incoming": incoming,
                     "verification": verification})
    return sorted(rows, key=lambda row: row["name"].casefold())


def perform_action(call, identifier, action):
    """Revalidate a confirmed target. Never accept inbound pairing requests."""
    path = device_path(identifier)
    if action != "unpair":
        raise Unavailable("Unsupported action")
    row = next((row for row in snapshot(call) if row["id"] == identifier), None)
    if row is None:
        raise Unavailable("Device no longer available")
    if not row["paired"]:
        raise Unavailable("Device is not paired")
    call(path, DEVICE, "unpair", [])


class SessionTransport:
    def __init__(self):
        self.deadline = time.monotonic() + 8

    def __call__(self, path, interface, method, arguments):
        # requestPairing may accept an inbound request racing a prior state check.
        if interface == DEVICE and method != "unpair":
            raise Unavailable("Pairing is managed in KDE Connect")
        from PySide6.QtDBus import QDBus, QDBusConnection, QDBusMessage, QDBusVariant

        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise Unavailable("KDE Connect refresh timed out")
        request = QDBusMessage.createMethodCall(SERVICE, path, interface, method)
        request.setAutoStartService(False)
        request.setArguments(arguments)
        reply = QDBusConnection.sessionBus().call(request, QDBus.Block,
                                                 max(1, min(1500, int(remaining * 1000))))
        if reply.type() == QDBusMessage.ErrorMessage:
            raise Unavailable("KDE Connect is unavailable or its interface could not be read")
        values = reply.arguments()
        if interface == DEVICE and method == "unpair" and not arguments:
            if values:
                raise Unavailable("Unexpected KDE Connect action reply")
            return None
        if len(values) != 1:
            raise Unavailable("Unexpected KDE Connect reply")
        value = values[0]
        return value.variant() if isinstance(value, QDBusVariant) else value
