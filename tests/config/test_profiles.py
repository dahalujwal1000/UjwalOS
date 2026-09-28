import importlib.util
import json
from pathlib import Path
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
