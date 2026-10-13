# v1.0.4 source

Rebuild v1.0.3 configs/models using the included v1.0.2 baseline and the documented build_configs_v103.py / add_grey_to_models.py scripts. Run the v1.0.3 verification before applying v1.0.4. Then run `python Source/apply_v104.py` to set the two new capacities, generate the compatibility patch and bump the version. All source scripts are retained.

Optional full delta verification: `python Source/apply_v104.py --baseline-zip <v1.0.3-player.zip>`. This compares all game files, allowing changes only in the two 3.75 m storage configs/version plus the new compatibility patch. It proves models, textures, variants and other part configs are unchanged.

The finish selector is supplied by a separate installed addon, not this package. RoosterWorksStationModules/Compatibility/ExteriorFinish.cfg contains @PART[RW_*]:HAS[!MODULE[ModuleRWStationFinish]]:FOR[RoosterWorksStationModules]. The new compatibility file uses an explicit part-ID allowlist and AFTER[RoosterWorksStationModules] to delete that module only from Station Support parts. It neither removes the finish DLL nor modifies Station Modules files.

v1.0.3 previews are still accurate for appearance; no geometry/material changes are made here. Older notes and verification logs are historical. Existing saved resource capacities are not migrated.
