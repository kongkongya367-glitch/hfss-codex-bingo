# Durable checkpoints and interrupted HFSS work

Use for multi-turn simulation work, context compression, and continuation plans. A disk checkpoint helps restore context; it does not guarantee future access, automatically resume a job, or replace the latest user instructions.

## Workspace documents

Maintain one authoritative set:

- `HFSS_RESUME.md`: short entrypoint with exact baseline, scope, achieved/not-achieved status, and what to read next;
- `HFSS_TASK_STATE.json`: machine-readable paths, source fingerprints, native expressions, sources/ports, requested criteria, trial outcomes, live-job snapshots, and next action;
- `HFSS_TARGET_PLAN.md`: physical hypotheses, phased goals, acceptance gates, rejected approaches, script map, and detailed engineering notes.

For an HFSS workspace, a small scoped `AGENTS.md` can point future agents to these documents. Do not force unrelated tasks to resume HFSS or write project-specific facts into global instructions. Clearly designate the authoritative files; dated backup copies are not live state.

Keep generic procedures in the skill and local paths/experimental results in the workspace. Preserve source backups; never rename an unsuccessful trial to `final` merely to simplify the checkpoint.

For the schema-1 checkpoint used by this workflow, run `python scripts/verify_task_checkpoint.py workspace-path` to check baseline fingerprints, project/results pairing, and recorded metrics against collected trial status files. This is a read-only disk check, not validation of current HFSS processes, source phases, geometry, or solver convergence. Investigate inconsistencies rather than rewriting native results to fit the checkpoint.

## What to checkpoint

At minimum record:

- goal, target frequency, beam coordinate system, native quantities, and user-vs-proposed tolerances;
- latest topology/material/dimension authorizations and revoked or rejected directions;
- immutable baseline and matching results directory, geometry authority, settings-only references, active trial, and delivery copies;
- terminal labels versus actual boundary names, differential/common impedances, source amplitudes and phases;
- adaptive settings, consecutive-pass requirement, saved-field provenance, sweep enabled/completed state;
- each trial's actual variables, changed objects, validation/continuity checks, convergence, metrics, native plots, and interpretation;
- failed operations and corrected causes, distinguishing API/quoting mistakes from solver/license failures;
- script entrypoints and their side effects, unfinished preflights, pending trial folders, and actions that must not be repeated;
- running-job identity with command, project, log, PID/session handle, last observed pass, and snapshot time;
- the first safe action on resume and explicit outstanding work.

Update before launching a job, after collecting it, on errors/interruption, and before handoff. Prefer a compact state file plus detailed per-trial logs rather than copying all solver output into the resume entrypoint. A run record should distinguish `prepared`, `solving`, `interrupted`, `collected`, `rejected`, and `qualified`.

## Resume without duplicate jobs

Read the checkpoint, then query live processes and open projects. A lost tool session does not prove the native solver stopped; a stale `solving` JSON does not prove it is running. Verify exact project paths, native command lines, and logs. Never kill unrelated GUI instances or a solver based solely on an old PID.

If a job is active, monitor it without starting another solve for the same trial. If it is absent, preserve interrupted logs before recovery. A `.lock` file is not itself a permission error: inspect its owning PID/path and check whether the project is open in any GUI instance.

Only after verifying the generated trial's owner is absent and its scope is exact may stale **trial-owned** lock/queue files be moved to recovery copies. Never remove a live original backup's lock. Keep `.aedtresults`, including HFSS `.tmp` field/cache files; a broad `*.tmp` cleanup can destroy solved data.

Resume the incomplete native solve only where the version and saved checkpoint support it. Verify the starting pass from the new log. A tested case resumed from pass 10 after an interrupted pass-9 checkpoint, but that is not guaranteed for all failures. Preserve the original log and write a separate recovery log. If recovery is not valid, create and label a fresh trial; do not overwrite prior evidence or relabel a restart as a continuation.

## Desktop/COM ownership

Full-path checks are essential: an identically named project can exist in the workspace and delivery folder. After attachment, `OpenProject`, `SetActiveProject`, and `SaveAs`, verify both project stem and `GetPath()` before mutation or collection.

When several papers or design branches share a workspace, record which task is active and scope historical objectives explicitly. The most recent dated section and per-trial status govern continuation; an old heading containing “current” does not reactivate its work. A new single-ended broadside paper must not inherit the earlier differential/endfire contract.

Serialize operations against a shared graphical Desktop. Independent external scripts can change the active project while `RunScript` reads it. Parallelize offline parsing/copying when safe, not concurrent active-project mutations or competing solves that exceed RAM.

Use unique native project names for unique trials. Do not hardcode `hfss-25` when the branch is `hfss-26`. Keep incomplete preflight projects outside the curated deliverable selection; package the exact project from the successful trial state, not every `.aedt` in a dirty folder.

Before final packaging: close the copied project, verify no active lock, reopen the exact delivery path, validate native metrics/ports, and close it again. If deliberately leaving a project visible afterward, the disk package and ZIP should already have been verified; distinguish the viewing lock from the clean archived contents.

## Knowledge and chat handoffs

The skill provides methods; it is not a transcript store or automatically shared conversation memory. Put current requirements, authorizations, selected source/result paths, and unfinished work in the workspace records. Summaries can help locate evidence, but must distinguish read transcripts from locally reconstructed continuity. If a referenced-chat reader or new-chat tool is unavailable, state that limit; never claim to have read or created a chat. A handoff prompt should name the workspace and require reading its records before model actions. Skill maintenance alone does not authorize a solve, a new chat, or project edits.
