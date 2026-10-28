#!/usr/bin/env python3
"""File-level validation for a packaged HFSS delivery."""

import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("--target-ghz", type=float)
    args = parser.parse_args()
    folder = Path(args.folder).expanduser().resolve()
    errors = []
    warnings = []
    projects = list(folder.glob("*.aedt")) if folder.is_dir() else []
    locks = list(folder.glob("*.lock")) if folder.is_dir() else []
    project_info = []
    for project in projects:
        results = Path(str(project) + "results")
        project_info.append({
            "project": str(project),
            "bytes": project.stat().st_size,
            "results": str(results),
            "results_present": results.is_dir(),
        })
        if not results.is_dir():
            warnings.append("No matching .aedtresults directory for " + project.name)
    if not projects:
        errors.append("No .aedt project found")
    if locks:
        errors.append("Delivery contains active .lock files")

    images = []
    for image in sorted(list(folder.glob("*.png")) + list(folder.glob("*.jpg"))):
        images.append({"name": image.name, "bytes": image.stat().st_size})
        if image.stat().st_size < 1024:
            errors.append("Image is empty or too small: " + image.name)

    csv_info = []
    target_values = []
    for csv_path in sorted(folder.glob("*.csv")):
        with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))
        item = {"name": csv_path.name, "rows": len(rows), "header": rows[0] if rows else []}
        csv_info.append(item)
        if rows and any("St(" in value and "Differential" in value for value in rows[0]):
            item["native_differential_terminal_data"] = True
            if args.target_ghz is not None:
                for row in rows[1:]:
                    try:
                        if abs(float(row[0]) - args.target_ghz) < 1e-9:
                            target_values.append({"file": csv_path.name, "value_db": float(row[1])})
                    except (ValueError, IndexError):
                        continue

    result = {
        "folder": str(folder),
        "projects": project_info,
        "images": images,
        "csv_files": csv_info,
        "target_values": target_values,
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
