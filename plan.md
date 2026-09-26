# UjwalOS master plan

## Execution boundary

The owner originally requested fundamentals first, then explicitly authorized
Stage 1 implementation in the next task. Stage 1 work is now authorized; the
specification below remains the original product scope, not a feature-status claim.

The full master prompt follows. Current decisions and evidence are maintained
in docs/; do not silently rewrite the original requirements when a decision changes.

---

# Master Codex Prompt: Build UjwalOS

You are the lead systems architect and implementation engineer for **UjwalOS**, a Fedora-based, lightweight gaming desktop operating system with a familiar Windows-style interface and deep Android phone integration.

Work inside this repository. Treat this prompt as the product specification, but verify all version-sensitive technical details against current upstream documentation before choosing commands, packages, APIs, or image-building tools.

## 1. Product goal

Build an installable, maintainable x86-64 Linux distribution that provides:

1. A fast, polished KDE Plasma desktop with familiar taskbar, launcher, tray, window controls, shortcuts, and settings.
2. Reliable Linux gaming through Steam and Proton, with optional gaming utilities.
3. Strong Android phone continuity: pairing, notifications, clipboard, files, battery information, and later advanced features.
4. A distinctive UjwalOS visual identity across the desktop, login screen, and boot splash.
5. Safe updates, straightforward recovery, hardware compatibility, and clear failure messages.
6. A reproducible bootable image that can be tested in a VM before installation on hardware.

The primary development and test machine may be a Fedora laptop with hybrid Intel/NVIDIA graphics, an RTX 3050, 16 GB RAM, and UEFI/Secure Boot. Do not assume that one laptop represents all supported hardware.

## 2. Core architecture

Use this baseline:

```text
UEFI firmware
    → Fedora-supported boot chain
    → Fedora kernel and initramfs
    → systemd services
    → KDE Plasma on Wayland
    → UjwalOS desktop configuration and applications
    → Steam/Proton gaming and KDE Connect phone integration
```

Use Fedora’s supported kernel and security update path. **Do not fork the kernel, bootloader, display server, desktop environment, or Android runtime in the first releases.**

Own the UjwalOS configuration, branding, packages, applications, integration code, documentation, build pipeline, and test pipeline. Prefer upstream fixes to permanent downstream patches.

Choose **one image and update strategy for v0.1** after checking current Fedora tooling:

- Default candidate: conventional Fedora KDE live/install image using Fedora’s supported compose workflow and RPM packages.
- Alternative: an image-based Fedora approach only if it demonstrably simplifies installation, updates, rollback, and third-party gaming software for this project.

Record the decision and tradeoffs in `docs/decisions/0001-image-strategy.md`. Do not mix both approaches in the same initial release.

## 3. Architecture rules

- **Boot and recovery are critical.** Keep bootloader customization limited to supported configuration and visual assets. Use Plymouth for the animated boot splash. Preserve access to recovery entries and boot diagnostics.
- **Desktop customization is packaged.** Ship Plasma layout, theme, wallpapers, shortcuts, and defaults through versioned packages or declarative configuration. Avoid scripts that repeatedly overwrite a user’s personal settings after first login.
- **Every system change is reversible.** Gaming Mode must restore previous settings when disabled, when a game exits unexpectedly, and after a crash or reboot.
- **Use least privilege.** The graphical UI runs as the user. Privileged operations go through a narrow, documented system service with PolicyKit authorization. Never run the whole UI as root.
- **No silent hardware tweaks.** Do not disable essential services, thermal controls, security controls, or updates to claim better performance.
- **No invented compatibility claims.** Measure performance against stock Fedora KDE on the same hardware. Clearly distinguish supported games from games limited by anti-cheat or proprietary launchers.
- **Android integration is opt-in.** Ask for device permissions, protect pairing keys, encrypt communication, and provide unpair/revoke controls. Do not upload phone content to a cloud service by default.
- **No mandatory Ujwal account in v1.** Begin with local phone-to-PC pairing. Add a cloud identity only when a feature requires it and its security model is specified.
- **Proprietary software is optional.** Keep redistributable base images legally reviewable. Provide a user-initiated setup path for software or drivers that cannot be bundled.
- **Never claim an untested build works.** Separate code written, image built, VM booted, installation tested, and hardware tested in every progress report.

## 4. Proposed technology stack

