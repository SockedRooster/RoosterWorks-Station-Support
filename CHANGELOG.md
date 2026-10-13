# v1.0.5 — adapter finish update

- Add White (default) / Armored Grey variants to the 1.25 m Hex, 2.5 m Octo and 3.75 m Octo adapters.
- Grey shells match the existing grey girder armor and retain gold trim. No extra mass or cost.
- All girder geometry, resources, costs, attachment nodes and v1.0.4 compatibility behavior are unchanged.

With KSP closed, copy this package's GameData contents over the existing Station Support installation and restart KSP. Both adapter model files and all three adapter configs must be updated together. Choose Armored Grey from the adapter's normal Variant selector.

Offline geometry/config/delta checks passed. The user verified v1.0.4 selector removal and capacities in-game; the newly added adapter variants still need an in-game selection and save/reload check.


## Previous changes

# v1.0.4 — TEST BUILD

- 3.75 m Medium: 3,949 ElectricCharge / 658 MonoPropellant.
- 3.75 m XL: 7,898 ElectricCharge / 1,316 MonoPropellant.
- Both represent a further 35% reduction from v1.0.3, rounded to whole units; initial fill and capacity are both changed.
- Add a narrowly scoped compatibility patch to remove the extra Exterior finish selector injected by RoosterWorks Station Modules. Open Frame, Armored Panels and Armored Grey remain available in the normal Variant selector.
- Other sizes, hollow parts, models, textures, armor costs/masses and attachment nodes are unchanged.

With KSP closed, install this ZIP's GameData contents over the previous Station Support version, including the new Compatibility folder. Restart KSP to apply the compatibility patch. No changes to the Station Modules installation are necessary.

For existing craft, replace affected 3.75 m storage parts to ensure saved resource capacities are updated. Offline delta checks passed; live KSP/ModuleManager behavior has not been tested here.


## Historical changes

# v1.0.3

- 60% EC/MonoPropellant capacity reduction on existing storage girders.
- 3.75 m octagonal Medium/XL, hollow versions, and adapter.
- Armored Grey finish with identical armor mass and price premium.
- Exact preservation of existing model geometry/colliders during grey-group addition.

## Historical releases

# v1.0.2 — local test candidate

- Armor costs 10% more than the corresponding open girder.
- Four additional hollow structural parts, without stored resources or center collision blocks.
- Original six models and textures preserved exactly; original resource capacities and nodes retained.
- Added clear-bore, original-geometry, config and price regression checks plus Blender previews.
- Added guidance on Vessel vs Parent radial symmetry; runtime reproduction remains pending.

## Previous history

# Changelog

## v1.0.1 — Armor Mass & Radial Attachment Test (2026-10-09)

- Four girders: Armored Panels now add **25% of the original dry mass** with stock `ModulePartVariants`: +0.800, +0.4625, +0.190, +0.105 tonnes respectively. Open Frame mass and EC/MonoPropellant capacities are unchanged.
- All six parts: added `node_attach` located on an outer polygon face and enabled **surface attachment as child parts**, retaining existing top/bottom stack nodes.
- All six `.mu`: added six or eight shallow outer-face box colliders so surface-attached parts are less likely to snap into the inner equipment volume. Original colliders retained; invisible colliders apply equally in Open Frame and Armored Panels.
- All six visible meshes and all eight texture files preserved from v1.0.0, confirmed by model-binary prefix and texture hash checks.
- Native Blender, FBX and converter source included; KSP gameplay validation still required.
- **No live GitHub update; do not mark v1.0.1 as CKAN-ready until user VAB and flight checks pass.**

## v1.0.0 — Initial release (2026-10-09)

- Six original RoosterWorks parts. Four permanent EC / MonoPropellant girders, two stack adapters.
- Original approved v0.8.4 visual geometry, optional armor plating, corrected outward batteries and nameplates.
- MIT license, KSP1 1.12.5 packaging, GitHub source and CKAN metadata.
