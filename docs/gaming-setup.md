# Stage 3 gaming setup and test protocol

Status: implementation in progress, checked 2026-09-28. No game performance or
compatibility result is claimed yet.

## Optional setup

The `ujwalos-gaming-setup` RPM adds a launcher in the KDE application menu and
the `ujwalos-gaming-setup` command. It contains only a script and desktop entry.
Run it as a normal user. `--status` reports installed packages, visible graphics
hardware and bound kernel drivers, Vulkan summary when available, and joystick
device nodes. `--plan`
lists the optional software without changing the machine.

The Fedora tools choice asks PolicyKit to run DNF5 for the fixed package set
`gamemode mangohud gamescope vulkan-tools`. DNF5 displays its transaction and
asks for confirmation. These packages are not preinstalled by the UjwalOS
gaming RPM. GameMode is not activated globally; individual games can request it
with Steam launch option `gamemoderun %command%`. Run
`ujwalos-gaming-setup --test-gamemode` after installation to invoke GameMode's
`gamemoded -t` self-test. MangoHud and Gamescope are optional per-game
tools; their presence does not prove better performance.
For a Steam game, use `mangohud %command%` to show the overlay. To test
Gamescope separately, use `gamescope -W 1280 -H 720 -- %command%` and keep the
same output resolution on the baseline. When testing Gamescope with an overlay,
use its `--mangoapp` option rather than wrapping the game in `mangohud`.
MangoHud can write local frame-time logs after `output_folder` is set; its
default logging toggle is Shift+F2. Do not upload logs to a third-party service
as part of the test protocol.

Steam is a separate choice. The script checks enabled repositories for a
`steam` package and then asks for an explicit `yes` before invoking DNF5. It
does not enable RPM Fusion or any other third-party repository. If none is
enabled, it points to RPM Fusion's configuration page. Proton is obtained and
selected within Steam; UjwalOS does not bundle or build it. The user remains
responsible for the selected repository and Valve account terms. NVIDIA driver
installation is outside this script; no automatic GPU switch, kernel module,
Secure Boot, or power profile change is performed.

### Source and redistribution review

Verified 2026-09-28: Fedora 44 publishes [GameMode](https://packages.fedoraproject.org/pkgs/gamemode/gamemode/),
[MangoHud](https://packages.fedoraproject.org/pkgs/mangohud/mangohud/),
[Gamescope](https://packages.fedoraproject.org/pkgs/gamescope/gamescope/fedora-44.html),
and [Vulkan tools](https://packages.fedoraproject.org/pkgs/vulkan-tools/vulkan-tools/index.html).
[Fedora's Mesa Vulkan drivers](https://packages.fedoraproject.org/pkgs/mesa/mesa-vulkan-drivers/index.html)
cover Intel and AMD hardware through the normal Fedora graphics stack. The
setup script checks the active kernel driver and Vulkan report; it does not
replace any driver. The optional NVIDIA path still needs a tested driver,
hybrid-GPU and Secure Boot procedure before it can be offered as an installer.
[GameMode upstream](https://github.com/FeralInteractive/gamemode) documents
`gamemoderun` and `gamemoded -t`. [Valve's Proton repository](https://github.com/ValveSoftware/Proton)
says most users should use the Proton builds supplied through Steam.
[MangoHud upstream](https://github.com/flightlessmango/MangoHud) documents
Steam launch options and local logging; [Gamescope upstream](https://github.com/ValveSoftware/gamescope)
documents nested launch and resolution flags.

Steam is proprietary software obtained from a third-party repository only
after the user's explicit action. [Valve's subscriber agreement](https://store.steampowered.com/subscriber_agreement/)
grants personal use and does not grant UjwalOS redistribution rights. The
UjwalOS ISO contains no Steam, Proton, NVIDIA proprietary driver, RPM Fusion
repository configuration, or game binaries. This is a source and packaging
review for an optional installer, not public-release legal clearance.

## Reproducible game matrix protocol

Use a stock Fedora KDE 44 install as baseline and the UjwalOS Stage 3 image on
the same physical machine. Record ISO hashes, package NEVRAs, kernel, Mesa,
GPU driver and Vulkan versions, display resolution and refresh rate, power
source/profile, Steam and Proton versions, game build, graphics settings,
controller model, and launch options. Run each benchmark or repeatable scene
at least three times per system after warm-up. Report median FPS, 1% low FPS,
frame-time variance, launch outcome and controller behavior. For failed runs,
record the error and the relevant log without account tokens or private paths.
Do not compare numbers from different GPUs, drivers, power states or scenes.

| Test | Stock Fedora KDE 44 | UjwalOS Stage 3 | Gate evidence |
| --- | --- | --- | --- |
| Native Linux game, repeatable scene | Not run | Not run | Three runs and frame-time capture on each image |
| Windows-only Steam game through Proton | Not run | Not run | Same Proton/game build and scene on each image |
| Controller input in a game | Not run | Not run | Device model, mapping, disconnect/reconnect result |
| GameMode request and restoration | Not run | Not run | `gamemoded -t`, per-game activation and post-exit state |
| MangoHud overlay | Not run | Not run | FPS/frame-time output and visibility in-game |
| Gamescope optional launch | Not run | Not run | Launch result, display mode and error log |

VM tests can verify package installation, menu entry and basic diagnostics but
do not establish physical GPU performance, hybrid GPU selection, Secure Boot
or controller support. Record those separately in `docs/status.md`.
