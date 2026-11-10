# RoosterWorks Station Support v1.0.10

- Adds three wired girder adapters linking 1.25, 2.5 and 3.75 m frames, plus a six-way storage hub and docking coupler in each diameter.
- Adds optional Kerbalism life-support interiors across the straight girder sizes, with oxygen, nitrogen, food and water capacity scaled to the girder.
- Updates girder joints, wire connections and label orientation. Docking couplers include an integrated battery, a steady approach light and aligned docking control transforms.
- Protects B9-selected battery capacity during undocking. KRnD upgrades are disabled on the six switchable storage girders and three hubs.
- Recommends RoosterWorks Station Modules and RoosterWorks Ground Modules in CKAN.

## Known issue

The docking-port light fades out once when Blink is enabled and stays dark. Turning Blink off restores steady illumination.

# v1.0.9 — 2026-11-02

- Detailed truss frames, larger battery banks, enlarged pressure vessels, seated restraint mounts and supports reaching the outer frame.
- One main-part selector offers Standard equipment, Battery Only, Empty Frame, Central Service Core, LF/Ox, Liquid Fuel, Oxidizer, Monopropellant and Xenon.
- Matching core end collars and continuous blue/yellow wiring, with corrected branch-to-core alignment.
- Independent open/white/grey armor choices; accepted adapters retained.
- Original Hollow part IDs remain hidden compatibility entries so existing craft can still load them.
- Corrected native model texture tables and integer entry costs. Fuel capacities follow enlarged tanks; existing Standard/Battery capacities are retained.

# v1.0.6 — 1.25 m battery clearance fix

- Correct battery/armor overlap on Hex Medium and Hex Long storage girders.
- All battery assembly surfaces now lie at least 5 mm behind the inner armor face, for both light and grey armor.
- Battery radial depth is reduced while its inner plane remains fixed, retaining tank-side space. Height and width remain unchanged; normals are updated for correct lighting.
- Only the two Hex storage models and version metadata change. Resources, mass, price, all other models, armor finishes, attachment nodes, textures and compatibility patches remain unchanged from v1.0.5.

Install this package's GameData contents over the previous version with KSP closed, then restart KSP. Existing crafts use the corrected model geometry automatically; no resource/config migration is introduced by this update.

Offline clearance and exact-delta checks passed. Blender geometry preview was inspected. Actual KSP rendering still needs confirmation.


## Previous changes

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
