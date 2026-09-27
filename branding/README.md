# UjwalOS branding assets

`root/` is the file tree installed by the `ujwalos-branding` RPM. The package
contains system defaults only. Plasma reads the global theme and its layout
script when creating a new shell configuration; user settings remain in
`~/.config`. The login appearance uses Plasma Login Manager's wallpaper
configuration, and the boot splash uses Plymouth's existing `two-step` module.

The wallpaper at
`root/usr/share/wallpapers/UjwalOS/contents/images/1672x941.png` was generated
with the built-in image generation tool on 2026-09-27 for this project. The
eight Plymouth progress frames were generated from original simple shapes with
ImageMagick. No Fedora or KDE artwork was copied. The wallpaper prompt was:

> A landscape 16:9 desktop wallpaper for UjwalOS: precise layered Himalayan
> ridgelines at dusk, subtle geometric light paths integrated into the terrain,
> clean digital matte-painting detail. Place visual interest on the right and
> lower center, with quiet space on the left for desktop icons and in the center
> for login text. Deep charcoal and indigo sky, cool teal highlights, gentle
> coral sunrise band. No text, logo, watermark, people, UI or bokeh.

`LicenseRef-UjwalOS-Internal` is an internal placeholder, not an external
redistribution license. See [licensing policy](../LICENSES/README.md).
