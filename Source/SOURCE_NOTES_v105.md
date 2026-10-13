# v1.0.5 adapter finishes

After building v1.0.3 and applying v1.0.4 as documented, run `python Source/apply_v105.py`. This is idempotent. An optional `--baseline-zip <v1.0.4-player.zip>` verifies the entire game-data delta.

The two adapter models each have one Body_white_00 mesh with material index 2 (RW_white). The builder duplicates only that child node into Body_grey_00, changes its material index to 0 (RW_steel), and preserves all existing binary model data. Gold trim, labels and structural details are shared and untouched. Existing colliders stay active regardless of finish. The 3.75 m adapter reuses the Octo model at its existing scale.

All three adapter configs gain one stock ModulePartVariants module: White and ArmoredGrey, with explicit mutually exclusive mesh toggles. Mass/cost offsets are zero and White is the baseVariant. No additional armor is being installed; this is a finish on the existing solid adapter shell.

No new dependency or runtime plugin is added. The v1.0.4 compatibility patch already covers these adapter IDs and continues to remove the redundant ModuleRWStationFinish field.

The historical FBX converter does not generate these new adapter alternatives; apply_v105.py is the canonical final step for the released adapter assets. All prior build tools and sources remain available.
