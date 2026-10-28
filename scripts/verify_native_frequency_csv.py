#!/usr/bin/env python3
"""Read-only validation of one-variation native HFSS frequency-curve CSV data."""
import argparse
import csv
from decimal import Decimal
import json
import math
from pathlib import Path
import re


def base_name(header):
    return re.sub(r"\s*\[[^\]]*\]\s*$", "", header).strip()


def unit_name(header):
    match = re.search(r"\[([^\]]*)\]\s*$", header)
    return match.group(1).strip() if match else None


def check(path, quantities, start=None, stop=None, step=None,
          theta=None, phi=None, frequency_unit=None):
    result = {"file": str(Path(path).resolve()), "ok": False, "errors": [],
              "scope": "CSV values only; not native convergence, Global CS, excitation or field-provenance validation"}
    try:
        with Path(path).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream)
            header = next(reader)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
        if not rows:
            raise ValueError("No frequency data rows")
        if any(len(row) != len(header) for row in rows):
            raise ValueError("Inconsistent CSV column count")

        def column(name):
            hits = [i for i, h in enumerate(header)
                    if h == name or base_name(h).casefold() == name.casefold()]
            if len(hits) != 1:
                raise ValueError("Missing or ambiguous column: " + name)
            return hits[0]

        freq_hits = [i for i, h in enumerate(header)
                     if base_name(h).casefold() in ("freq", "frequency")]
        if len(freq_hits) != 1:
            raise ValueError("Missing or ambiguous native frequency column")
        fi = freq_hits[0]
        native_unit = unit_name(header[fi])
        unit = frequency_unit or native_unit
        factors = {"Hz": 1e-9, "kHz": 1e-6, "MHz": 1e-3, "GHz": 1.0}
        if unit not in factors:
            raise ValueError("Unknown frequency unit; supply --frequency-unit explicitly")
        if frequency_unit and native_unit and frequency_unit != native_unit:
            raise ValueError("Frequency-unit override disagrees with the native header")
        frequencies = [float(row[fi]) * factors[unit] for row in rows]
        if not all(math.isfinite(v) for v in frequencies):
            raise ValueError("Nonfinite frequency")
        if len({round(v, 12) for v in frequencies}) != len(frequencies):
            raise ValueError("Repeated frequencies: export a single variation and fixed-direction curve")
        order = sorted(range(len(rows)), key=lambda i: frequencies[i])
        sorted_freq = [frequencies[i] for i in order]
        if any(v is not None for v in (start, stop, step)):
            if any(v is None for v in (start, stop, step)):
                raise ValueError("Supply --start-ghz, --stop-ghz and --step-ghz together")
            a, b, d = (Decimal(str(v)) for v in (start, stop, step))
            if d <= 0 or b < a:
                raise ValueError("Require positive step and stop >= start")
            intervals = (b - a) / d
            if intervals != intervals.to_integral_value():
                raise ValueError("Requested endpoints are not divisible by step")
            count = int(intervals) + 1
            if len(rows) != count:
                raise ValueError(f"Expected {count} frequency rows, found {len(rows)}")
            if any(not math.isclose(v, float(a + i * d), rel_tol=1e-9, abs_tol=1e-9)
                   for i, v in enumerate(sorted_freq)):
                raise ValueError("Frequency grid does not match requested GHz values")

        summaries = {}
        for name in quantities:
            ci = column(name)
            values = [float(row[ci]) for row in rows]
            if not all(math.isfinite(v) for v in values):
                raise ValueError("Nonfinite quantity values: " + name)
            low = min(range(len(rows)), key=lambda i: values[i])
            high = max(range(len(rows)), key=lambda i: values[i])
            summaries[name] = {"header": header[ci],
                               "sample_min_GHz_value": [frequencies[low], values[low]],
                               "sample_max_GHz_value": [frequencies[high], values[high]]}

        checked_angles = {}
        for label, expected in (("Theta", theta), ("Phi", phi)):
            if expected is None:
                continue
            ci = column(label)
            angle_unit = unit_name(header[ci])
            if angle_unit not in ("deg", "rad"):
                raise ValueError("Unknown native angle unit: " + label)
            values = [float(row[ci]) for row in rows]
            if angle_unit == "rad":
                values = [math.degrees(v) for v in values]
            if any(not math.isfinite(v) or not math.isclose(v, expected, abs_tol=1e-7, rel_tol=0)
                   for v in values):
                raise ValueError("Direction column does not match requested angle: " + label)
            checked_angles[label + "_deg"] = expected

        result.update(ok=True, rows=len(rows), headers=header, frequency_unit=unit,
                      frequency_range_GHz=[sorted_freq[0], sorted_freq[-1]],
                      ascending_frequency_order=order == list(range(len(rows))),
                      checked_angle_columns=checked_angles, quantities=summaries)
    except (OSError, ValueError, StopIteration, csv.Error, ArithmeticError) as exc:
        result["errors"].append(str(exc))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file")
    parser.add_argument("--quantity", action="append", required=True,
                        help="Exact native quantity name; repeat for multiple traces")
    parser.add_argument("--start-ghz", type=float)
    parser.add_argument("--stop-ghz", type=float)
    parser.add_argument("--step-ghz", type=float)
    parser.add_argument("--theta-deg", type=float)
    parser.add_argument("--phi-deg", type=float)
    parser.add_argument("--frequency-unit", choices=["Hz", "kHz", "MHz", "GHz"])
    args = parser.parse_args()
    result = check(args.csv_file, args.quantity, args.start_ghz, args.stop_ghz,
                   args.step_ghz, args.theta_deg, args.phi_deg, args.frequency_unit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
