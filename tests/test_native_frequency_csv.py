"""Synthetic data tests; no HFSS installation, private files, or network required."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "frequency_check", ROOT / "scripts" / "verify_native_frequency_csv.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
QUANTITY = "dB(RealizedGainTotal)"


class NativeFrequencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "native.csv"

    def write(self, rows, unit="GHz"):
        with self.path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Phi [deg]", "Theta [deg]", f"Freq [{unit}]", QUANTITY + " []"])
            writer.writerows(rows)

    def test_metadata_columns_before_frequency_and_direction(self):
        self.write([[0, 90, 1, -8], [0, 90, 1.1, -3], [0, 90, 1.2, -6]])
        result = CHECK.check(self.path, [QUANTITY], start=1, stop=1.2, step=.1, theta=90, phi=0)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["quantities"][QUANTITY]["sample_max_GHz_value"], [1.1, -3])

    def test_frequency_units_are_converted_from_header(self):
        self.write([[0, 90, 1000, -8], [0, 90, 1100, -3]], unit="MHz")
        result = CHECK.check(self.path, [QUANTITY], start=1, stop=1.1, step=.1)
        self.assertTrue(result["ok"], result)

    def test_wrong_direction_is_rejected(self):
        self.write([[0, 0, 1, -8]])
        self.assertFalse(CHECK.check(self.path, [QUANTITY], theta=90, phi=0)["ok"])

    def test_polarization_component_cannot_substitute_for_quantity(self):
        self.write([[0, 90, 1, -8]])
        self.assertFalse(CHECK.check(self.path, ["dB(RealizedGainX)"])["ok"])

    def test_duplicate_frequency_is_not_a_single_curve(self):
        self.write([[0, 90, 1, -8], [90, 90, 1, -3]])
        self.assertFalse(CHECK.check(self.path, [QUANTITY])["ok"])

    def test_missing_requested_frequency_is_rejected(self):
        self.write([[0, 90, 1, -8], [0, 90, 1.2, -3]])
        self.assertFalse(CHECK.check(self.path, [QUANTITY], start=1, stop=1.2, step=.1)["ok"])

    def test_nonfinite_value_is_rejected(self):
        self.write([[0, 90, 1, "nan"]])
        self.assertFalse(CHECK.check(self.path, [QUANTITY])["ok"])

    def test_unknown_frequency_unit_is_not_guessed(self):
        self.write([[0, 90, 1, -8]], unit="unknown")
        self.assertFalse(CHECK.check(self.path, [QUANTITY])["ok"])


if __name__ == "__main__":
    unittest.main()