| Area | Starting choice |
|---|---|
| Base OS | Current supported Fedora KDE release |
| Kernel | Fedora kernel; no custom fork |
| Desktop | KDE Plasma, Wayland first |
| Display/login | Fedora KDE defaults initially; customize after a reliable boot |
| Boot menu | Fedora-supported bootloader configuration |
| Boot splash | Plymouth theme |
| OS packages | RPM, built and installed through a documented pipeline |
| System services | systemd and D-Bus |
| Desktop UI | Qt 6/QML, with KDE frameworks where useful |
| Small build/config tools | Python and shell where appropriate |
| Gaming | Steam/Proton, with optional GameMode, MangoHud, Gamescope, and Heroic after validation |
| Android continuity | KDE Connect first |
| Android apps | Optional Waydroid experiment; feature-gated |
| Installation | Supported Fedora installer/image workflow |
| Test automation | Shell/Python checks, VM smoke tests, and targeted application tests |
| Release artifacts | Versioned image, checksums, build manifest, and release notes |

Verify that each dependency and package name exists for the selected Fedora release. Pin image inputs or document their versions so a build can be reproduced.

## 5. Kernel and driver plan

### v0.1–v1.0

- Use Fedora’s kernel, firmware, Mesa, audio stack, power management, and device drivers.
- Test Intel and AMD open drivers first in VMs and available hardware.
- Provide an optional NVIDIA installation flow with clear checks for hybrid graphics, kernel module readiness, and Secure Boot requirements.
- Do not force unsupported kernel flags or hardcode PCI IDs.
- Collect hardware diagnostics without collecting private user data.
- Maintain a hardware compatibility matrix with: hardware model, boot result, Wi-Fi, audio, suspend/resume, external display, GPU acceleration, gaming result, and known issues.

### Later kernel work

Consider kernel configuration changes only when there is a reproducible problem or benchmark. Document baseline, method, results, regression risk, and rollback. A custom kernel is **not** a v1 requirement.

## 6. User experience and design system

Design UjwalOS as its own product while retaining familiar desktop behavior.

### Desktop

- Bottom taskbar with application launcher, search, pinned apps, active windows, system tray, and clock.
- Clean dark and light themes; accessible contrast and scalable UI.
- Launcher sections for apps, games, recent items, phone, and settings.
- Standard window management and keyboard shortcuts.
- Defaults that remain usable at laptop resolution, high DPI, and external-monitor scale.

### Boot and login

- Minimal branded boot menu without hiding recovery or another installed OS.
- Plymouth splash with a simple logo and restrained animation.
- Consistent login theme.
- Fast path from power-on to a usable desktop; measure rather than invent a boot-time target.

### Gaming panel

- GameMode status and per-game settings.
- Optional FPS and performance overlay when the tools provide those metrics.
- CPU/GPU information only when reliably available.
- Clear distinction between a *requested* performance setting and one actually applied.
- One-click restoration of defaults.

### Phone panel

- Pair/unpair and device status.
- Battery, notifications, clipboard, and file transfer using KDE Connect capabilities.
- Permission and privacy controls.
- Advanced mirroring, webcam, calls, and activity handoff only after feasibility and platform limitations are documented.

Create a small design system: color tokens, type scale, spacing, icon rules, motion rules, and accessibility checks. Avoid copying Microsoft, Apple, or Google assets.

## 7. Android compatibility plan

Treat these as separate capabilities:

1. **Phone continuity:** KDE Connect provides the first implementation. Build UjwalOS UI around its supported interfaces rather than immediately writing a new protocol.
2. **Android applications on the PC:** evaluate Waydroid separately. Test graphics, audio, input, performance, security, distribution rights, and compatibility on real hardware.
3. **Advanced continuity:** investigate camera-as-webcam, screen mirroring, calls, and handoff individually. Specify phone permissions and Android platform limitations for each.

Do not promise that all APKs, banking apps, games, Google Play dependent apps, or DRM apps will run. Do not claim iPhone/Mac feature parity until individual features are implemented and tested.

## 8. Repository structure

Create or refine this structure based on the chosen Fedora build method:

