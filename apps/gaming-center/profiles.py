"""User-owned requested settings, never proof of applied system state."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import stat
import tempfile

MAX_PROFILE_BYTES = 256 * 1024
MAX_PROFILES = 256


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
    path = Path(path)
    try:
        flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise ValueError("Unable to open profile file safely") from exc
    try:
        if not os.path.samestat(os.fstat(descriptor), os.stat(path, follow_symlinks=False)):
            raise ValueError("Profile file changed while opening")
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("Profile path must be a regular file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            raw = stream.read(MAX_PROFILE_BYTES + 1)
        if len(raw) > MAX_PROFILE_BYTES:
            raise ValueError("Profile file is too large")
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("Invalid or unreadable profile file") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if (not isinstance(document, dict)
            or set(document) != {"version", "profiles"}
            or type(document["version"]) is not int
            or document["version"] != 1
            or not isinstance(document["profiles"], list)
            or len(document["profiles"]) > MAX_PROFILES):
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
    if len(profiles) > MAX_PROFILES:
        raise ValueError("Too many profiles")
    _validate_unique(profiles)
    document = {"version": 1, "profiles": [asdict(p) for p in profiles]}
    serialized = json.dumps(document, indent=2) + "\n"
    encoded = serialized.encode("utf-8")
    if len(encoded) > MAX_PROFILE_BYTES:
        raise ValueError("Profile file is too large")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
