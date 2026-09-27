"""Tests for source integrity, bounded customization and safe refusal paths."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("prepare", ROOT / "scripts/build/prepare-description.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class ImageTests(unittest.TestCase):
    def test_pinned_source_and_bounded_derivative(self):
        inputs = json.loads((ROOT / "image/inputs.json").read_text())
        archive = ROOT / "image" / inputs["archive"]
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), inputs["archive_sha256"])
        with tempfile.TemporaryDirectory() as tmp:
            derived = Path(tmp) / "description"
            prepare.prepare(derived)
            with tarfile.open(archive) as upstream:
                for member in upstream.getmembers():
                    if member.isfile() and member.name not in ("Fedora.kiwi", "components/liveinstall.xml", "config.sh"):
                        self.assertEqual((derived / member.name).read_bytes(),
                                         upstream.extractfile(member).read(), member.name)
            tree = ET.parse(derived / "Fedora.kiwi")
            self.assertEqual(tree.getroot().get("name"), "UjwalOS-0.1")
            self.assertEqual(tree.findtext("preferences/release-version"), "44")
            self.assertEqual(tree.findtext("preferences/packagemanager"), "dnf5")
            liveinstall = ET.parse(derived / "components/liveinstall.xml")
            x86_type = liveinstall.find("./preferences[@profiles='LiveInstall'][@arch='x86_64']/type")
            self.assertEqual(x86_type.get("fscreateoptions"), "-C 1048576")
            self.assertEqual(x86_type.get("erofscompression"), "lzma,level=6")
            with tarfile.open(archive) as upstream:
                original_liveinstall = ET.fromstring(upstream.extractfile("components/liveinstall.xml").read())
                original_config = upstream.extractfile("config.sh").read().decode()
            original_liveinstall.find("./preferences[@profiles='LiveInstall'][@arch='x86_64']/type").set(
                "fscreateoptions", "-C 1048576")
            self.assertEqual(ET.tostring(liveinstall.getroot()), ET.tostring(original_liveinstall))
            expected_config = original_config.replace(
                "\nexit 0\n",
                "\n# Kernel RPM hooks can leave KIWI's temporary root in GRUB's BLS search path.\n"
                'if [[ "$kiwi_profiles" == *KDE-Desktop-Live* ]]; then\n'
                '    rpm -Uvh /image/ujwalos-branding.rpm\n'
                '    plymouth-set-default-theme ujwalos\n'
                '    rm /image/ujwalos-branding.rpm\n'
                'fi\n'
                'if [[ "$kiwi_profiles" == *Live* ]]; then\n'
                '    grub2-editenv /boot/grub2/grubenv unset blsdir\n'
                'fi\n\nexit 0\n',
            )
            self.assertEqual((derived / "config.sh").read_text(), expected_config)
            package = derived / "root/image/ujwalos-branding.rpm"
            self.assertTrue(package.is_file())
            self.assertEqual(subprocess.check_output(["rpm", "-qp", "--scripts", str(package)],
                                                     text=True), "")
            paths = subprocess.check_output(["rpm", "-qpl", str(package)], text=True)
            self.assertFalse(any(path.startswith(("/home/", "/root/")) for path in paths.splitlines()))
            self.assertIn("/usr/share/wallpapers/UjwalOS/contents/images/1672x941.png", paths)
            self.assertIn("/etc/xdg/kdeglobals", paths)
            self.assertIn("/etc/xdg/kicker-extra-favoritesrc", paths)
            self.assertIn("/etc/plasmalogin.conf.d/50-ujwalos-wallpaper.conf", paths)
            self.assertIn("/usr/share/plymouth/themes/ujwalos/ujwalos.plymouth", paths)
            self.assertIn("/usr/share/plymouth/themes/ujwalos/watermark.png", paths)
            self.assertFalse((derived / "repositories/core.xml").is_symlink())
            self.assertEqual((derived / "repositories/core.xml").read_bytes(),
                             (derived / "repositories/core-nonrawhide.xml").read_bytes())
            self.assertIn("isomd5sum", (derived / "boxroot/etc/kiwi.yml.d/ujwalos.yml").read_text())
            extra = ET.parse(derived / "ujwalos-packages.xml")
            self.assertEqual([p.get("name") for p in extra.findall("packages/package")], ["kde-connect"])
            before = (derived / "config.sh").read_bytes()
            with self.assertRaises(FileExistsError):
                prepare.prepare(derived)
            self.assertEqual(before, (derived / "config.sh").read_bytes())

    def test_shell_syntax(self):
        for path in ("scripts/build/build-iso.sh", "scripts/build/build-branding-rpm.sh",
                     "scripts/test/test-iso.sh"):
            subprocess.run(["bash", "-n", str(ROOT / path)], check=True)

    def test_missing_iso_refused(self):
        result = subprocess.run([str(ROOT / "scripts/test/test-iso.sh"),
                                 "/definitely-missing-ujwalos.iso", "--check-only"],
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ISO must be an existing regular file", result.stderr)

    def test_checksum_mismatch_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.iso"
            path.write_bytes(b"not an ISO")
            (Path(tmp) / "SHA256SUMS").write_text("0" * 64 + "  bad.iso\n")
            result = subprocess.run([str(ROOT / "scripts/test/test-iso.sh"), str(path), "--check-only"],
                                    text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("checksum mismatch", result.stderr)

    def test_vm_uses_private_disk_and_acceleration_fallback(self):
        # Synthetic media only tests catalog/launch plumbing, never OS boot.
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            root = Path(tmp)
            entry = root / "scripts/test/test-iso.sh"
            entry.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "scripts/test/test-iso.sh", entry)
            entry.chmod(0o755)
            media = root / "media"
            media.mkdir()
            (media / "efi.img").write_bytes(bytes(1024 * 1024))
            iso = root / "fixture.iso"
            subprocess.run(["xorriso", "-as", "mkisofs", "-o", str(iso),
                            "-e", "efi.img", "-no-emul-boot", str(media)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (root / "SHA256SUMS").write_text(hashlib.sha256(iso.read_bytes()).hexdigest() + "  fixture.iso\n")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            qemu = fake_bin / "qemu-system-x86_64"
            qemu.write_text('#!/usr/bin/env python3\nimport json, os, sys\nfrom pathlib import Path\nPath(os.environ["CAPTURE"]).write_text(json.dumps(sys.argv[1:]))\n')
            qemu.chmod(0o755)
            capture = root / "args.json"
            env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ["PATH"], CAPTURE=str(capture))
            subprocess.run([str(entry), str(iso), "--headless"], env=env,
                           check=True, stdout=subprocess.DEVNULL)
            args = json.loads(capture.read_text())
            expected_accel = "kvm" if os.access("/dev/kvm", os.R_OK | os.W_OK) else "tcg"
            self.assertEqual(args[args.index("-accel") + 1], expected_accel)
            vm = next((root / "out").glob("vm-*"))
            self.assertIn(f"file={vm}/disk.qcow2,format=qcow2,if=virtio", args)
            self.assertIn(f"file={iso},media=cdrom,format=raw,readonly=on", args)
            self.assertIn(f"unix:{vm}/vnc.sock", args)
            self.assertIn(f"unix:{vm}/qmp.sock,server=on,wait=off", args)
            subprocess.run([str(entry), "--installed", str(vm), "--headless"], env=env,
                           check=True, stdout=subprocess.DEVNULL)
            installed_args = json.loads(capture.read_text())
            self.assertFalse(any("media=cdrom" in arg for arg in installed_args))


if __name__ == "__main__":
    unittest.main()
