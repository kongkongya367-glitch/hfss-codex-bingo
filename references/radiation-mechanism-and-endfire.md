# Radiation mechanism before directional optimization

Read for specified beam directions, high realized-gain targets, or a matched/high-efficiency model with an unexpected pattern. These are engineering decision gates, not an assertion that one geometry must or cannot work.

## 1. Specify the physical question

Before selecting variables, identify the intended radiator, feed/filter network, parasitic conductors, intended differential symmetry, and expected phase relationships. Record which relationships are verified and which are hypotheses.

Separate:

- geometry correctness: layers, voids, connections, vias, resistors, port faces;
- excitation correctness: native active differential pair and equal, opposite terminal sources;
- radiation mechanism: actual current distribution and phase on the intended radiator;
- performance: matching, efficiency, direction, realized gain, bandwidth.

A failure at one level cannot be repaired merely by reporting success at another. Avoid automatically assuming the feed is non-radiating or that a detached metal strip is an effective director. Define its intended role and verify its induced currents before tuning that role.

## 2. Direction is not a polarization component or a color

Use the actual far-field coordinate system, not an inferred screenshot orientation. For HFSS Global spherical coordinates:

| Direction | Theta | Phi |
|---|---:|---:|
| +X | 90 deg | 0 deg |
| -X | 90 deg | 180 deg |
| +Y | 90 deg | 90 deg |
| -Y | 90 deg | -90 deg |
| +Z | 0 deg | any |
| -Z | 180 deg | any |

For a user asking gain along +X, sample `dB(RealizedGainTotal)` at Theta=90 deg, Phi=0 deg. `RealizedGainX` is a field-component quantity, not total gain toward +X. Confirm the report uses Global; a rotated report coordinate system is not a physical beam change.

Keep peak gain, requested-axis gain, opposite-axis gain, and the sampled peak angles separately. State angular grid resolution; do not claim exact mainlobe alignment beyond that resolution. An angular cone such as 15 deg may be a screening convention, but is not a user requirement unless agreed. Color depends on scale and does not prove the beam points along a particular axis.

Radiation efficiency is not total efficiency including mismatch. Record native incident, accepted, and radiated powers where available, so efficient radiation of a small accepted power is not confused with high realized gain.

## 3. Diagnose using native saved fields

Use a separately saved, verified baseline copy with valid fields. Preserve the original solved model and `.aedtresults`. If reusing older converged fields, retain their original solve provenance; do not relabel them as a fresh solve under newly requested settings.

Inspect native surface-current magnitude and vectors on feed, ground/radiator, bottom filter, and parasitic conductors. Inspect slot electric fields at consistent positions. Reidentify face IDs after geometry rebuilds; inherited overlays may use stale faces.

Compare phases such as 0/90 deg (or 0/90/180/270 deg when needed) with common units and comparable scales. Local autoscaling can hide weak excitation or make different structures appear equally strong. Set a useful shared scale, state it, and inspect numerical samples as a cross-check. Example scales from one 2-GHz case were 0.01–20 A/m for Jsurf and 10–10000 V/m for E on logarithmic scales; these are examples, not defaults for all antennas.

For complex grid exports:

- inspect headers, units, and column count before parsing;
- establish grid ordering with a known single-point native export rather than assuming rows include XYZ;
- a verified HFSS 2021 case exported two header lines followed by six complex-vector scalar columns, with x outer/y inner;
- use finite masks for NaNs inside metal/undefined locations; do not convert undefined fields to zero;
- retain region bounds, grid spacing, sample counts, and phase/normalization.

Track changed geometry when placing diagnostics. After moving a parasitic conductor, a current sample at its old position is no longer a measurement on that conductor. Distinguish fixed-space field comparisons from corresponding physical-conductor comparisons and expand the sampling domain after PCB extension when needed.

Near-field RMS/peak amplitudes in unequal regions are diagnostic observations, **not internal S21 or per-region radiated power**. Interference prevents a unique allocation of total radiation by simple amplitude comparison. Strong feed fields and weak antenna fields support a coupling hypothesis; they do not by themselves prove the feed supplies most radiated power.

Check actual differential current symmetry with consistently oriented paths/field components where feasible. Merely setting opposite terminal phases is not proof of the intended current distribution. A common-phase control is a diagnostic only when appropriate: run it in a separate copy or transient postprocessing context, restore the required differential sources in `finally`, and verify native metrics after restoration. Do not deliver a common-phase pattern as a differential result. Remove/relabel control reports that would otherwise recompute under restored sources.

## 4. Hypothesis-driven dimension trials

For each trial family, record:

1. hypothesis and field/pattern evidence;
2. proposed dimension changes and unchanged topology/material/ports;
3. predicted measurable effect, including direction—not only Sdd;
4. physical bounds, collision/continuity checks, and reversible source copy;
5. convergence state, native Sdd, efficiency, requested/opposite-axis gain, and peak angles;
6. conclusion: supported, contradicted, or inconclusive because the run is provisional.

Use small discriminating tests before a larger joint search. Changing several interacting dimensions can be legitimate, but does not identify which dimension caused an effect. Evaluate controls when that distinction matters. When a family repeatedly improves scalar metrics but not direction, revisit the mechanism rather than automatically enlarging the same sweep.

Keep user topology restrictions. PCB extension, parasitic spacing changes, extra conductors, added reflectors, replacement antennas, and altered feed connections are different scope decisions. Do not treat permission for one as permission for all. If new architecture is needed, seek that authority; a few failed local trials do not prove the current architecture is impossible.

## 5. Qualification and handoff

Record requested tolerances separately from proposed screening thresholds. Do not invent an agreed minimum efficiency, a +5-dBi acceptance tolerance, or an angular tolerance. A final candidate must meet the actual combination of matching, beam direction, gain, radiation, convergence, and scope requirements.

Honor the requested pass limit and Delta S. Use the native convergence table's target/current consecutive passes and whole-run messages. If a dense starting mesh or mesh reuse is considered, verify the versioned API first and report the solve provenance and computational work honestly. Never silently relax consecutive-pass requirements or disguise extra iterations.

For optimization qualification, run the final sweep on a promising stable candidate and include the target exactly. An explicit request for a diagnostic frequency curve can authorize a sweep before performance goals are met; retain its provisional qualification. Clearly distinguish a LastAdaptive point from a completed frequency sweep. Preserve the existing valid baseline if new trials fail. A useful failed-study handoff contains verified observations and next hypotheses, not fabricated optimal dimensions.
