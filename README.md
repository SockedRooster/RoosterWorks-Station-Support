# RoosterWorks Station Support

**Version:** v1.0.0  
**Author:** SockedRooster  
**License:** MIT  
**KSP:** Kerbal Space Program 1 (built for 1.12.5)  
**Repository:** https://github.com/SockedRooster/RoosterWorks-Station-Support

Original station construction components for KSP 1: four rigid structural girders with integrated ElectricCharge and MonoPropellant, plus two octagonal/hexagonal stack adapters. The parts are designed for use with **Kerbalism**, but require **no Kerbalism plugin or other mod** to load.

## Features

- Original RoosterWorks Blender-modeled frames, monopropellant vessels, internal batteries, structural joints and readable identification badges.
- **Open Frame** or **Armored Panels** selectable on all four girders using KSP's native part-variant system. The selection does not change part mass, resources or physics colliders.
- Permanent **ElectricCharge and MonoPropellant RESOURCE** definitions, avoiding reliance on runtime resource switching.
- Two rigid adapters for standard **2.5 m** and **1.25 m** stack parts; no fuel storage in adapters.
- Stock **Structural** VAB category and career technology unlocks; optional VAB Organizer grouping under **Trusses** and **Adapters**.
- No Near Future Construction model, texture or artwork is redistributed.

## Parts

| Part | Approximate envelope | Internal layout | ElectricCharge | MonoPropellant | Career node |
| --- | --- | --- | ---: | ---: | --- |
| Octo XL Girder | 2.5 m × 4.75 m | 4 vessels | 9,000 | 1,500 | Specialized Construction |
| Octo Medium Girder | 2.5 m × 2.65 m | 3 vessels | 4,500 | 750 | Specialized Construction |
| Hex Long Girder | 1.25 m × 3.15 m | 4 vessels | 1,200 | 200 | Advanced Construction |
| Hex Medium Girder | 1.25 m × 1.75 m | 1 vessel | 600 | 100 | Advanced Construction |
| Octo → 2.5 m Adapter | 2.5 m interface | Stack adapter | — | — | Specialized Construction |
| Hex → 1.25 m Adapter | 1.25 m interface | Stack adapter | — | — | Advanced Construction |

## Installation (manual)

1. Quit KSP. Back up your save and any crafts using previous test versions.
2. Delete the old `GameData/RoosterWorksStationSupport` folder before installing. **Do not merge** test and release files.
3. If the older prototype `GameData/RoosterWorksKerbalismAdditions` is still installed, remove it to prevent duplicate part IDs.
4. Extract **`RoosterWorks-Station-Support-v1.0.0.zip`** into the KSP installation **root**. The final part folder must be `Kerbal Space Program/GameData/RoosterWorksStationSupport/`.
5. Launch KSP and locate the six parts under **Structural**. If VAB Organizer is installed, they should appear under its Trusses and Adapters subcategories.

Do not place a second `GameData` folder inside your existing `GameData` directory.

## Operation

- Select **Open Frame** or **Armored Panels** in the VAB using the part's variant selector. Adapters do not offer this selector.
- Girders store their EC and MonoPropellant directly on the part, and are not generators or fuel producers.
- Parts have top and bottom stack nodes; all four girders are fixed **Support-only** configurations.

## Known limitations and release validation

- The complete six-part set has been visually approved in the VAB by its creator; **full flight testing, save/reload, adapter physics and Kerbalism background resource persistence are not comprehensively verified**. Perform these checks before relying on the pack in a valuable save.
- The included KSP/Diffuse color textures are simplified placeholders; Blender PBR surface detail has not been baked into game textures.
- The green battery LED details are **static**, not actually blinking in KSP.
- These high-detail models are not optimized for very large craft with numerous repeated parts.
- The armored plating is a visual variant; physical collision uses the same simplified rigid collider approximation in both modes.

See `TEST_CHECKLIST.md` for focused verification steps and `CHANGELOG.md` for the release history.

## Compatibility and dependencies

- Designed for KSP **1.12.5**.
- No required external plugin or ModuleManager patch.
- Kerbalism and VAB Organizer are **optional**, not hard dependencies. Kerbalism-specific persistence still requires live testing in your installation.
- Existing six part identifiers are retained from the v0.8.x prototypes for craft compatibility. Back up saves before upgrading.

## Source / licensing

The models, scripts, textures, configs and documentation are released under the **MIT** license in `LICENSE`. The `Source/` directory contains editable Blender and FBX inputs plus the custom conversion utilities. No assets from Near Future Construction are bundled. Attribution: **SockedRooster / RoosterWorks**.

Report bugs or feature requests through the [GitHub Issues](https://github.com/SockedRooster/RoosterWorks-Station-Support/issues) page.
