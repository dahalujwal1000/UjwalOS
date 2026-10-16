"""Read-only CPU and memory metrics from bounded procfs snapshots."""

from dataclasses import dataclass
import os
from pathlib import Path
import re
import stat


MAX_PROC_BYTES = 64 * 1024
MAX_COUNTER = (1 << 64) - 1
_DECIMAL = re.compile(r"[0-9]+\Z")


@dataclass(frozen=True)
class MetricsSnapshot:
    cpu_percent: float | None
    memory_percent: float | None
    errors: list[str]


def _parse_counter(value: str) -> int:
    if _DECIMAL.fullmatch(value) is None:
        raise ValueError("counter is malformed")
    normalized = value.lstrip("0") or "0"
    if (len(normalized) > 20
            or (len(normalized) == 20 and normalized > str(MAX_COUNTER))):
        raise ValueError("counter exceeds unsigned 64-bit range")
    return int(normalized)


def _parse_cpu_counters(contents: str) -> tuple[int, ...]:
    line = next((item for item in contents.splitlines() if item.startswith("cpu ")), None)
    if line is None:
        raise ValueError("aggregate CPU row is missing")
    fields = line.split()
    values = fields[1:]
    if len(values) < 4:
        raise ValueError("aggregate CPU counters are malformed")
    counters = [_parse_counter(value) for value in values]
    # user, nice, system, idle, iowait, irq, softirq, steal. Do not sum the
    # following guest fields because they are already counted in user/nice.
    return tuple((counters + [0] * 8)[:8])


def parse_cpu_stat(contents: str) -> tuple[int, int]:
    """Return aggregate (total_ticks, busy_ticks), excluding idle and iowait.

    Guest and guest_nice are intentionally excluded: Linux includes them in
    user and nice already. Missing optional trailing counters count as zero.
    """
    counters = _parse_cpu_counters(contents)
    total = sum(counters)
    busy = total - counters[3] - counters[4]
    return total, busy


def parse_meminfo(contents: str) -> float:
    """Return used-memory percentage using MemTotal and MemAvailable in kB."""
    wanted: dict[str, int] = {}
    for line in contents.splitlines():
        fields = line.split()
        if not fields or fields[0] not in {"MemTotal:", "MemAvailable:"}:
            continue
        key = fields[0]
        if key in wanted or len(fields) != 3 or fields[2] != "kB":
            raise ValueError("memory counters are malformed")
        wanted[key] = _parse_counter(fields[1])
    if set(wanted) != {"MemTotal:", "MemAvailable:"}:
        raise ValueError("MemTotal or MemAvailable is missing")
    total = wanted["MemTotal:"]
    available = wanted["MemAvailable:"]
    if total <= 0 or not 0 <= available <= total:
        raise ValueError("memory counters are out of range")
    return (total - available) * 100.0 / total


def _read_proc_file(path: Path) -> str:
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("source is not a regular file")
        chunks = bytearray()
        while len(chunks) <= MAX_PROC_BYTES:
            chunk = os.read(descriptor, min(8192, MAX_PROC_BYTES + 1 - len(chunks)))
            if not chunk:
                break
            chunks.extend(chunk)
        if len(chunks) > MAX_PROC_BYTES:
            raise ValueError("source exceeds 64 KiB limit")
        return chunks.decode("ascii")
    finally:
        os.close(descriptor)


def _error_detail(error: Exception) -> str:
    if isinstance(error, ValueError):
        return str(error)
    return error.__class__.__name__


class MetricsCollector:
    """Collect aggregate system metrics from procfs without commands or writes."""

    def __init__(self, proc_stat: str | os.PathLike[str] = "/proc/stat",
                 meminfo: str | os.PathLike[str] = "/proc/meminfo"):
        self._proc_stat = Path(proc_stat)
        self._meminfo = Path(meminfo)
        self._previous_cpu: tuple[int, ...] | None = None

    def sample(self) -> MetricsSnapshot:
        errors: list[str] = []
        cpu_percent: float | None = None
        try:
            current = _parse_cpu_counters(_read_proc_file(self._proc_stat))
        except (OSError, UnicodeError, ValueError) as exc:
            self._previous_cpu = None
            errors.append(f"CPU metrics unavailable: {_error_detail(exc)}")
        else:
            previous = self._previous_cpu
            self._previous_cpu = current
            if previous is None:
                errors.append("CPU metrics unavailable: waiting for a second sample")
            else:
                deltas = tuple(now - before for now, before in zip(current, previous))
                total_delta = sum(deltas)
                busy_delta = total_delta - deltas[3] - deltas[4]
                if (any(delta < 0 for delta in deltas) or total_delta <= 0
                        or busy_delta < 0 or busy_delta > total_delta):
                    errors.append(
                        "CPU metrics unavailable: counters reset or did not advance"
                    )
                else:
                    cpu_percent = busy_delta * 100.0 / total_delta

        memory_percent: float | None
        try:
            memory_percent = parse_meminfo(_read_proc_file(self._meminfo))
        except (OSError, UnicodeError, ValueError) as exc:
            memory_percent = None
            errors.append(f"Memory metrics unavailable: {_error_detail(exc)}")
        return MetricsSnapshot(cpu_percent, memory_percent, errors)
