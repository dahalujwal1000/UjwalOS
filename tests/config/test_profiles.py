import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[2] / "apps/gaming-center/profiles.py"
SPEC = importlib.util.spec_from_file_location("gaming_profiles", SOURCE)
profiles = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = profiles
SPEC.loader.exec_module(profiles)
Profile = profiles.Profile


class ProfileTests(unittest.TestCase):
    def test_fixed_launch_options(self):
        for mode, overlay, expected in [
            (False, False, "%command%"),
            (True, False, "gamemoderun %command%"),
            (False, True, "mangohud %command%"),
            (True, True, "gamemoderun mangohud %command%"),
        ]:
            self.assertEqual(Profile("$(untrusted)", mode, overlay).launch_options(), expected)

    def test_reset_is_local_and_immutable(self):
        original = Profile("Game", True, True)
        self.assertEqual(original.reset(), Profile("Game"))
        self.assertTrue(original.gamemode)

    def test_invalid_values(self):
        for name in ["", "  ", "bad\nname", "a" * 121, None]:
            with self.assertRaises(ValueError):
                Profile(name)
        for value in [1, "false", None]:
            with self.assertRaises(ValueError):
                Profile("Game", value)

    def test_round_trip_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            self.assertEqual(profiles.load_profiles(path), [])
            items = [Profile("Game", True)]
            profiles.save_profiles(path, items)
            self.assertEqual(profiles.load_profiles(path), items)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_existing_version_one_document_remains_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text('{"version":1,"profiles":[{"name":"Legacy",'
                            '"gamemode":true,"overlay":false}]}')
            self.assertEqual(profiles.load_profiles(path), [Profile("Legacy", True)])

    def test_fifo_is_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.fifo"
            os.mkfifo(path)
            code = (
                "import importlib.util, sys; "
                f"spec=importlib.util.spec_from_file_location('profiles', {str(SOURCE)!r}); "
                "module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
                "module.load_profiles(sys.argv[1])"
            )
            result = subprocess.run(
                [sys.executable, "-c", code, str(path)],
                capture_output=True, text=True, timeout=3,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ValueError", result.stderr)

    def test_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                profiles.load_profiles(directory)

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target.json"
            target.write_text('{"version":1,"profiles":[]}')
            link = Path(directory) / "profiles.json"
            link.symlink_to(target)
            with self.assertRaises(ValueError):
                profiles.load_profiles(link)

    def test_dangling_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / "profiles.json"
            link.symlink_to(Path(directory) / "missing.json")
            with self.assertRaises(ValueError):
                profiles.load_profiles(link)

    def test_invalid_utf8_and_deep_json_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            for content in [b"\xff", b"[" * 1500 + b"]" * 1500]:
                path.write_bytes(content)
                with self.assertRaises(ValueError):
                    profiles.load_profiles(path)

    def test_oversized_file_and_profile_count_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_bytes(b" " * (profiles.MAX_PROFILE_BYTES + 1))
            with self.assertRaises(ValueError):
                profiles.load_profiles(path)

            oversized = {"version": 1, "profiles": [
                {"name": f"Game {index}", "gamemode": False, "overlay": False}
                for index in range(profiles.MAX_PROFILES + 1)
            ]}
            path.write_text(json.dumps(oversized))
            with self.assertRaises(ValueError):
                profiles.load_profiles(path)

            with self.assertRaises(ValueError):
                profiles.save_profiles(path, [
                    Profile(f"Game {index}")
                    for index in range(profiles.MAX_PROFILES + 1)
                ])

    def test_save_rejects_oversized_data_without_replacing_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            profiles.save_profiles(path, [Profile("Keep")])
            old_content = path.read_bytes()
            with patch.object(profiles, "MAX_PROFILE_BYTES", 10):
                with self.assertRaises(ValueError):
                    profiles.save_profiles(path, [Profile("Too large")])
            self.assertEqual(path.read_bytes(), old_content)

    def test_rejected_documents_are_not_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            for document in ["{", "[]", '{"version": 2, "profiles": []}',
                             json.dumps({"version": 1, "profiles": [{"name": "Game"}]})]:
                path.write_text(document)
                with self.assertRaises(ValueError):
                    profiles.load_profiles(path)
                self.assertEqual(path.read_text(), document)

    def test_failed_replace_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            profiles.save_profiles(path, [Profile("Old")])
            with patch.object(profiles.os, "replace", side_effect=OSError("test failure")):
                with self.assertRaises(OSError):
                    profiles.save_profiles(path, [Profile("New")])
            self.assertEqual(profiles.load_profiles(path), [Profile("Old")])
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_duplicate_names_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                profiles.save_profiles(Path(directory) / "profiles.json",
                                       [Profile("Same"), Profile("Same")])
