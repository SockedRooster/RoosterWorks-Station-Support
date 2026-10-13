# Canonical v1.0.3 build

Use build_configs_v103.py and add_grey_to_models.py with the v1.0.2 player ZIP. Both are idempotent and use only Python's standard library. Verify with verify_v103.py using that same baseline.

Grey armor is a duplicate ArmorPanelsGrey transform of ArmorPanels, with identical geometry and transforms. Only white-panel mesh material index 2 (RW_white) changes to index 0 (RW_steel); gold/bronze seams retain their material. Every variant explicitly controls both panel groups. Open enables neither, Armored enables only original armor, ArmoredGrey enables only grey armor. Grey cost and mass exactly match white armor. All existing geometry and colliders are untouched.

The 3.75 m configs reuse Octo models with rescaleFactor 1.5. Source node positions remain unchanged because KSP applies rescaleFactor to them; only stack node size changes from 2 to 3. Dimensions scale 1.5; volume-proportional balance scales 3.375. Resource values first receive the 60% reduction, then are scaled for 3.75 m and rounded half up to whole units.

The inherited FBX converter now emits grey groups too, but some historical released source/models differed. Do not substitute a complete FBX reconversion when aiming to reproduce this exact release. The binary-preserving builder is the canonical path. Blender/FBX source remains available for future asset editing.

The reader supports byte input, allowing validation without temporary extraction. Grey subgroup duplication increases stored mesh data, but variants expose only one armor group at a time.

Version-specific old notes, preview tools and tests describe their named historical builds. Current verification is verify_v103.py. Existing saves are not migrated.
