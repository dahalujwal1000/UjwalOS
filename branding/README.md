# UjwalOS branding assets

`root/` is the file tree installed by the `ujwalos-branding` RPM. The package
contains system defaults only. Plasma reads the global theme and its layout
script when creating a new shell configuration; user settings remain in
`~/.config`. The login appearance uses Plasma Login Manager's wallpaper
configuration, and the boot splash uses Plymouth's existing `two-step` module.

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

`LicenseRef-UjwalOS-Internal` is an internal placeholder, not an external
redistribution license. See [licensing policy](../LICENSES/README.md).
