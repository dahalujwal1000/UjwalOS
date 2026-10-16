# Stage 4 Gaming Center requirements

Started by owner request on 2026-09-28. Stage 3 remains incomplete; starting
this phase does not waive its real-game, baseline or hardware gates.

## Goal and acceptance

Deliver an unprivileged Qt 6/QML Gaming Center with per-game profiles,
optional performance monitoring, explicit requested versus applied state,
and restoration controls. Preserve Fedora RPM updates and existing preferences.

1. Profile editing, saving, deletion and reset work across application restarts.
   Invalid documents show an error without silently replacing user data.
2. UI remains usable with keyboard navigation, laptop-sized windows and high DPI.
   Missing tools and unavailable metrics show unavailable, never fabricated data.
3. Applying settings requires an explicit user action. A saved profile or command
   preview must never be reported as an applied performance mode.
4. Any privileged operation has a narrow typed service interface and PolicyKit
   caller authorization. No root UI, arbitrary command or shell passthrough.
5. System mutations require durable prior-state ownership and recovery tests for
   disable, game exit, app/service crash and reboot. Preserve concurrent external
   changes. Keep mutation controls unavailable until these tests pass.
6. Package and test in a disposable VM, then compose and test a fresh install.
   Report code, package, ISO, live boot, installed boot and hardware separately.

## Implementation sequence

- First milestone: validated profile model, private atomic local storage, fixed
  launch-option previews and reset of requested settings. No process execution.
- Next: Qt/QML profile editor and read-only tool/status adapter; dependency and
  license review, automated UI tests and accessibility checks.
- Then: define the exact system operations needed, their authorization and
  restoration contract, implement and fault-test them before enabling controls.
- Finally: RPM/image integration and VM acceptance. Hardware tests stay separate.

## Current evidence and limitations

`apps/gaming-center/main.py` and `Main.qml` provide a profile editor using
`profiles.py`: create, rename, save, delete with confirmation and reset, plus
read-only command availability. Qt's application config directory holds the
profiles, and QLockFile prevents competing editor instances. Atomic replacement prevents partial JSON
publication, but is not a privileged-state journal or a reboot-recovery claim.
Reset changes requested profile values, not live system settings or Steam files.
Source now includes opt-in aggregate CPU and estimated memory-use monitoring.
It is off at startup, samples every two seconds only while enabled, and discards
samples when disabled. It reads bounded `/proc/stat` and `/proc/meminfo` files
without commands, network access, process enumeration or saved telemetry.
CPU requires two valid samples; missing, malformed or reset counters display
unavailable. These are system metrics, not GPU/FPS or per-game applied state.
There is still no privileged helper. The previous editor is packaged in
`ujwalos-apps` 0.1-4 and included in the corrected engineering ISO
`out/build-6KtHtk1p/result/UjwalOS-0.1.x86_64-44-0.iso` recorded in
[status](status.md). System Python
does not have PySide6; tests use a repository-local virtual environment with
PySide6-Essentials 6.11.2. No host system packages were installed.

On 2026-10-15, the combined repository run passed 48 configuration, 13 UI
and 2 synthetic D-Bus tests (not all are Gaming Center tests). Stage 4 remains
incomplete: new-monitoring VM acceptance, accessibility and authorized
settings/restoration gates are open. The security review reproduced a local
profile-file blocking issue. Source fix dated 2026-10-15 uses nonblocking,
no-follow opens and regular-file checks, with a 256 KiB document limit and
256-profile limit on both load and save. Invalid files disable editing without
replacing the user's data. The 0.1-4 package is in the corrected ISO; compose
and media checks, live boot and installation passed on 2026-10-16. The new
monitoring source targets apps 0.1-5 and is not in that ISO.
Regression and image evidence is recorded in [status](status.md). Python's
[file descriptor APIs](https://docs.python.org/3/library/os.html#os.open)
were checked on 2026-10-15.

## Development and tests

Run as a normal desktop user, not root:

```sh
python3 -m venv out/stage4-venv
out/stage4-venv/bin/pip install -r apps/gaming-center/requirements-dev.txt
out/stage4-venv/bin/python apps/gaming-center/main.py
```

The application saves requested preferences only. It neither applies Steam
launch options nor launches a game, and tool availability is not active-state
monitoring. Application exit therefore has no system state to restore yet.

```sh
python3 -m unittest discover -s tests/config -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  out/stage4-venv/bin/python -m unittest discover -s tests/ui -v
```

Repeat the Qt command with `QT_SCALE_FACTOR=2` for high-DPI smoke coverage.
Set `UJWALOS_UI_SCREENSHOTS=out/stage4-ui` to save test screenshots.
Keyboard/screen-reader acceptance and real Plasma/Wayland tests remain open.

Monitoring semantics verified 2026-10-16 against Linux
[/proc documentation](https://www.kernel.org/doc/html/latest/filesystems/proc.html)
and Qt [QTimer](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTimer.html).
Memory usage is `(MemTotal - MemAvailable) / MemTotal`; CPU excludes idle and
iowait and does not double-count guest ticks already included in user/nice.

Verified 2026-09-28: Python documents same-filesystem atomic
[os.replace](https://docs.python.org/3/library/os.html#os.replace), and Qt provides
[QQmlApplicationEngine](https://doc.qt.io/qtforpython-6/PySide6/QtQml/QQmlApplicationEngine.html)
for the Python/QML frontend. Qt's
[QLockFile](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QLockFile.html) and
[QStandardPaths](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QStandardPaths.html)
provide instance locking and user-specific storage. Fixed wrapper names follow the upstream
sources recorded in [gaming setup](gaming-setup.md). Qt/Fedora package selection
was checked for image packaging; final project licensing and redistribution
clearance remain required before public release.

The goal tracker rejected creation of a Stage 4 goal because the unfinished
Stage 3 goal still exists. These repository requirements record the new scope
without falsely marking Stage 3 complete.