```text
ujwalos/
├── README.md
├── AGENTS.md
├── LICENSES/
├── docs/
│   ├── product-spec.md
│   ├── architecture.md
│   ├── security-model.md
│   ├── compatibility.md
│   ├── build-and-test.md
│   ├── roadmap.md
│   ├── release-process.md
│   └── decisions/
├── image/
│   ├── manifests/
│   ├── compose/
│   └── installer/
├── packaging/
│   ├── ujwalos-branding/
│   ├── ujwalos-defaults/
│   ├── ujwalos-gaming/
│   └── ujwalos-phone/
├── desktop/
│   ├── plasma/
│   ├── login/
│   ├── plymouth/
│   ├── wallpapers/
│   └── icons/
├── apps/
│   ├── welcome/
│   ├── gaming-center/
│   └── phone-panel/
├── services/
│   └── privileged-helper/
├── integrations/
│   ├── kde-connect/
│   ├── steam/
│   └── waydroid/
├── scripts/
│   ├── build/
│   ├── test/
│   └── release/
├── tests/
│   ├── config/
│   ├── integration/
│   └── vm/
└── .github/
    └── workflows/
```

Only create directories needed for real work. Avoid empty placeholder projects that imply a feature exists.

## 9. Development stages and release gates

### Stage 0 — Specification and feasibility

Deliver architecture, image-strategy decision, dependency and licensing review, threat model, supported hardware targets, and an executable v0.1 build plan.

**Gate:** Another developer can follow the docs and identify the exact image inputs and build command.

### Stage 1 — Bootable v0.1

Produce a Fedora KDE based live image with minimal UjwalOS branding, package selection, installer path, checksum, and VM test instructions.

**Gate:** Image builds, boots to Plasma in a VM, launches the installer, installs to a blank virtual disk, and boots the installed system.

### Stage 2 — Desktop identity

Package the taskbar layout, launcher settings, theme, wallpaper, login appearance, and boot splash.

**Gate:** A newly created account gets the intended layout, while existing user customization survives an update.

### Stage 3 — Gaming foundation

Add an optional gaming setup experience and validate Steam/Proton, graphics drivers, controller input, and performance tools.

**Gate:** Document at least a small reproducible game test matrix with baseline comparisons. No blanket “all Windows games work” claim.

### Stage 4 — Gaming Center

Build the Qt/QML app and safe system integration for profiles, per-game settings, monitoring, and restoration.

**Gate:** Disabling a mode or crashing the app restores prior settings; privileged operations require authorization.

### Stage 5 — Android continuity

Integrate KDE Connect pairing, notifications, files, clipboard, and battery into a cohesive phone panel.

**Gate:** Pairing, revocation, reconnection, and permission changes work across a real Android phone and PC.

### Stage 6 — Optional Android apps

Prototype Waydroid behind an explicit install/enable action.

**Gate:** Document supported hardware, performance, known app failures, security assumptions, and how to remove it cleanly.

### Stage 7 — Recovery and release quality

Finish update guidance, recovery documentation, release automation, signed or verifiable artifacts as appropriate, accessibility, and hardware testing.

**Gate:** Clean install, update, failed-update recovery, dual-boot safety review, and repeated hardware smoke tests pass.

### Stage 8 — Public v1.0

Release only after installation and recovery have been tested beyond one developer laptop. Publish known limitations prominently.

## 10. Required engineering workflow

For each stage:

1. Inspect the repository and current upstream documentation.
2. Write a short implementation plan and list assumptions.
3. Implement the smallest complete milestone.
4. Build and run relevant tests.
5. Report exact commands and results.
6. Update architecture, compatibility, and release notes.
7. Identify remaining risks and propose the next bounded task.

Keep commits focused. Do not edit a user’s installed system while developing the distribution unless explicitly asked. Build and test in an isolated environment first. Never overwrite disks, modify boot entries on the host, or reboot the host as part of automated testing.

## 11. First task: start now

Begin with **Stage 0 and Stage 1**.

- Inspect the working directory and existing files.
- Verify the current Fedora KDE release and supported image-building workflow.
- Create the architecture decision and essential documentation.
- Set up the smallest viable image configuration and build scripts.
- If the environment has the required dependencies and resources, build the image and boot it in a VM.
- If building is blocked, still deliver a coherent repository with exact reproducible commands, identify the specific blocker, and distinguish unverified steps from tested steps.

At the end, report:

- Files created or changed.
- The selected image/update strategy and why.
- Build command and build result.
- VM boot and installation results, if run.
- Known limitations.
- The next concrete implementation task.

---

## Owner's appended instruction (original wording)

> on ujwal@desktop-4gneur2:~/Documents/UjwalOS$ first seup funadamental and all this orompt to readme or plan.md after setting up the fubdamentals ask me to start the project
