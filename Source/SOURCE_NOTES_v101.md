# Native model conversion — v1.0.1

The visible FBX meshes are unchanged from the approved v1.0.0 source; the converter now inserts hidden `RadialFaceCollider_XX` box colliders after the prior rail/equipment (or adapter) colliders and before the material table. Boxes use per-node Unity yaw quaternions to make a shallow continuous polygonal outer face against which surface attachments can raycast.

Build: `python Source/Conversion/convert_all.py` (NumPy, SciPy and Pillow required). Approved Octo XL source lives in `Source/Blender/Approved_OctoXL_INTERMEDIATE.fbx`; the other five FBXs live in `Source/FiveFBXExports/`.

New stock KSP config fields: `node_attach = ...`, `attachRules = 1,1,1,1,0`, `baseMass = 0`, and `VARIANT.mass = ...` additive armor dry mass. No additional dependencies.

Regression checks verify identical old mesh/collider bytes prior to the additional colliders; new collider runtime behavior has NOT been validated in Unity or KSP. Please test prior to publishing.
