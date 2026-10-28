# Reproduce paper geometry and feed physics

Use for standalone paper models, coax/probe feeds, retained-CAD integration, or dimension audits. Frequencies, impedances, dimensions and tolerances come from the current task; none are installation defaults.

## Source and dimension audit

Select the final prototype, figure/caption and parameter set before drawing. A paper's introductory plain patch, one-slot example and final multi-slot prototype can be different antennas. Compare three separate claims: published geometry reproduced, assumed hardware implemented, and electromagnetic results reproduced.

Maintain a dimension table with symbol, units, published/CAD value, geometric definition, actual measured value, variable expression and evidence. Record whether a length is a projection, folded centerline, edge-to-edge gap, junction-center distance or exposed uniform-line length. Creation commands may include overlap that is removed or hidden by union. A nominal variable alone is not a physical measurement.

Use native BRep vertices/edges/faces after Boolean operations. For circular vias/probes, planar cap centers and area establish the axis; a cylinder seam vertex is not its center. Probe actual conductor contacts and insulation. Temporarily perturb authorized parameters and confirm intended native geometry moves, then restore the selected values. Keep unrelated geometry and variables unchanged.

List unpublished copper thickness/conductivity, dielectric loss, probe radius, solder, connector dimensions and manufacturing details as assumptions. A PEC zero-thickness sheet is different from finite-thickness copper. Do not silently change either representation to improve a curve. Mark a figure-derived mechanical outline separately from author-certified mechanical dimensions.

## Relayout and impedance reasoning

When moving a multilayer conversion/filter region, preserve relative registration of conductors, ground slots, vias, gaps and resistive terminations. Record necessary changes at fixed/moving interfaces and their electrical lengths. Moving internally identical shapes can still change external coupling; deleting a fold is a topology/electrical-path change, not an equivalent translation.

For a microstrip estimate, use the conductor-to-reference-ground dielectric thickness, not automatically the entire multilayer board thickness. State the assumptions of the selected approximation: isolated line, intact ground, uniform dielectric and conductor thickness. Distinguish exposed line length from overlap at wide junctions.

Do not apply a microstrip width formula to a ground slot, a patch over a ground window, or coupled odd/even-mode lines. Approximate quarter-wave lengths can explain why reference dimensions are retained; they do not prove the complete transition impedance or matching. An ideal branch-line table is not a substitute for the actual multilayer circuit.

## Single-ended coax/probe feeds

For the intended single-ended mode, retain the appropriate DrivenModal/DrivenTerminal solution and actual port names. Use native `dB(S(port,port))` for modal S11. Differential St quantities belong to a differential contract, not every antenna.

For an ideal, uniform, nonmagnetic coaxial TEM section, `Z0 ≈ 60/sqrt(er) * ln(b/a)`, with inner conductor radius `a` and outer conductor inner radius `b`. This derives a nominal line geometry; it does not specify a real SMA's mechanical body or discontinuities.

Check probe-to-patch contact, shell-to-ground contact, ground clearance around the signal conductor, dielectric occupancy, port cross-section, modal count, normalization and de-embedding direction/reference plane. Geometry/extended port validation and a successfully solved port mode are different evidence levels.

An interior wave port generally requires an appropriate termination/backing implementation. One HFSS 2021 R1 documented approach for an internal coax-fed patch uses a PEC cap on the non-propagating side; verify the installed manual and actual port eligibility before choosing it. The cap must not short the intended forward coax path or be assigned as a radiation boundary.

Keep the radiation-region clearance independent of the connector length. Shortening a connector must not accidentally move the air boundary to the port plane. Assign radiation to the intended exterior faces, excluding port sections and internal material interfaces as appropriate to the selected formulation.

De-embedding moves the reference plane along a transmission line. It does not remove the connector exterior's interaction with a finite ground plane or antenna. A long external coax and a short SMA-shaped model cannot be declared electromagnetically equivalent just because their reference planes coincide. If shape, port, cap and region also change, compare the complete implementation and do not attribute the difference uniquely to length.

## Compare with the paper without tuning to appearances

Keep simulated data, measured data and approximate figure digitization in separate columns, with the relevant frequency and metric definition. Do not invent an acceptance tolerance. Unknown connector/loss details can limit reproduction even when the published planar dimensions match.

Distinguish S11 matching minima, directional radiation nulls, total-radiated-power minima and efficiency minima. A missing second S11 dip does not prove a mode is absent; two radiation nulls do not prove two impedance matches. Native complex single-ended S gives `Zin = Zref*(1+S)/(1-S)` for the stated reference and termination, which helps explain reflection but does not uniquely diagnose geometry.

With native mixed-mode Sdd, the same relation describes differential input with the common port matched to its reference. It need not equal the native Z-matrix diagonal, which has a different boundary condition. Neither quantity alone is the impedance of an isolated radiator inside an integrated filter/antenna.

Deep dB minima are sensitive to small complex reflection changes. Compare like convergence settings and quantify numerical drift before calling small changes an improvement. Do not alter paper dimensions merely to manufacture a second dip when the user asked for fixed-dimension reproduction.
