# v1.0.8-dev.2 model-loading correction

The installed KSP.log showed six support model imports failing with TextureError (14 versus 11 or 12) and subsequent missing-model errors. Their unused trailing texture entries are now removed. Geometry, materials, attachment nodes, colliders, and all 15 original part IDs are unchanged. Two inherited fractional entryCost values on the 3.75 m medium parts are rounded to integers required by KSP.

Close KSP and extract the Install ZIP into the KSP folder, merging GameData and replacing the RoosterWorksStationSupport files. Keep B9PartSwitch and ModuleManager installed. Restart KSP fully to reload the models.

Stocked girders offer Standard equipment, Battery, LF/Ox, Liquid Fuel, Oxidizer, Monopropellant and Xenon through their Storage selector. Separate Hollow parts offer Empty Frame or Central Service Core only. Armor remains an independent appearance selector.

Load the original save after restarting. If a save was overwritten after accepting removal of missing vessels, restore a backup from before that removal; this update does not reconstruct deleted vessels. No save files have been edited by this correction.

Offline checks cover the newly added loader-table and integer constraints, all 15 original IDs, 42 storage options, resources, transforms, geometry and colliders. Geometry was compared directly before/after serialization. In-game acceptance still needs a fresh KSP launch; no claim of an in-game test is made. No Blender render was required. Repair, validation and packaging workers run at idle priority on one CPU core.
