# RoosterWorks Station Support v1.0.1

**Not yet the public GitHub/CKAN release.** Please validate behavior in KSP 1.12.5 first.

### Changes since v1.0.0

- Armored girder variants now add 25% to the dry mass (+0.800 t Octo XL, +0.4625 t Octo Medium, +0.190 t Hex Long, +0.105 t Hex Medium).
- All six assets can now themselves attach radially to another part via `node_attach`/`attachRules`.
- New invisible perimeter box colliders on all six assets to encourage exterior surface mounting, instead of attaching inside the truss.
- All existing stack nodes, parts, fuel/charge capacities, names, visible geometry and textures remain unchanged.

**Important limitation:** The Open Frame visual mode also retains the new invisible radial face collision surfaces. No in-game physics or VAB testing has been performed here. If the outer colliders interfere with planned station layouts, please report it before release.

**Installation:** Remove previous `GameData/RoosterWorksStationSupport` then extract the `v1.0.1-TEST.zip` into the KSP installation root. Make sure to back up saves and craft files.

**License:** MIT · **Author:** SockedRooster · **KSP:** 1.12.5 · **Source:** https://github.com/SockedRooster/RoosterWorks-Station-Support
