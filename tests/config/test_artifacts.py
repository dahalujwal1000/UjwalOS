import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "scripts/release/artifacts.py"
SPEC = importlib.util.spec_from_file_location("artifacts", SOURCE)
artifacts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(artifacts)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        (self.directory / "test.iso").write_bytes(b"synthetic ISO fixture")

    def create(self):
        return artifacts.create(self.directory, ["test.iso"], "a" * 40)

    def test_round_trip(self):
        document = self.create()
        self.assertEqual(document, artifacts.verify(self.directory))

    def test_tampering_and_missing_file(self):
        self.create()
        (self.directory / "test.iso").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            artifacts.verify(self.directory)
        (self.directory / "test.iso").unlink()
        with self.assertRaises(OSError):
            artifacts.verify(self.directory)

    def test_paths_duplicates_and_revision(self):
        for name in ("../test.iso", "/test.iso", "a/b", artifacts.MANIFEST, "bad\nname"):
            with self.assertRaises(ValueError):
                artifacts.create(self.directory, [name], "a" * 40)
        with self.assertRaises(ValueError):
            artifacts.create(self.directory, ["test.iso"] * 2, "a" * 40)
        with self.assertRaises(ValueError):
            artifacts.create(self.directory, ["test.iso"], "main")

    def test_symlink_and_fifo_refused(self):
        (self.directory / "link.iso").symlink_to("test.iso")
        os.mkfifo(self.directory / "pipe.iso")
        for name in ("link.iso", "pipe.iso"):
            with self.assertRaises((OSError, ValueError)):
                artifacts.fingerprint(self.directory, name)

    def test_manifest_not_overwritten(self):
        self.create()
        original = (self.directory / artifacts.MANIFEST).read_bytes()
        with self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual((self.directory / artifacts.MANIFEST).read_bytes(), original)

    def test_strict_schema(self):
        original = self.create()
        for key, value in (("schema", True), ("classification", "release-approved"),
                           ("artifacts", []), ("source_revision", "HEAD")):
            document = dict(original, **{key: value})
            with self.assertRaises(ValueError):
                artifacts.validate(document)
        original["artifacts"][0]["size"] = True
        with self.assertRaises(ValueError):
            artifacts.validate(original)

    def test_duplicate_json_and_oversize_manifest(self):
        manifest = self.directory / artifacts.MANIFEST
        for content in ('{"schema":1,"schema":1}', " " * 65537):
            manifest.write_text(content)
            with self.assertRaises(ValueError):
                artifacts.verify(self.directory)

    def test_cli_success_and_failure(self):
        result = subprocess.run([sys.executable, str(SOURCE), "create", str(self.directory),
                                 "--revision", "a" * 40, "--artifact", "test.iso"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not release approval", result.stdout)
        (self.directory / "test.iso").write_bytes(b"tampered")
        result = subprocess.run([sys.executable, str(SOURCE), "verify", str(self.directory)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
