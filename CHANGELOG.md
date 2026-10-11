# Changelog

## v1.0.1 — Armor Balancing & Radial Attachment (2026-10-11)

- Armored Panels now add **25% to Open Frame dry mass** on all four girders via stock `ModulePartVariants`: Octo XL +0.800 t, Octo Medium +0.4625 t, Hex Long +0.190 t, Hex Medium +0.105 t.
- Enabled radial attachment for all six station parts with exterior `node_attach` positions; original stack attachment nodes remain unchanged.
- Added six (Hex) or eight (Octo) invisible polygon perimeter colliders per model to improve external surface mounting, while preserving the original collision geometry.
- Preserved existing visible meshes, textures, names, costs, resource capacities and part IDs.
- VAB and flight testing reported successful by the author.
- Known behavior: perimeter attachment colliders also apply in Open Frame mode.

## v1.0.0 — Initial release (2026-10-09)

- Six original RoosterWorks station components: four resource-bearing girders and two stack adapters.
- Stock Open Frame/Armored Panels visual variants; integrated permanent ElectricCharge and MonoPropellant storage; original models and branding.
- MIT license, KSP 1.12.5 configuration, GitHub release and NetKAN metadata.
