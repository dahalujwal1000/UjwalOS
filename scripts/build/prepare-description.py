#!/usr/bin/env python3
"""Verify the vendored source, then apply the deliberately small derivative."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def prepare(destination):
    inputs = json.loads((ROOT / "image/inputs.json").read_text())
    archive = ROOT / "image" / inputs["archive"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != inputs["archive_sha256"]:
        raise ValueError("Upstream archive checksum mismatch; refusing to compose")
    # Never reuse or delete a previous build tree.
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive) as source:
        source.extractall(destination, filter="data")
    # QEMU's mapped 9p export does not expose native host symlinks reliably.
    # Materialize the pinned repository alias; its bytes remain identical.
    alias = destination / "repositories/core.xml"
    if alias.is_symlink():
        content = alias.read_bytes()
        alias.unlink()
        alias.write_bytes(content)
    description = destination / inputs["kiwi_file"]
    original = description.read_text()
    needle = '<image schemaversion="7.4" name="Fedora">'
    if original.count(needle) != 1 or original.count("</image>") != 1:
        raise ValueError("Unexpected upstream description structure")
    derived = original.replace(needle, needle.replace('name="Fedora"',
                                                       f'name="{inputs["image_name"]}"'))
    derived = derived.replace("</image>",
                              '\t<include from="this://./ujwalos-packages.xml"/>\n</image>')
    ET.fromstring(derived)
    description.write_text(derived)
    liveinstall = destination / "components/liveinstall.xml"
    liveinstall_tree = ET.parse(liveinstall)
    types = liveinstall_tree.findall("./preferences[@profiles='LiveInstall'][@arch='x86_64']/type")
    if len(types) != 1 or types[0].get("filesystem") != "erofs" or \
            types[0].get("fscreateoptions") != "-Efragments -C 1048576":
        raise ValueError("Unexpected upstream x86-64 live filesystem options")
    types[0].set("fscreateoptions", "-C 1048576")
    liveinstall_tree.write(liveinstall, encoding="unicode")
    config = destination / "config.sh"
    script = config.read_text()
    ending = "\nexit 0\n"
    if script.count(ending) != 1:
        raise ValueError("Unexpected upstream config.sh ending")
    script = script.replace(ending,
        "\n# Kernel RPM hooks can leave KIWI's temporary root in GRUB's BLS search path.\n"
        "if [[ \"$kiwi_profiles\" == *Live* ]]; then\n"
        "    grub2-editenv /boot/grub2/grubenv unset blsdir\n"
        "fi\n" + ending)
    config.write_text(script)
    shutil.copyfile(ROOT / "image/compose/packages.xml", destination / "ujwalos-packages.xml")
    # Official boxed-builder hook: copied into the disposable builder, not ISO.
    shutil.copytree(ROOT / "image/compose/boxroot", destination / "boxroot")
    manifest = {}
    for file in sorted(destination.rglob("*")):
        if file.is_file():
            manifest[str(file.relative_to(destination))] = hashlib.sha256(file.read_bytes()).hexdigest()
    (destination.parent / "description-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Prepared {inputs['image_name']} from {inputs['upstream_commit']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    prepare(args.destination)
