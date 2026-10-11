# RoosterWorks Station Support

**v1.0.1 VAB / flight test build** · **Author:** SockedRooster · **License:** MIT · **KSP:** 1.12.5

Original modular station-support components: four structural girders with persistent ElectricCharge and MonoPropellant resource definitions, and two 2.5m/1.25m adapters. No required plugin. Designed for use with Kerbalism, but not dependent on it.

## v1.0.1 update: armoring and radial attachment

- **Armored Panels now add 25% of the part's Open Frame dry mass** through KSP's built-in `ModulePartVariants` `mass` offset. Open Frame remains the default and original mass. EC and MonoPropellant amounts are unchanged.
- Every girder and adapter now has a **radial `node_attach`** and allows itself to attach radially to another part (`attachRules = 1,1,1,1,0`). Top/bottom stack attachment is unchanged.
- All six model files have extra, shallow, **invisible perimeter colliders** to catch editor surface clicks before they hit the interior service equipment. These are aligned to the octagonal/hexagonal outer faces; the original rail/equipment colliders are retained.
- All approved visible models, texture files, nameplates, tanks and resource capacities remain unchanged.

**Collision trade-off:** Those perimeter colliders are present **even in Open Frame mode**. That improves surface placement but means the visibly open truss faces behave as thin collision walls. The stock armor selector does not currently toggle colliders. This build needs a VAB/flight collision test before publishing.

## Parts and balance

| Part | Diameter × height | EC | MonoPropellant | Open dry mass | Armored dry mass | Armor addition |
|---|---|---:|---:|---:|---:|---:|
| Octo XL | 2.5 × 4.75 m | 9,000 | 1,500 | 3.200 t | 4.000 t | +0.800 t |
| Octo Medium | 2.5 × 2.65 m | 4,500 | 750 | 1.850 t | 2.3125 t | +0.4625 t |
| Hex Long | 1.25 × 3.15 m | 1,200 | 200 | 0.760 t | 0.950 t | +0.190 t |
| Hex Medium | 1.25 × 1.75 m | 600 | 100 | 0.420 t | 0.525 t | +0.105 t |
| Octo → 2.5m Adapter | 2.5 × 0.74 m | — | — | 0.280 t | — | — |
| Hex → 1.25m Adapter | 1.25 × 0.56 m | — | — | 0.140 t | — | — |

Armor's additional mass is *dry*, so the total launched mass still includes 0.004 t per MonoPropellant unit. EC is treated as massless in stock KSP.

## Installation

1. Exit KSP, back up the save and any craft files, and **remove** the existing `GameData/RoosterWorksStationSupport` folder.
2. Extract `RoosterWorks-Station-Support-v1.0.1-TEST.zip` into the **KSP installation root**, so the folder is `GameData/RoosterWorksStationSupport`.
3. If the old `GameData/RoosterWorksKerbalismAdditions` prototype exists, remove it to prevent duplicate part IDs.
4. In the VAB find the six parts under **Structural**. Test both **Open Frame** and **Armored Panels** before loading an important craft.

If using the **hotfix-only** ZIP, keep your working v1.0.0 installation and overwrite its four/six config files, all six model files and version file with those from the hotfix. The hotfix is not standalone and does **not** include textures. A full replacement is recommended.

## Testing and notes

See `TEST_CHECKLIST.md`. Verify the VAB part mass changes when armor is selected, side-mounted items snap near the outer face rather than at the center, radial attachment of these parts is sensible, and existing craft remain attached after save/reload and flight. The visible meshes and textures were regression checked against v1.0.0; **this is not a substitute for actual KSP runtime validation**.

Known limitations: static green LED details (not flashing), placeholder KSP/Diffuse colors, high triangle counts on large stations, Kerbalism timewarp persistence not systematically verified. The new perimeter colliders make open trusses physically closed across their side faces.

## Source, compatibility and CKAN

The editable Blender assets and FBXs are in `Source/`; native `.mu` files are regenerated with `Source/Conversion/convert_all.py` and require Python, NumPy, SciPy and Pillow. Run `python Source/verify_v101.py` to check the source package against the preserved v1.0.0 baseline (baseline ZIP needs to be available).

The v1.0.0 release is already public and CKAN request [#11672](https://github.com/KSP-CKAN/NetKAN/issues/11672) is open. **v1.0.1 is a test candidate, not a published GitHub release or an indexed CKAN update.** Do not replace the public release until runtime tests pass.

Original artwork. No Near Future Construction assets redistributed. MIT License, SockedRooster. [Repository](https://github.com/SockedRooster/RoosterWorks-Station-Support).
