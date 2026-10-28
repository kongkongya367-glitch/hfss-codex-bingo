#!/usr/bin/env python3
"""Create and export an HFSS-native Driven Terminal mixed-mode Sdd11 report."""

import argparse
import json
import os
from pathlib import Path
import sys

import pythoncom
import win32com.client


PROGID = "Ansoft.ElectronicsDesktop.2021.1"


def require_project_path(project, expected):
    """Reject an identically named project opened from a different directory."""
    expected = Path(expected).expanduser().resolve()
    actual_folder = Path(str(project.GetPath())).expanduser().resolve()
    if actual_folder != expected.parent or str(project.GetName()) != expected.stem:
        raise RuntimeError(
            "Wrong active project path: {} / {}; expected {}".format(
                actual_folder, project.GetName(), expected
            )
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    parser.add_argument("--design", required=True)
    parser.add_argument("--solution", required=True,
                        help="Example: Setup_2GHz : Sweep_1p5_2p5GHz")
    parser.add_argument("--differential", default="Differential_1")
    parser.add_argument("--report", default="Sdd11_native_mixed_mode")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--image", help="Optional direct HFSS report image export")
    args = parser.parse_args()

    project_path = Path(args.project).expanduser().resolve()
    csv_path = Path(args.csv).expanduser().resolve()
    image_path = Path(args.image).expanduser().resolve() if args.image else None
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if image_path:
        image_path.parent.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject(PROGID)
    except Exception:
        app = win32com.client.Dispatch(PROGID)
    desktop = app.GetAppDesktop()
    project_name = project_path.stem
    try:
        project = desktop.SetActiveProject(project_name)
    except Exception:
        project = None
    if project is None:
        project = desktop.OpenProject(str(project_path))
    require_project_path(project, project_path)
    design = project.SetActiveDesign(args.design)
    if design.GetSolutionType() != "DrivenTerminal":
        raise RuntimeError("Native Sdd requires a DrivenTerminal design")

    report = design.GetModule("ReportSetup")
    if args.report in list(report.GetAllReportNames()):
        report.DeleteReports([args.report])
    quantity = "dB(St({0},{0}))".format(args.differential)
    report.CreateReport(
        args.report,
        "Terminal Solution Data",
        "Rectangular Plot",
        args.solution,
        ["Domain:=", "Sweep"],
        ["Freq:=", ["All"]],
        ["X Component:=", "Freq", "Y Component:=", [quantity]],
        [],
    )
    report.ExportToFile(args.report, str(csv_path))

    image_result = None
    if image_path:
        if image_path.exists():
            image_path.unlink()
        try:
            report.ExportImageToFile(args.report, str(image_path), 1600, 900)
            image_result = {
                "ok": image_path.is_file() and image_path.stat().st_size > 0,
                "path": str(image_path),
                "bytes": image_path.stat().st_size if image_path.exists() else 0,
                "source": "HFSS ReportSetup.ExportImageToFile",
            }
        except Exception as exc:
            image_result = {
                "ok": False,
                "path": str(image_path),
                "error": repr(exc),
                "required_action": "Run the image export inside graphical HFSS; do not redraw externally without consent.",
            }

    project.Save()
    print(json.dumps({
        "project": project.GetName(),
        "design": design.GetName(),
        "solution_type": design.GetSolutionType(),
        "report": args.report,
        "quantity": quantity,
        "csv": str(csv_path),
        "csv_bytes": os.path.getsize(csv_path),
        "image": image_result,
    }, ensure_ascii=False, indent=2))
    if image_result and not image_result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
