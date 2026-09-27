# Licensing and redistribution

No project-wide license has been selected by the owner yet. Repository setup
does not grant redistribution rights to third-party software or trademarks.
Choose a license for original code, documentation, and artwork before release.
The Stage 2 branding RPM currently uses `LicenseRef-UjwalOS-Internal` as an
internal placeholder; it is not a grant of redistribution rights. The original
wallpaper was generated for this project with the built-in image generation tool
on 2026-09-27. Decide and document its distribution terms before publication.

Keep Fedora and upstream package licenses and corresponding source obligations.
Before publication, inventory every RPM and bundled asset, record its license,
retain required notices, and review Fedora trademark/remix requirements.
Use original UjwalOS artwork; do not copy Microsoft, Apple, or Google assets.

Steam, NVIDIA proprietary drivers, codecs from outside Fedora, Heroic distribution
channels, and Android images require separate source/license review before any
optional installer is implemented. Do not bundle them in the initial base image.
This is a review policy, not a completed legal clearance.

The Stage 3 Steam choice uses only a repository already enabled by the user;
its source, no-bundling boundary and Valve terms are reviewed in
[gaming-setup.md](../docs/gaming-setup.md). No Steam or Proton binaries are
redistributed in the ISO. NVIDIA and Heroic installers remain unimplemented.

The vendored Fedora KIWI archive under `image/upstream/` is GPL-3.0-or-later;
its complete source, upstream attribution, and COPYING are retained. The absence
of a project-wide license does not replace that upstream license.
