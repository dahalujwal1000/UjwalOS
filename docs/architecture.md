# Architecture

Status: Stage 1 implementation, 2026-09-27. See status.md for validation evidence.

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

Future versioned RPMs own branding, initial Plasma layout, wallpaper, Plymouth
assets, and integration defaults. First-login defaults must allow user changes
to survive updates. Login branding follows a proven baseline boot/install.

Future Qt 6/QML applications run as the user. Reuse KDE Connect's supported
interfaces for local continuity. A privileged helper is deferred until a
specific operation needs it; define a narrow D-Bus/PolicyKit contract first.
Gaming Mode must journal previous state and restore it on disable, game exit,
crash, and reboot. Do not implement performance changes until this is tested.

No custom kernel, Android runtime fork, mandatory account, cloud service,
Waydroid integration, or broad game compatibility promise is part of v0.1.

Source: [Fedora 44 change set](https://fedoraproject.org/wiki/Releases/44/ChangeSet)
and [KDE first-run changes](https://fedoraproject.org/wiki/Changes/Unified_KDE_OOBE),
checked 2026-09-26. These documents inform planning, not test results.
