# Current source notes: v1.0.2

All work is based on the supplied v1.0.1 player and developer archives. Original archives and Blender/FBX references were not modified.

`convert_station_fbx.py` adds optional hollow mode. It skips source objects beginning Monopropellant_, Battery_Face_, Central_Service_Spine, Lower_, or Upper_. In these supplied models, Lower_/Upper_ are only the inner end-ring/spoke assemblies. The exterior frame, joints, diagonal braces, identification plate and armor remain. Hollow outputs omit EquipmentCollider, retaining only perimeter rail and radial-face collision boxes. Hollow mode rejects adapters.

`convert_hollow.py` builds four *_Hollow.mu assets. Existing release textures are retained byte-for-byte by the converter; placeholder generation is used only when a texture is absent. Existing six MU files in this release are the supplied v1.0.1 binaries, not reconverted copies.

Four new part configs use unique *_Hollow IDs and new models; resources are absent. Open base price, dry mass and entry cost are 50% of their storage equivalents. Armor mass matches the corresponding storage shell. Every armored variant adds exactly 10% of its own open base price. Original configs change only by explicit Open/Armored cost fields.

Separate part definitions avoid introducing a plugin or attempting to change fixed resources with a mesh-only stock variant. Existing craft IDs, nodes, storage resources and original models remain unchanged.

Symmetry: the installed KSP 1.12.5 EditorLogic.UpdateSymmetry selects potentialParent.transform.up for Parent radial mode and rootPart.transform.up for Vessel radial mode. Therefore an axis mismatch on a sideways girder explains center-only alignment without a model change. Documented as a likely diagnosis until reproduced with the user's craft. No game code is redistributed or patched.

Verification: run `python Source/verify_v102.py --baseline-zip <v1.0.1-player.zip>` (Python standard library only). It parses MU records, verifies original assets, tests hollow clearance using projected triangle interiors/edges and oriented perimeter boxes, and compares retained frame/armor triangles to the original models. Blender previews use `blender --background --python Source/preview_hollow.py`.

The original Blender projects remain storage versions; rebuild Hollow outputs with the converter filter. Older verify scripts and source notes describe older releases only. Do not use their fixed six-part/version assertions for v1.0.2.
