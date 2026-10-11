# v1.0.1 KSP Validation Checklist

Use a sandbox save or backup. This is a new physics/collider test build and is not published to GitHub/CKAN.

## Variant mass — all four girders

- [ ] Select Octo XL Open Frame; verify dry mass ~3.20 t. Switch to Armored Panels; verify ~4.00 t.
- [ ] Select Octo Medium Open Frame; verify ~1.85 t. Switch to Armored Panels; verify ~2.3125 t.
- [ ] Select Hex Long Open Frame; verify ~0.76 t. Switch to Armored Panels; verify ~0.95 t.
- [ ] Select Hex Medium Open Frame; verify ~0.42 t. Switch to Armored Panels; verify ~0.525 t.
- [ ] Save craft with armored variants, reload and check their selected variants and mass.
- [ ] Verify EC (9000/4500/1200/600) and MonoPropellant (1500/750/200/100) have NOT changed.

## Exterior surface attachment — six parts

- [ ] Stack all six pieces using top and bottom nodes and check no gaps.
- [ ] Click near the **center of a side face** (not a corner or end) to radially attach a solar panel, RCS block, small battery or light. Check it mounts on the exterior instead of at the girder center.
- [ ] Try attaching a girder itself sideways to a regular stock fuel tank, and verify its radial `node_attach` aligns as expected.
- [ ] Repeat the radial mounting test with two-fold and four-fold symmetry on both Octo and Hex girders.
- [ ] Check attachment positions in **both** Open Frame and Armored Panels, noting any unwanted hovering or clipping.
- [ ] Look for unexpected invisible barriers when interacting with open girders; outer collider faces are deliberately present in both variants.
- [ ] Save/load the craft and inspect radial placement. Launch a disposable test craft, check separation/jitter/collisions, quicksave/load and timewarp.

## General regression

- [ ] No missing or reversed outer surfaces, batteries, nameplates or armor meshes.
- [ ] Both adapters still connect to stock 2.5m and 1.25m diameter parts.
- [ ] All part categories, costs, descriptions and career unlocks still work.
- [ ] Inspect `KSP.log` for collision, variant, and model loading errors.
- [ ] With Kerbalism installed, confirm EC and MonoPropellant storage persist after vessel switch and timewarp.

Please send screenshots of an Octo XL and Hex Long with a stock solar panel or RCS block radially attached, plus VAB mass readout for Open vs Armored.
