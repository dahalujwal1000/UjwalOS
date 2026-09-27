# UjwalOS branding assets

`root/` is the file tree installed by the `ujwalos-branding` RPM. The package
contains system defaults only. Plasma reads the global theme and its layout
script when creating a new shell configuration; user settings remain in
`~/.config`. The login appearance uses Plasma Login Manager's wallpaper
configuration, and the boot splash uses Plymouth's existing `two-step` module.

## Login (greeter) wallpaper location

`root/usr/lib/plasmalogin/plasmalogin.conf.d/50-ujwalos-wallpaper.conf` is not an
arbitrary choice. Plasma Login Manager 6.7.5 builds its greeter configuration
from four sources, in `PlasmaLoginSettings::getInstance()`
(`src/frontend/settings/plasmaloginsettings.cpp`), and KConfig gives priority to
the main file, then to `addConfigSources()` calls in reverse call order
(`KConfig::addConfigSources`, `src/core/kconfig.h`, KConfigCore 6.30.0):

| Priority | Path | Owner |
|----------|------|-------|
| highest | `/etc/plasmalogin.conf` | administrator |
| | `/usr/lib/plasmalogin/plasmalogin.conf.d/*` | packages, including this one |
| | `/usr/lib/plasmalogin/defaults.conf` | distribution |
| lowest | `/etc/plasmalogin.conf.d/*` | local drop-ins |

The distribution `defaults.conf` sets
`[Greeter][Wallpaper][org.kde.image][General] Image`, so a drop-in in
`/etc/plasmalogin.conf.d/` is shadowed and the greeter keeps the distribution
wallpaper. 0.2-1 and 0.2-2 shipped there and were therefore ineffective. An
administrator still overrides this package by editing `/etc/plasmalogin.conf`.

Two further details come from the same release: the greeter reads the key
`[Greeter] WallpaperPluginId` (`src/frontend/settings/plasmaloginsettingsbase.kcfg`;
`WallpaperPlugin` is silently ignored, so the packaged `defaults.conf` does not
set it and the plugin falls back to the schema default `org.kde.image`), and the
image wallpaper plugin resolves `Image` through
`KPackage::Package::setPath(QUrl::toLocalFile())`
(`wallpapers/image/plugin/imagebackend.cpp`, `.../utils/mediaproxy.cpp`), which
is why the value is a `file://` package path rather than a bare wallpaper name.
`plasma-apply-wallpaperimage` writes the same form.

The wallpaper at
`root/usr/share/wallpapers/UjwalOS/contents/images/1672x941.png` was generated
with the built-in image generation tool on 2026-09-27 for this project. The
eight Plymouth progress frames and the UjwalOS wordmark were generated from
original simple shapes and text with ImageMagick. No Fedora or KDE artwork was
copied. The wallpaper prompt was:

> Use case: stylized-concept
> Asset type: operating system desktop wallpaper for UjwalOS, Fedora KDE gaming desktop, landscape 16:9 widescreen
> Primary request: an original, polished bitmap wallpaper that evokes a powerful but calm workspace.
> Scene/backdrop: precise layered silhouettes of Himalayan ridgelines at dusk, with subtle geometric light paths reminiscent of circuits integrated into the terrain; atmospheric depth without blur.
> Style/medium: sophisticated digital matte painting, clean edges and restrained detail, not photographic and not a generic gradient.
> Composition/framing: 16:9 wide image; visual interest concentrated toward the right and lower center; generous quiet negative space on left for desktop icons and center for login text. No focal object that becomes cropped on 16:10 screens.
> Color palette: deep charcoal and indigo sky, cool teal highlights, gentle coral sunrise band; readable dark and light UI contrast.
> Constraints: no text, no logos, no watermark, no people, no stock desktop icons or UI, no orbs/bokeh. High fidelity, usable as desktop and login background.

Plymouth's `two-step` plugin requires `lock.png`, `entry.png`, and `bullet.png`
for its password prompt even on an unencrypted installation. The original
sprites in the theme were generated with
`scripts/build/generate-plymouth-prompts.sh branding/root/usr/share/plymouth/themes/ujwalos`.
Omitting `lock.png` caused the plugin to fail at `show_splash_screen` and fall
back to Fedora's `bgrt` theme in the installed VM.

`LicenseRef-UjwalOS-Internal` is an internal placeholder, not an external
redistribution license. See [licensing policy](../LICENSES/README.md).
