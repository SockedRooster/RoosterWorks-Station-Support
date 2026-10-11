# RoosterWorks Station Support — developer source

The authoritative **v1.0.1 gameplay files** are under `GameData/RoosterWorksStationSupport/`. Nothing in this `Source/` directory should be copied into a player's KSP `GameData`.

## Approved native model sources

- `Blender/Approved_RW_OctoSupport_XL.blend` and `Blender/Approved_OctoXL_INTERMEDIATE.fbx` preserve the approved Octo XL source and export.
- `Blender/Approved_OctoXL_Builder_USER_EDITED.py` preserves the creator-edited Blender construction script.
- `Blender/RoosterWorks_Girder_Builder.py` is the editable general-purpose Blender construction script.
- `FiveFBXExports/*_INTERMEDIATE.fbx` stores the other five approved source exports.
- `Conversion/convert_station_fbx.py` and `Conversion/parse_rw_fbx.py` implement native KSP `.mu` conversion.

The approved **visible geometry** was unchanged between v1.0.0 and v1.0.1. The v1.0.1 converter adds hidden `RadialFaceCollider_XX` box colliders along the outer polygon faces. These colliders exist in both Open Frame and Armored modes. Stock `ModulePartVariants` changes the visible armor and additive dry mass, not the resource capacity.

## Rebuilding models

Rebuilding is for **development only**: it rewrites tracked models and textures, potentially changing tested binaries.

```bash
python -m pip install -r Source/Conversion/requirements.txt
python Source/Conversion/convert_all.py
python Source/verify_release.py
python Source/verify_v101.py
```

The first converter uses the approved FBXs in `Source/Blender/` and `Source/FiveFBXExports/`. Preserve or review the existing GameData before running it.

## Validation and release packaging

`verify_release.py` checks all six KSP models/configs at a basic level. `verify_v101.py` checks v1.0.1 radial colliders, variant mass, resources and version; it optionally accepts `--baseline-zip path/to/v1.0.0.zip` for binary regression comparison.

The repo-root `CHECKSUMS-SHA256.txt` lists the expected hashes of released v1.0.1 GameData files. Recheck it before publishing. Static checks are not substitutes for VAB/flight tests; creator testing for v1.0.1 was reported as passed.

## Historical development

Earlier prototype scripts generated `RoosterWorksKerbalismAdditions` instead of the current `RoosterWorksStationSupport` folder and were removed to prevent accidental builds from obsolete code. Legacy conversion details remain recoverable in Git history. Do not reintroduce old prototype files into player releases.
