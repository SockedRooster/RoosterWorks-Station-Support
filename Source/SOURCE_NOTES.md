# Station Support v0.8.4 developer notes

`DeveloperSource/Conversion/convert_station_fbx.py` applies two scoped v0.8.4 changes:

1. Octo XL: rotate every `Battery_Face_##_...` object 180 degrees around the local vertical axis through the corresponding battery face center, including LED meshes and trim.
2. Octo XL and Octo Medium: move all nameplate assembly submeshes 17 mm outward, without touching text size or mirroring.

Regenerate only the two Octo .mu assets from the included original FBX files. All four remaining .mu files and six part .cfg files were carried forward byte-for-byte from v0.8.3.

Original approved Blender .blend and author-edited Python builder remain included. Do not rerun the old builder to apply this hotfix: the authoritative KSP change is intentionally scoped to converter output.

## v1.0.0 release
The approved v0.8.4 `.mu` meshes and `.cfg` files are authoritative for the v1.0.0 player archive; retained converter utilities represent the reproducible development pipeline and preserve legacy v0.8.x filenames. Running source converters again may require Blender or FBX dependencies and is **not** necessary to install the mod.
