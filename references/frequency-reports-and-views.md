# Native frequency data, efficiency, and camera views

Use only the quantities, frequency ranges and directions requested for the current project.

## Match the sweep to the requested observable

| Existing data / request | Appropriate handling |
|---|---|
| LastAdaptive saved fields | Native S parameters and radiation at that solved frequency; not a broadband curve. |
| Converged interpolating S sweep, radiation fields not saved | S-parameter curves; not a broadband gain/efficiency curve. |
| Directional gain across frequency | Verify saved radiation fields at every requested point; otherwise add an authorized field-saving sweep to an independent copy. A discrete sweep with SaveFields and SaveRadFields is a tested option. |
| User changes only output step during interpolation | Where the solved cache supports it, select the requested frequencies in the native report; do not stop/restart just to decimate output. Preserve the distinction between cached grid, actually solved bases and report samples. |
| Only a different 3D viewing direction | Rotate the report camera; no new solve, excitation change or coordinate-system rotation. |

Include exact target frequencies, both endpoints, and the expected count. For a divisible uniform range, count is `(stop-start)/step + 1`. Parse exported frequency units and column names; fixed Phi and Theta columns can precede frequency and gain. Validate finite values, duplicates, sample spacing and fixed-angle columns. A grid maximum/minimum is not a continuous-frequency extremum.

`scripts/verify_native_frequency_csv.py` is a read-only helper for these checks. It cannot establish source phases, Global coordinates, native solver success or field provenance. Verify those in HFSS and the solve record.

Pass the input CSV, repeat `--quantity` for each exact native expression, and optionally supply `--start-ghz`, `--stop-ghz`, `--step-ghz` together. For directional curves also pass the intended `--theta-deg` and `--phi-deg`; missing angle columns then produce an error rather than an unsupported direction claim. Frequencies are normalized from the native header to GHz. A range and step are arguments for this task, not defaults stored in the skill.

Label inherited work accurately: a new field sweep on a converged adaptive mesh is not an independent adaptive solve at every frequency. Count resumed adaptive passes cumulatively. Retain the user-selected limits and check actual linear solver execution in native profiles. A successful diagnostic sweep can be delivered before optimization goals pass if the user explicitly requested it; label its qualification.

Check the source's adaptive value against the swept value at the reused frequency. For resource-limited jobs, serialize solves and GUI work. Keep saved radiation `.tmp` caches; do not use cleanup patterns that remove them.

## Native quantities and power definitions

- Single-ended modal S11: native `dB(S(actual_port,actual_port))`.
- Differential/common reflection: native `dB(St(diff,diff))` / `dB(St(common,common))`; mode conversion such as `St(common,diff)` is a different quantity.
- Requested-axis gain: `dB(RealizedGainTotal)` at the verified physical direction. It includes mismatch and both polarizations. `RealizedGainX` is not “total gain toward +X.”
- Physical Global +X: Theta90/Phi0. Global +Z: Theta0, with Phi degenerate at the pole. All-space peak gain is a separate value.

Retain native incident, accepted and radiated powers. Radiation efficiency is `Prad/Paccepted`; total efficiency including mismatch is `Prad/Pincident`. Conventional power-efficiency dB uses `10*log10(ratio)`. If a paper prints `20*log10` of a power ratio or leaves its input-power definition ambiguous, label its printed convention separately instead of silently equating it with HFSS RadiationEfficiency.

For a verified purely differential excitation, native mode reflection fractions may explain accepted power through `1-|Sdd|²-|Scd|²` when the port conventions and normalization support that balance. Check it against native power values; Sdd alone omits conversion. Do not infer per-region dissipation or radiation from reflection alone.

Locate gain nulls, efficiency minima and matching dips separately. Refine frequency locally only within the requested scope; retain each result's actual sampling resolution. A fixed boresight front/back ratio is not a rear-hemisphere maximum ratio. State the plane, angular domain and co/cross component convention before comparing cross-polarization metrics.

## Native figures and comparisons

Export reports with `ReportSetup.ExportImageToFile`, numeric data with `ExportToFile`, and model views with `ExportModelImageToFile`. If a native export is unavailable, report the issue; do not substitute an external redraw as a software screenshot. Contact sheets can arrange native exports with captions while preserving the separate original images and labeling the layout as a composition.

When overlaying results from different projects, compare like quantities, directions, normalizations and sample grids. A native-exported CSV can be imported as a static comparison trace into an independent report; label which curve is static, keep its source/hash, and verify imported values. Do not imply that an imported prior trace is dynamically solved by the new project.

For model three-views/layers, display only the selected objects or adjust transparency in a display copy. Keep physical positions, thickness and sources unchanged; label any exploded or rescaled engineering drawing separately. Real-scale side views of a thin board can be nearly a line.

## Same 3D radiation result from multiple cameras

Keep frequency, solution variation, source, quantity, physical far-field coordinate system and color scale identical. Change only the camera. Confirm the report, not the modeler, is active before orientation commands; `SetActiveDesign` can reset the active editor.

Prefer the supported native report/view interface. When needed, a tested GUI route is the active 3D report's **View → Modify Attributes → Orientation List**, selecting a view and applying it, then fitting the active view and exporting that named report. Menu IDs, window handles, grid positions and process IDs are session/version-specific: inspect them rather than reusing task script constants.

Read the native current-view direction/up vector or verify the coordinate triad before naming an image “from +X.” Default labels such as front/right are not sufficient across contexts. “From +X” means a camera on the positive-X side looking toward the origin; it does not change the antenna's mainlobe.

Allow GUI changes to settle before reading properties or exporting. Retain axes/triad and a consistent color scale. Check that the exported images are distinct and neither pattern nor scale is clipped. Close the unsaved display copy and verify the solved source remains unchanged. A camera operation does not qualify previously unconverged RF data.
