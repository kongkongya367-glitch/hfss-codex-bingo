# End-to-end workflow and gates

## 1. Preflight

Pass when HFSS 2021 R1 is installed, the COM ProgID is available, input files are readable, an output directory is writable, and a license is available. Record already-open projects and avoid touching unrelated ones.

## 2. Geometry interpretation

Extract the VSDX, identify the page and physical layer mapping, establish scale/units, and produce a shape table. Pass when every modeled conductor and void can be traced to a source shape and ambiguous markup is excluded.

## 3. Baseline build

Create a new project/design, material stack, conductive bodies, cutouts, and named variables. Pass when HFSS geometry validation succeeds and three exported views match the source topology.

## 4. Excitations and open boundary

Create ports only after conductor connectivity is correct. For Sdd, use Driven Terminal, actual terminal names, an active differential pair, and the requested reference impedances. Create the air region/radiation boundary and far-field sphere. Pass when no boundary is orphaned and both terminals have the correct reference conductor.

For single-ended coax/probe papers, use the intended modal/terminal single-ended port instead. Reference-plane de-embedding does not remove the connector's exterior electromagnetic effect; use the paper/feed reference when configuring internal wave ports and backcaps.

## 5. Baseline solve

Create an adaptive setup at the target; when a sweep is requested, include that target exactly. Establish a converged baseline before optimization. Export the applicable native S11 or Sdd/Scc data and inspect convergence and radiation. An S-parameter interpolation sweep without saved radiation fields cannot supply a broadband gain curve.

## 6. Parameterization and tuning

Bind variables to the selected geometry. Demonstrate binding by changing each variable temporarily and confirming the intended dimension changes, then restore the baseline. Use coarse-to-fine trials and save each result in a machine-readable log. Do not change topology when the user restricted optimization to dimensions.

Stop when one of these conditions is met:

- a converged candidate satisfies the matching target and radiation constraints;
- the defined search bounds are exhausted;
- repeated solver or licensing failures prevent meaningful progress;
- meeting the target requires a topology/material/layer change outside authorization.

Use fixed-geometry numerical controls before physical search. Write evidence/prediction/falsification before each probe and define a bounded stopping rule. Repeated credible negative controls require reassessing that hypothesis rather than extending it automatically. A source and delivery path with identical filenames are still different projects: verify full paths and matching results.

## 7. Final solve and reports

Rebuild or set the selected variables cleanly, run the final convergence limit, and regenerate the sweep and native reports. Record target-frequency Sdd, minimum Sdd/frequency, estimated bandwidth from the sweep grid, adaptive convergence, efficiency, gain, realized gain, and any limitation.

Only make physical changes if requested; a report/delivery request can reuse valid solved data. Explicit diagnostic sweeps need not wait for an optimization target to pass. For paper reproduction, compare simulation and measurement separately and label unknown feed/material details as assumptions. See `paper-reproduction-and-feeds.md` and `frequency-reports-and-views.md`.

## 8. Delivery

Create a clean folder with deterministic names. Include only requested artifacts, typically:

- final `.aedt` and its `.aedtresults` directory;
- top, bottom, and isometric HFSS model views;
- HFSS-native Sdd report image and CSV;
- dimension table;
- concise summary if requested.

Close the delivery project so no `.lock` remains. Reopen it once and verify the solution/report tree before final handoff.
