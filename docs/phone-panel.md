# Stage 5 Android continuity

Started at the owner's request on 2026-09-28. Stages 3 and 4 retain their
outstanding validation and implementation gates; advancing does not close them.

## Requirements and acceptance

Build an unprivileged Qt/QML panel on KDE Connect's user-session interfaces,
without a new phone protocol, mandatory account, cloud relay or privileged UI.

1. Device discovery/status and unavailable-service states are accurate. Never
   interpret failure as an empty successful device list or unknown battery as 0%.
2. Pairing requires explicit user action and device verification; requests are
   not reported as successful pairing until KDE Connect confirms the state.
3. Unpair/revoke works for online and offline devices, and reconnection cannot
   silently restore revoked trust. KDE Connect owns all pairing keys.
4. Notifications, file transfer, clipboard and battery respect KDE Connect
   plugin settings and Android permissions. Transfers and clipboard disclosure
   require explicit consent; no phone content in diagnostic logs or cloud uploads.
5. Test real Android pairing, rejection, cancellation, revocation, network loss,
   reconnect, reboot and permission changes. Test two user accounts independently.
6. Package, integrate into an image, and verify both live and installed sessions.
   Report code, package, image, VM and real-device tests separately.

## Implemented milestones

`apps/phone-panel/` contains a Qt/QML status panel. Refresh explicitly
queries the already-running KDE Connect service on the user session bus. It
does not activate that service or trigger network rediscovery. Device status and
battery are snapshots labelled as such, not continuous monitoring. Work runs on
a background thread with bounded call timeouts and an eight-second query budget.
Refresh clears stale data; errors remain visible. Battery is read only for paired,
reachable devices, and missing plugins or invalid values show unavailable.

No identifiers or phone content are written to disk. Device names are displayed
as plain text, bounded and wrapped. The panel does not read notifications,
clipboard, messages, pairing certificates or file contents. Device IDs stay in
memory for stable action targeting. Pair/unpair requests require a confirmation
dialog and recheck current state before dispatch. Offline paired devices can be
unpaired. Pending/incoming requests cannot trigger another pair request; inbound
acceptance and request cancellation remain in KDE Connect's own UI.

Requests are not reported as completed pairing or revocation. Refresh shows the
daemon's current state and public verification code for pending requests; compare
codes before accepting on the phone. Transport errors have an uncertain outcome,
so refresh before retrying. No automatic retries, plugin-setting changes or
private-key access are added. KDE Connect owns trust and plugin permissions.

The updated source packages as `ujwalos-apps` 0.1-2. The existing engineering ISO
contains the read-only 0.1-1 panel; no new image or real-phone acceptance is claimed.

## Development and verification

Use the repository-local Qt environment from Stage 4, as a normal desktop user:

```sh
out/stage4-venv/bin/python apps/phone-panel/phone_panel.py
python3 -m unittest discover -s tests/config -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  out/stage4-venv/bin/python -m unittest discover -s tests/ui -v
dbus-run-session -- out/stage4-venv/bin/python tests/integration/test_phone_transport.py -v
```

Never run the transport integration test against a personal session bus. Repeat
the Qt tests with `QT_SCALE_FACTOR=2`; optional `UJWALOS_UI_SCREENSHOTS=out/stage5-ui`
saves screenshots containing synthetic fixtures only. Qt dependencies remain the
Stage 4 development pins, not Fedora packaging clearance.

KDE Connect is absent on this development host. Mocked transport tests establish
local handling, not compatibility with the image's actual KDE Connect version.
The private-bus tests verify real Qt D-Bus missing-service handling without
activation, plus a synthetic populated service, properties and void action replies.
This fixture is not a real KDE Connect compatibility test.
The current-apps live ISO also passed launch and refresh to the real
KDE Connect empty-device result in Plasma. Device properties, real-phone tests
and broader Plasma/Wayland acceptance remain pending. Next test pairing/rejection,
offline revocation and reconnect against real KDE Connect and an Android phone.

## Upstream interfaces

Verified 2026-09-28 against upstream source (interfaces must also be checked
against the Fedora image package before packaging):

- [Daemon](https://github.com/KDE/kdeconnect-kde/blob/master/core/daemon.h):
  `devices(bool, bool)` on `org.kde.kdeconnect.daemon`.
- [Device](https://github.com/KDE/kdeconnect-kde/blob/master/core/device.h):
  `name`, `isPaired`, `isReachable`; per-device object paths.
- [Device v26.08.1](https://github.com/KDE/kdeconnect-kde/blob/v26.08.1/core/device.h):
  checked 2026-09-28 for `requestPairing`, `unpair`, `isPairRequested`,
  `isPairRequestedByPeer` and `verificationKey`; matches the ISO package version.
- [Battery plugin](https://github.com/KDE/kdeconnect-kde/blob/master/plugins/battery/batteryplugin.h):
  `hasBattery` and `charge`; unavailable charge can be negative.
- [CLI implementation](https://github.com/KDE/kdeconnect-kde/blob/master/cli/kdeconnect-cli.cpp):
  service and object naming and separate pairing/transfer operations.

The adapter is original integration code, not copied KDE source. KDE Connect
remains an upstream dependency; its licenses and notices must be preserved.
Project licensing and redistribution clearance remain open as documented in
`LICENSES/README.md`.
