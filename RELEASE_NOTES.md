# RoosterWorks Station Support v1.0.8

**Stable release — November 2, 2026**  
Target: Kerbal Space Program 1.12.5  
Author: SockedRooster  
License: MIT

This release modernizes the station support girder family with selectable internal equipment, refreshed models and materials, and aligned service connections. It consolidates the tested 1.0.6 battery clearance fix, 1.0.7 selectable battery storage, and the 1.0.8 visual/interior/wiring development builds into a stable release.

## What's new

- **Complete visual overhaul:** beveled frames, braces, mounting plates, fasteners, improved equipment and materials, recessed battery drawers, pressurized storage vessels and dedicated xenon bottle racks.
- **One Storage selector on each of the six main girders:** EC + MonoPropellant (Standard), Battery Only, Empty Frame, Central Service Core, LF/Ox, Liquid Fuel, Oxidizer, Monopropellant, and Xenon Gas. Interiors and associated equipment geometry change with the selected mode.
- **Battery-only capacity:** Hex Medium 2,000 EC; Hex Long 4,000 EC; 2.5 m Octo Medium 15,000 EC; 2.5 m Octo XL 30,000 EC; 3.75 m Octo Medium 33,000 EC; 3.75 m Octo XL 66,000 EC.
- **New fuel and xenon options:** tank sizes and masses balanced to the equipment volumes; LF/Ox follows a 9:11 ratio. The Standard storage selection retains its previous EC/MonoPropellant capacities.
- **Better stacked-part continuity:** matched coupling collars, frame-mounted tank restraints, and blue/yellow service wiring that meets the external service lanes at both ends. The v1.0.8-dev.4 wiring mismatch is corrected.
- **Appearance options retained:** Open Frame, Armored Panels and Armored Grey remain independent of interior storage; adapters retain White / Armored Grey options.
- **Legacy craft compatibility:** all 15 existing part IDs remain available. The six former Hollow IDs remain loadable for existing craft, but are hidden from the editor in favor of Empty Frame and Central Service Core selections on the main girders.
- **Earlier maintenance fixes included:** the 1.25 m battery/armor clearance correction, new 3.75 m parts, and scoped removal of the duplicate exterior-finish control added when Station Modules is installed.

## Requirements

- Kerbal Space Program **1.12.5** (target version)
- **B9PartSwitch** (required for Storage/interior selections)
- **ModuleManager** (required for compatibility patches)

The dependencies are **not included** in the download. RoosterWorks Station Modules is not required.

## Installation / upgrading

1. Close KSP and back up saves and the existing `GameData/RoosterWorksStationSupport` folder.
2. Remove the old `GameData/RoosterWorksStationSupport` folder to prevent obsolete files from remaining.
3. Extract the release ZIP into the Kerbal Space Program directory, preserving the `GameData/RoosterWorksStationSupport` path.
4. Ensure B9PartSwitch and ModuleManager are installed, and launch KSP.

The supplied ZIP is a **full replacement**, not a patch. Do not install multiple copies. Existing saves/craft can retain serialized resource amounts, so verify previously placed switched parts in a backup save and replace/re-save parts if needed. Switching interiors is editor-only.

## Validation

The author reports that the build was **tested in game** and approved for release. Re-ran the included offline validator for this release: **PASS** (15 parts, 10 models, 42 stocked-resource selections, 24 empty/core selections, 64 service-core wiring junctions, plus collision, texture, geometry and adapter-baseline checks). Source and player GameData files were confirmed byte-identical before release metadata updates.

## Downloads

- `RoosterWorks-Station-Support-v1.0.8.zip` — install package for players and CKAN release-asset matching.
- `RoosterWorks-Station-Support-v1.0.8-Developer-Source.zip` — full GameData, editable source, conversion tools, preview art, checks and historical documentation.

For CKAN, the `.netkan` file targets the **exact player ZIP naming pattern** above. CKAN indexing is separate from releasing on GitHub.
