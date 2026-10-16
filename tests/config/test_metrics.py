import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "gaming_center_metrics", ROOT / "apps/gaming-center/metrics.py")
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.stat = self.root / "stat"
        self.meminfo = self.root / "meminfo"

    def collector(self, stat_text="cpu 100 0 0 100 0 0 0 0 0 0\n",
                  mem_text="MemTotal: 1000 kB\nMemAvailable: 250 kB\n"):
        self.stat.write_text(stat_text)
        self.meminfo.write_text(mem_text)
        return metrics.MetricsCollector(self.stat, self.meminfo)

    def test_real_files_first_sample_unavailable_then_cpu_and_memory(self):
        collector = self.collector()
        first = collector.sample()
        self.assertIsNone(first.cpu_percent)
        self.assertEqual(first.memory_percent, 75.0)
        self.assertTrue(any("second sample" in error for error in first.errors))
        self.stat.write_text("cpu 120 0 0 120 0 0 0 0 0 0\n")
        second = collector.sample()
        self.assertEqual(second.cpu_percent, 50.0)
        self.assertEqual(second.memory_percent, 75.0)
        self.assertEqual(second.errors, [])

    def test_guest_counters_are_not_double_counted(self):
        self.assertEqual(metrics.parse_cpu_stat(
            "cpu 100 0 0 100 0 0 0 0 90 40\n"), (200, 100))
        collector = self.collector("cpu 100 0 0 100 0 0 0 0 90 40\n")
        collector.sample()
        self.stat.write_text("cpu 110 0 0 110 0 0 0 0 100 50\n")
        snapshot = collector.sample()
        self.assertEqual(snapshot.cpu_percent, 50.0)

    def test_cpu_reset_and_nonadvancing_counters_are_unavailable(self):
        collector = self.collector("cpu 100 0 0 100\n")
        collector.sample()
        self.stat.write_text("cpu 90 0 0 90\n")
        self.assertIsNone(collector.sample().cpu_percent)
        self.stat.write_text("cpu 90 0 0 90\n")
        same = collector.sample()
        self.assertIsNone(same.cpu_percent)
        self.assertTrue(any("reset or did not advance" in error for error in same.errors))
        self.stat.write_text("cpu 100 0 0 100\n")
        self.assertEqual(collector.sample().cpu_percent, 50.0)

    def test_individual_counter_decrease_is_unavailable_when_aggregate_grows(self):
        collector = self.collector("cpu 100 0 100 100 0 0 0 0\n")
        collector.sample()
        # user decreases by 10, while system increases by 30 and idle by 10;
        # the total still rises by 30, which aggregate-only checks miss.
        self.stat.write_text("cpu 90 0 130 110 0 0 0 0\n")
        snapshot = collector.sample()
        self.assertIsNone(snapshot.cpu_percent)
        self.assertTrue(any("counters reset" in error for error in snapshot.errors))

    def test_cpu_parser_rejects_missing_malformed_and_negative_counters(self):
        for contents in ("intr 0\n", "cpu 1 2 x 4\n", "cpu 1 2 -3 4\n",
                         "cpu 1 2 3\n"):
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                metrics.parse_cpu_stat(contents)

    def test_memory_validation_and_absent_fields_do_not_fabricate_values(self):
        valid = "MemAvailable: 0 kB\nMemTotal: 42 kB\n"
        self.assertEqual(metrics.parse_meminfo(valid), 100.0)
        for contents in (
            "MemTotal: 100 kB\n",
            "MemTotal: 0 kB\nMemAvailable: 0 kB\n",
            "MemTotal: 100 kB\nMemAvailable: 101 kB\n",
            "MemTotal: -1 kB\nMemAvailable: 0 kB\n",
            "MemTotal: 100 MB\nMemAvailable: 10 kB\n",
        ):
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                metrics.parse_meminfo(contents)
        collector = self.collector(mem_text="MemTotal: 100 kB\n")
        snapshot = collector.sample()
        self.assertIsNone(snapshot.memory_percent)
        self.assertTrue(any("Memory metrics unavailable" in error
                            for error in snapshot.errors))

    def test_oversized_decimal_counters_are_unavailable_without_overflow(self):
        huge = "9" * 100
        collector = self.collector(
            f"cpu {huge} 0 0 100 0 0 0 0\n",
            f"MemTotal: {huge} kB\nMemAvailable: 1 kB\n",
        )
        snapshot = collector.sample()
        self.assertIsNone(snapshot.cpu_percent)
        self.assertIsNone(snapshot.memory_percent)
        self.assertTrue(any("CPU metrics unavailable" in error
                            for error in snapshot.errors))
        self.assertTrue(any("Memory metrics unavailable" in error
                            for error in snapshot.errors))

    def test_proc_reader_rejects_symlink_directory_fifo_and_oversize(self):
        target = self.root / "target"
        target.write_text("cpu 1 0 0 1\n")
        link = self.root / "link"
        link.symlink_to(target)
        directory = self.root / "directory"
        directory.mkdir()
        fifo = self.root / "fifo"
        os.mkfifo(fifo)
        oversized = self.root / "oversized"
        oversized.write_bytes(b"x" * (metrics.MAX_PROC_BYTES + 1))
        for path in (link, directory, fifo, oversized):
            with self.subTest(path=path.name), self.assertRaises((OSError, ValueError)):
                metrics._read_proc_file(path)


if __name__ == "__main__":
    unittest.main()
