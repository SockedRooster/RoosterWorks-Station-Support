# v1.0.6 QA

Measured baseline overlap beyond the armor's inner plane: 10.07 mm Hex Medium, 50.07 mm Hex Long. The Long's battery details also extended about 27.07 mm past the armor's outer surface. All six faces had the same issue.

Battery assembly depth changes from 77.07 mm to 62 mm (Medium) / 22 mm (Long), anchored at the existing innermost battery plane. This includes housings, cooling rails, LEDs and cables. Normals use inverse-transpose transformation. Geometry is not moved past the original tank-side plane.

Passed: at least 4.9999 mm armor clearance on all 12 faces after float serialization; inner plane unchanged; tangential coordinates and heights preserved; unit normals; all non-battery vertices/normals identical; UVs, triangles, materials and colliders unchanged. Byte masking proves only mapped battery position/normal records change. Full package comparison allows only two Hex storage MU files and version metadata to differ from v1.0.5.

Battery vertex ownership was recovered from original FBX object IDs and validated against exact equality of all exported Hex body mesh data with the released v1.0.5 assets before use. Mapping audit is in Source/BatteryMaps/AUDIT.txt.

Remaining: KSP rendering check for Open Frame, Armored Panels and Armored Grey on both Hex storage girders. Blender previews are not KSP screenshots. Previously reported in-game verification of selector removal and capacity reductions remains historical confirmation of v1.0.4.
