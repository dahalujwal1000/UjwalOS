# Architecture

Status: Stages 1 and 2 VM acceptance passed; Stage 3 gaming foundation in
progress, 2026-09-28. See status.md for validation evidence.

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
It does not execute games or mutate system settings. See
[Gaming Center requirements](gaming-center.md) for its pending integration gates.
Reuse KDE Connect's supported
interfaces for local continuity. A privileged helper is deferred until a
specific operation needs it; define a narrow D-Bus/PolicyKit contract first.
Gaming Mode must journal previous state and restore it on disable, game exit,
crash, and reboot. Do not implement performance changes until this is tested.

The Stage 5 phone status panel uses read-only user-session KDE Connect D-Bus
queries on explicit refresh, with no service activation, phone-data persistence
or private pairing-key access. Explicit, confirmed pair/unpair requests are
revalidated before dispatch. KDE Connect owns trust; the panel displays public
verification codes for pending requests and never accepts inbound requests.
It does not transfer phone content.
See [phone-panel.md](phone-panel.md) for the remaining privacy and acceptance gates.

No custom kernel, Android runtime fork, mandatory account, cloud service,
Waydroid integration, or broad game compatibility promise is part of v0.1.

Source: [Fedora 44 change set](https://fedoraproject.org/wiki/Releases/44/ChangeSet)
and [KDE first-run changes](https://fedoraproject.org/wiki/Changes/Unified_KDE_OOBE),
checked 2026-09-26. These documents inform planning, not test results.
