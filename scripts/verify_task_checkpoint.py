#!/usr/bin/env python3
"""Read-only disk consistency check; never attaches to HFSS or launches a solve."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def verify(workspace):
    root = Path(workspace).resolve()
    errors = []
    warnings = []
    for name in ("HFSS_RESUME.md", "HFSS_TARGET_PLAN.md", "HFSS_TASK_STATE.json"):
        file = root / name
        if not file.is_file() or file.stat().st_size == 0:
            errors.append("Missing or empty continuation file: " + name)
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}
    try:
        state = json.loads((root / "HFSS_TASK_STATE.json").read_text(encoding="utf-8-sig"))
        if state.get("schema_version") != 1:
            errors.append("Unsupported checkpoint schema_version")
        if Path(state["authoritative_workspace"]).resolve() != root:
            errors.append("Workspace does not match authoritative_workspace")
        baseline = state["baseline"]
        project = Path(baseline["project"])
        results = Path(baseline["results"])
        if not project.is_file():
            errors.append("Baseline project missing: " + str(project))
        elif baseline.get("sha256"):
            actual = hashlib.sha256(project.read_bytes()).hexdigest()
            if actual.lower() != baseline["sha256"].lower():
                errors.append("Baseline SHA256 mismatch; investigate, do not overwrite the model")
        if not results.is_dir():
            errors.append("Baseline results directory missing")
        if results != project.with_suffix(".aedtresults"):
            errors.append("Baseline project/results names do not match")
        if state.get("goal_met") and not state.get("delivery", {}).get("contains_qualified_final_project"):
            errors.append("goal_met conflicts with absence of a qualified final delivery")
        count = 0
        mapping = {
            "Sdd11_dB": ("metrics", "dB(St(Differential_1,Differential_1))"),
            "efficiency": ("metrics", "RadiationEfficiency"),
            "global_peak_dBi": ("metrics", "dB(PeakRealizedGain)"),
            "plusX_dBi": ("axes_dBi", "+X"),
        }
        for trial in state.get("collected_trials", []):
            folder = root / trial["folder"]
            trial_project = folder / trial["project_name"]
            trial_status = folder / "status.json"
            if not trial_project.is_file() or not trial_status.is_file():
                errors.append("Trial project/status missing: " + trial["id"])
                continue
            native = json.loads(trial_status.read_text(encoding="utf-8-sig"))
            if Path(native["project"]).resolve() != trial_project.resolve():
                errors.append("Trial project path mismatch: " + trial["id"])
            if native.get("status") != "collected":
                errors.append("Recorded collected trial is not collected: " + trial["id"])
            if native.get("adaptive_converged") != trial.get("adaptive_converged"):
                errors.append("Convergence mismatch: " + trial["id"])
            if native.get("goal_met") != trial.get("goal_met"):
                errors.append("Qualification mismatch: " + trial["id"])
            for label, (section, key) in mapping.items():
                if label in trial and not math.isclose(float(trial[label]), float(native[section][key]), rel_tol=1e-9, abs_tol=1e-8):
                    errors.append("Metric mismatch: " + trial["id"] + "/" + label)
            if not trial_project.with_suffix(".aedtresults").is_dir():
                errors.append("Trial solved results missing: " + trial["id"])
            count += 1
        if state.get("live_snapshot"):
            warnings.append("Live snapshot is historical: requery Desktop/processes before any action")
        return {"ok": not errors, "workspace": str(root), "checked_collected_trials": count,
                "goal_met": state.get("goal_met"), "errors": errors, "warnings": warnings,
                "scope": "Disk records only; not a live geometry, license, source-phase, convergence or radiation verification"}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append("Invalid/unreadable checkpoint: " + str(exc))
        return {"ok": False, "errors": errors, "warnings": warnings}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace")
    result = verify(parser.parse_args().workspace)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)
