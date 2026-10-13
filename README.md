# RoosterWorks Station Support v1.0.5

Author: SockedRooster · MIT · KSP 1.12.5 · No required plugin

## v1.0.5 changes

- All three adapters (Hex 1.25 m, Octo 2.5 m, Octo 3.75 m) now offer **White** and **Armored Grey** in the normal Variant selector. White is the default.
- Grey uses the same steel-grey material as the girder armor and retains the gold trim. The finish change is cosmetic, with zero added cost or mass.
- Only adapter shell variants were added; all girders, storage capacities, prices, attachment nodes and the extra-selector removal patch remain as in v1.0.4.
- The user verified v1.0.4's selector removal and capacities in-game. This new adapter option has passed offline geometry/config checks and still needs its own in-game selection/save-load check.

## v1.0.4 changes

- The 3.75 m storage girders have a further 35% reduction in both EC and MonoPropellant versus v1.0.3, rounded to whole units. Initial fill matches the new capacity. Other sizes and hollow parts are unchanged.
- Remove the redundant **Exterior finish** selector from Station Support parts when RoosterWorks Station Modules is also installed. Keep **Open Frame**, **Armored Panels**, and **Armored Grey** in the stock Variant selector. Armor appearance, price and mass are unchanged.
- The selector fix is a ModuleManager compatibility patch restricted to the 15 exact Station Support IDs. It runs after Station Modules adds its finish module; it does not alter Station Modules parts or its plugin. Standalone Station Support needs no additional plugin.

## Existing features

- Reduce ElectricCharge and MonoPropellant capacities by exactly 60% on the original storage girders: 40% remains. Initial fill is reduced to match. Existing base prices and dry masses stay unchanged.
- Add a 3.75 m octagonal family: Medium and XL storage girders, matching Hollow girders, and an octagonal-to-round 3.75 m adapter. The package now has 15 parts.
- All 12 girders offer **Open Frame**, **Armored Panels** (original light finish), and **Armored Grey** (grey panels with gold trim). Both armored finishes add the same mass and 10% of the corresponding open base price.
- All previously shipped mesh geometry, original materials/textures, and collision shapes are preserved. Grey armor uses an additional selectable mesh group with grey steel panel material and unchanged gold seams.

## Capacities

| Storage girder | ElectricCharge | MonoPropellant |
|---|---:|---:|
| Hex Medium | 240 | 40 |
| Hex Long | 480 | 80 |
| Octo 2.5 m Medium | 1,800 | 300 |
| Octo 2.5 m XL | 3,600 | 600 |
| Octo 3.75 m Medium | 3,949 | 658 |
| Octo 3.75 m XL | 7,898 | 1,316 |

All Hollow girders remain resource-free. Adapters have no resource storage.

## 3.75 m dimensions and balance

The full octagonal family is uniformly enlarged by 1.5, so diameter is 3.75 m and nominal Medium / XL / adapter heights are 3.975 / 7.125 / 1.11 m. Stack attachment nodes use size3. Models and collision shapes are shared with the 2.5 m family and scaled by KSP.

Base dry mass, armor mass, base cost, armor cost and entry cost scale by volume: 1.5 cubed = 3.375. Storage first used the same scaling in v1.0.3; v1.0.4 reduces those whole-unit capacities by a further 35%, then rounds to the nearest whole unit (half up). Hollow variants retain half the base dry mass and price of the matching storage part, as in v1.0.2.

## Installation and use

With KSP closed, copy the player ZIP's `GameData/RoosterWorksStationSupport` folder into your KSP `GameData` folder and replace existing mod files. Keep one installed copy. This is a full installation, not a patch. The developer ZIP contains the same game files plus source and verification tools.

Find the parts under Structural; search **3.75** for the enlarged family or **hollow** for empty frames. Right-click a girder to select one of the three finishes, or an adapter to select White / Armored Grey. Hollow girders are separate editor entries; their interiors have no tanks, batteries, service spine, inner ring/spoke assemblies or central equipment collider.

The new capacities apply to freshly loaded part definitions and newly placed parts. Existing .craft/save files may retain serialized resource amounts/capacities; replace affected parts in the editor and save a new craft to ensure the reduced values are applied. This build does not migrate existing saves.

## Validation and limits

Offline regression checks passed for all 15 configurations and 10 shared model files: capacities, scaled values, attachment node coordinates/sizes, exactly three exclusive finish choices, armor prices/masses, identical original geometry and colliders, correct grey panel material and unchanged textures. See historical `VALIDATION_v103.txt` in the developer source and current `VALIDATION_v105.txt`. v1.0.4 delta verification confirmed all original assets, variants and other part configs are unchanged.

Blender previews show geometry and approximate materials, not KSP's actual lighting. KSP editor, flight, existing-save migration and Kerbalism persistence tests have not been run. `TEST_CHECKLIST.md` lists the remaining in-game checks.

Inherited limitations: shallow invisible collision walls remain across side faces even in Open Frame mode; hollow passages are open through the ends. LEDs are static and texture/shader detail is simple. Hollow clear bores are over 0.92 m (Hex), 2.0 m (2.5 m Octo), and 3.0 m (3.75 m Octo).

## Developer build

The developer ZIP includes the required v1.0.2 baseline in `Source/Baseline/`. Using Python, run:

```
python Source/build_configs_v103.py --baseline-zip Source/Baseline/RoosterWorks-Station-Support-v1.0.2-TEST.zip
python Source/add_grey_to_models.py --baseline-zip Source/Baseline/RoosterWorks-Station-Support-v1.0.2-TEST.zip
python Source/verify_v103.py --baseline-zip Source/Baseline/RoosterWorks-Station-Support-v1.0.2-TEST.zip
python Source/apply_v104.py
python Source/apply_v105.py
```

These standard-library-only scripts reproduce the release configs/models while preserving the previous geometry. Included Blender/FBX conversion scripts also support grey armor, but are an alternative asset-editing path: the historical FBX references do not exactly reproduce every manually adjusted released model. Older version notes and verification scripts are historical. See `Source/SOURCE_NOTES_v105.md`, `Source/SOURCE_NOTES_v104.md` and historical `Source/SOURCE_NOTES_v103.md`.

This local test build has not been published to GitHub or CKAN. Original artwork, author attribution and MIT license retained.
