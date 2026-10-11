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
