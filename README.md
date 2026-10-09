# RoosterWorks Station Support — v0.8.4 Octo Polish Test Build

**Author:** SockedRooster · **License:** MIT · **Target:** Kerbal Space Program 1.12.5  
**Project:** https://github.com/SockedRooster/RoosterWorks-Station-Support

## What this contains

All six original station-support parts, now generated from the approved Blender-style geometry. This is a **test build**, not the 1.0/CKAN release.

### v0.8.4 Octo-only polish
- Octo XL batteries and green LED assemblies rotated 180 degrees around their vertical axes to face out through the truss.
- Octo XL and Octo Medium RoosterWorks badges moved 17 mm outward, preserving label size, legibility and earlier left-right corrections.
- Both adapters, both Hex girders, resource capacity, armor switching, colliders, and part configuration files remain identical to v0.8.3.

### v0.8.3 geometry changes
- Hex Long retains four monopropellant tanks, narrowed 20%, with wall battery assemblies moved 4 cm outward to prevent clipping.
- Reversed the adapter outer-shell face winding and corresponding normals so the exterior skin renders instead of being culled.
- Aligned all six nameplate backing meshes against their outer skin/frame. Text scale and orientation are unchanged.
- No gameplay resource capacities, part IDs, tech nodes, attachment nodes, or variant options were changed.


| Part | Configuration | ElectricCharge | MonoPropellant |
|---|---|---:|---:|
| Octo XL Girder | 4 large monopropellant tanks; outward-facing battery banks; Octo badge moved 17 mm out | 9,000 | 1,500 |
| Octo Medium Girder | 3 tanks, full-height battery packs facing outward | 4,500 | 750 |
| Hex Long Girder | 4 tanks narrowed 20%, battery banks moved outward for clearance | 1,200 | 200 |
| Hex Medium Girder | 1 enlarged tank, outward-facing battery packs | 600 | 100 |
| Octo → 2.5 m Adapter | 2.5 m octagonal-to-round stack converter | — | — |
| Hex → 1.25 m Adapter | 1.25 m hexagonal-to-round stack converter | — | — |

The four girders each offer **Open Frame** and **Armored Panels** selectable stock part variants (no B9 dependency). Adapter parts are fixed structural converters with top/bottom stack nodes. Fuel and charge quantities do **not** change with panel selection.

## Install

1. Exit KSP and back up your save before changing test versions.
2. Delete the previous `GameData/RoosterWorksStationSupport` folder, rather than merging different test builds.
3. If you also have the *older named* prototype installed, remove `GameData/RoosterWorksKerbalismAdditions` to avoid duplicate part IDs.
4. Unzip the **player ZIP** into your Kerbal Space Program installation root so it creates `GameData/RoosterWorksStationSupport`.
5. Open the VAB, find RoosterWorks parts under **Structural** (with VAB Organizer: **Trusses** and **Adapters**).

## Things to test before release

1. Place each girder in the VAB; rotate it to confirm outward-facing battery panels and correctly oriented **RoosterWorks / Station Support** nameplates.
2. Switch from **Open Frame** to **Armored Panels** and back; save/reload a craft and confirm the selection persists.
3. Test both adapters connected between a girder and a correctly sized round part. Check stack attachment nodes from both ends.
4. Test collisions with a disposable sandbox craft.
5. Fill/drain EC and MonoPropellant, time warp, swap vessels and reload to test **Kerbalism resource persistence**.

## Known limitations

- **KSP runtime behavior remains unverified** for the five newly converted parts. Static structural validation does not establish stable attachment, proper variant switching, or resource persistence.
- These meshes use **simple, temporary KSP/Diffuse materials**; the final Blender metallic/ceramic shader finish has **not been baked** yet.
- The green mini LED elements are **static visual indicators**, not actually flashing in KSP.
- Current meshes have high triangle counts; performance and draw calls have not been optimized for stations with many repeated girders.
- Open/armored plating shares the same simplified rigid collision volumes.

## Source

Developer source includes the approved Octo XL `.blend` and author's edited script, five Blender-produced FBX exports, the Blender batch builder, and the FBX-to-KSP `.mu` conversion scripts. No Near Future Construction assets or models are included. See [LICENSE](LICENSE).
