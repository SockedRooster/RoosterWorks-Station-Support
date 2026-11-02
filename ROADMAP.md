# RoosterWorks Station Support — Development Roadmap

This document describes **potential future parts**, not changes included in the currently published release. The released v1.0.8 gameplay files are unaffected by roadmap ideas.

## Current stable baseline — v1.0.8

- Six main support girders in 1.25 m, 2.5 m and 3.75 m families, plus three adapters.
- Six legacy Hollow IDs remain loadable for existing craft, bringing the total to 15 existing part IDs.
- Nine interior/storage selections on the main girders, including EC + MonoPropellant, Battery Only, Empty Frame, Central Service Core, fuel and xenon options.
- Open Frame, Armored Panels and Armored Grey girder appearances; White and Armored Grey adapter appearances.
- Preserved attachment interfaces, external colliders and compatibility with existing saves and craft.
- Current storage switching requires B9PartSwitch; ModuleManager is also a required dependency for compatibility patches.

## Next structural expansion — 5 m and 7.5 m (planned)

Introduce larger structural support options suitable for massive orbital stations, shipyards and deep-space construction, while maintaining the existing RoosterWorks design language.

### 5 m support family

- **5 m large-diameter girders**, with at least short/medium and long-length options to support modular assembly.
- Matching **open-frame and armored-panel variants** so users can customize appearance, mass and protection style.
- Large stack connection nodes, attachment geometry and radial attachment behavior specifically designed for 5 m modules.
- Internal ElectricCharge and MonoPropellant storage where suitable, balanced for the increased physical volume and dry mass.
- **Transition adapters** to existing station components and the future RoosterWorks Station Modules 5 m interfaces.

### 7.5 m heavy station family

- **7.5 m super-heavy support girders**, intended for large interplanetary stations, orbital construction platforms and oversized habitation structures.
- Short and extended segments to avoid forcing extremely long structural assemblies.
- Open Frame / Armored Panels options, with visually plausible large-scale framing and appropriate mass trade-offs.
- Structurally appropriate attachment nodes, radial snap positions and exterior colliders for stable construction.
- Appropriately balanced onboard electrical and monopropellant storage rather than directly copying capacities from small girders.
- **7.5 m to 5 m transition adapters** and additional interfaces as required by the final Station Modules catalog.

### Shared requirements and quality gates

1. Generate original meshes and textures programmatically using the established Blender/FBX-to-KSP `.mu` pipeline; retain editable source projects and scripts.
2. Reuse the current RoosterWorks styling: white panels, exposed steel framing, bronze/metallic detailing, brand plates and practical external fixtures.
3. Model the 5 m / 7.5 m dimensions accurately. Verify KSP node orientation, scale, collider footprints, VAB/SPH attachment and symmetry.
4. Account for significantly larger volumes with realistic **dry mass, cost, resource capacity and physics**. Do not simply scale mass linearly with diameter.
5. Preserve existing 1.25 m / 2.5 m / 3.75 m part names and functionality; the new parts should have unique internal IDs.
6. Keep **Kerbalism optional**: built-in storage uses stock persistent resources and should remain usable without Kerbalism. Any Kerbalism-specific configuration must be separately tested.
7. Confirm compatibility with **RoosterWorks Station Modules**, including its planned realistic and futuristic station families; avoid duplicating habitable modules inside Station Support.
8. Conduct focused in-game tests: launching, stacking, radial mounting, armor switching, resource persistence, performance and save/load.

**Scope and timing:** Planned for a future version **after v1.0.8**. The exact release number, part dimensions/lengths, adapters and capacities will be finalized during prototyping, not assumed complete here.

## Longer-term ideas (not committed to a release)

- Additional reinforced ring/junction and connection hardware for large orbital structures.
- Optional matching truss-mounted utility equipment, provided it does not duplicate the separate Station Modules addon.
- Performance-optimized variants for very large assembled stations.

**Important:** This roadmap does not add gameplay parts, change v1.0.8 models, or publish a new release.
