"""User-owned requested settings, never proof of applied system state."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile


@dataclass(frozen=True)
class Profile:
    name: str
    gamemode: bool = False
    overlay: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("A profile needs a nonempty name")
        if len(self.name) > 120 or any(ord(c) < 32 for c in self.name):
            raise ValueError("Profile name is too long or contains control characters")
        if type(self.gamemode) is not bool or type(self.overlay) is not bool:
            raise ValueError("Options must be booleans")

    def launch_options(self):
        # Only fixed tokens reach the command preview; names are never commands.
        tokens = []
        if self.gamemode:
            tokens.append("gamemoderun")
        if self.overlay:
            tokens.append("mangohud")
        return " ".join([*tokens, "%command%"])

    def reset(self):
        return Profile(self.name)


def load_profiles(path):
    try:
        with Path(path).open(encoding="utf-8") as stream:
            document = json.load(stream)
    except FileNotFoundError:
        return []
    if (not isinstance(document, dict)
            or set(document) != {"version", "profiles"}
            or type(document["version"]) is not int
            or document["version"] != 1
            or not isinstance(document["profiles"], list)):
        raise ValueError("Unsupported profile document")
    profiles = []
    for item in document["profiles"]:
        if not isinstance(item, dict) or set(item) != {"name", "gamemode", "overlay"}:
            raise ValueError("Invalid profile fields")
        profiles.append(Profile(**item))
    _validate_unique(profiles)
    return profiles


def _validate_unique(profiles):
    if any(not isinstance(profile, Profile) for profile in profiles):
        raise ValueError("Expected Profile instances")
    if len({profile.name for profile in profiles}) != len(profiles):
        raise ValueError("Duplicate profile names")


def save_profiles(path, profiles):
    profiles = list(profiles)
    _validate_unique(profiles)
    document = {"version": 1, "profiles": [asdict(p) for p in profiles]}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
