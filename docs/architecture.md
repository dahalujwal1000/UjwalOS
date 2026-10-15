# Architecture

Status reconciled 2026-10-15: the newest ISO, containing apps 0.1-4 and the
security source fixes, passed compose and media checks. Live boot and installation
are pending. The older 2026-09-30 image passed live Plasma boot. Stages 1 and 2
acceptance passed on earlier recorded images; Stage 3 optional setup is
implemented with acceptance pending. Stages 4/5 previews are packaged, Stage 6
is unimplemented, and Stage 7 has artifact verification/recovery documentation
but open operational and security gates. See the
[acceptance summary](status.md#current-acceptance-summary) for detailed evidence.

```text
UEFI → Fedora-supported boot chain → Fedora kernel/initramfs → systemd
     → KDE Plasma / Wayland → packaged UjwalOS defaults and applications
     → optional Steam/Proton and opt-in KDE Connect
```

Use Fedora KDE 44 x86-64 with conventional RPM package updates and a KIWI-built
live/install ISO. [ADR 0001](decisions/0001-image-strategy.md) records the choice.
An ISO build tool does not imply an immutable or image-based update model.

Keep Fedora kernel, firmware, Mesa, audio, power management, and boot security.
Preserve diagnostics and recovery entries. Follow Fedora's installer and
first-run setup instead of designing an installer. Fedora 44's KDE changes
include Plasma Login Manager and Plasma Setup; do not assume SDDM or invent
configuration APIs. Verify these against the pinned definition before composing.

The versioned `ujwalos-branding` RPM owns the new desktop appearance and boot
assets. First-login defaults must allow user changes to survive updates. Plasma
Login Manager uses its supported wallpaper configuration rather than an SDDM
theme; login validation follows a fresh image boot/install test.

The Stage 4 Qt 6/QML profile editor runs as the user, stores requested settings
under Qt's application config directory and locks out competing instances.
Apps RPM 0.1-4 adds bounded, nonblocking profile-file reads and matching save
limits; rejected files are preserved. The 2026-10-15 configuration regression
suite passed these cases. The editor does not execute games or mutate system
settings. See
[Gaming Center requirements](gaming-center.md) for its pending integration gates.
Reuse KDE Connect's supported
interfaces for local continuity. A privileged helper is deferred until a
specific operation needs it; define a narrow D-Bus/PolicyKit contract first.
Gaming Mode must journal previous state and restore it on disable, game exit,
crash, and reboot. Do not implement performance changes until this is tested.

The Stage 5 phone status panel uses read-only user-session KDE Connect D-Bus
queries on explicit refresh, with no service activation, phone-data persistence
or private pairing-key access. Explicit, confirmed unpair requests are
revalidated before dispatch. Pairing, acceptance and cancellation are delegated
to KDE Connect's native UI via an explicit launcher; direct pairing D-Bus calls
are blocked. Launching the native UI may activate its service. KDE Connect owns
trust; the panel displays public verification codes for pending requests.
It does not transfer phone content.
See [phone-panel.md](phone-panel.md) for the remaining privacy and acceptance gates.

No custom kernel, Android runtime fork, mandatory account, cloud service,
Waydroid integration, or broad game compatibility promise is part of v0.1.

Source: [Fedora 44 change set](https://fedoraproject.org/wiki/Releases/44/ChangeSet)
and [KDE first-run changes](https://fedoraproject.org/wiki/Changes/Unified_KDE_OOBE),
checked 2026-09-26. These documents inform planning, not test results.
