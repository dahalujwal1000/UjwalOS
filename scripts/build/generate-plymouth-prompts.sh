#!/usr/bin/env bash
set -Eeuo pipefail
[[ $# -eq 1 && -d $1 ]] || { echo 'Usage: generate-plymouth-prompts.sh EXISTING-THEME-DIR' >&2; exit 2; }
theme=$(cd -- "$1" && pwd -P)

# Plymouth's two-step plugin loads these even on systems without disk encryption.
magick -size 48x48 xc:none -fill none -stroke '#19a7ad' -strokewidth 3 \
    -draw 'path "M 15,22 L 15,17 C 15,5 33,5 33,17 L 33,22"' \
    -draw 'roundrectangle 11,21 37,40 3,3' "$theme/lock.png"
magick -size 192x28 xc:none -fill '#172d3b' -stroke '#19a7ad' -strokewidth 1 \
    -draw 'roundrectangle 1,1 190,26 3,3' "$theme/entry.png"
magick -size 10x10 xc:none -fill '#19a7ad' \
    -draw 'circle 5,5 5,1' "$theme/bullet.png"
