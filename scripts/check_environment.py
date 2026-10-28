#!/usr/bin/env python3
"""Check prerequisites for the HFSS 2021 R1 Codex workflow without mutation."""

import argparse
import json
import os
from pathlib import Path
import sys


PROGID = "Ansoft.ElectronicsDesktop.2021.1"


def candidate_executables():
    seen = set()
    roots = []
    env_root = os.environ.get("AWP_ROOT211")
    if env_root:
        roots.extend([Path(env_root), Path(env_root) / "AnsysEM"])
    for drive in ("C:", "D:", "E:"):
        roots.extend([
            Path(drive + r"\Program Files\AnsysEM\AnsysEM21.1"),
            Path(drive + r"\Program Files\ANSYS Inc\v211\AnsysEM"),
        ])
    for root in roots:
        path = root / "Win64" / "ansysedt.exe"
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            yield path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Optional .vsdx input to validate")
    parser.add_argument("--probe-active-com", action="store_true",
                        help="Check for an already-running HFSS instance; never launches one")
    args = parser.parse_args()

    found = [str(path.resolve()) for path in candidate_executables() if path.is_file()]
    pywin32 = {"available": False}
    try:
        import pythoncom
        import win32com.client
        pywin32 = {"available": True}
    except Exception as exc:
        pywin32 = {"available": False, "error": repr(exc)}

    active = {"checked": False}
    if args.probe_active_com:
        active = {"checked": True, "available": False}
        if pywin32["available"]:
            try:
                pythoncom.CoInitialize()
                app = win32com.client.GetActiveObject(PROGID)
                desktop = app.GetAppDesktop()
                active = {
                    "checked": True,
                    "available": True,
                    "projects": list(desktop.GetProjectList()),
                }
            except Exception as exc:
                active["error"] = repr(exc)

    input_status = None
    if args.input:
        path = Path(args.input).expanduser().resolve()
        input_status = {
            "path": str(path),
            "exists": path.is_file(),
            "extension": path.suffix.lower(),
        }

    result = {
        "platform": sys.platform,
        "python": sys.executable,
        "hfss_2021r1_executables": found,
        "com_progid": PROGID,
        "pywin32": pywin32,
        "active_com": active,
        "input": input_status,
    }
    errors = []
    if not sys.platform.startswith("win"):
        errors.append("HFSS 2021 R1 COM automation requires Windows")
    if not found:
        errors.append("ansysedt.exe for 2021 R1 was not found in common locations")
    if not pywin32["available"]:
        errors.append("pywin32 is unavailable")
    if input_status and (not input_status["exists"] or input_status["extension"] != ".vsdx"):
        errors.append("input is not a readable .vsdx file")
    result["ok"] = not errors
    result["errors"] = errors
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
