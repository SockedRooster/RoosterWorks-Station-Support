# RoosterWorks Station Support v1.0.10

- Adds three wired girder adapters linking 1.25, 2.5 and 3.75 m frames, plus a six-way storage hub and docking coupler in each diameter.
- Adds optional Kerbalism life-support interiors across the straight girder sizes, with oxygen, nitrogen, food and water capacity scaled to the girder.
- Updates girder joints, wire connections and label orientation. Docking couplers include an integrated battery, a steady approach light and aligned docking control transforms.
- Protects B9-selected battery capacity during undocking. KRnD upgrades are disabled on the six switchable storage girders and three hubs.
- Recommends RoosterWorks Station Modules, RoosterWorks Ground Modules, and RoosterWorks Inflatable Fuel Depot in CKAN.

## Known issue

The docking-port light fades out once when Blink is enabled and stays dark. Turning Blink off restores steady illumination.

## Installation

Close KSP and replace the existing GameData/RoosterWorksStationSupport folder with the one from the release ZIP. If upgrading from the early expansion tests, move RoosterWorksGirderExpansion and RoosterWorksKerbalismSupport out of GameData. Restart KSP.

Install ModuleManager and B9PartSwitch. The optional life-support interiors also require Kerbalism Default and Community Resource Pack.

For steady docking illumination, turn the approach light on and leave Blink off. If the ring fades out, turn Blink off to restore it.

## Developer source

See SOURCE_UPDATE.md for the release baseline and packaging command.

## License

Copyright (c) 2026 SockedRooster.

This project uses **dual licensing**:

- **Art assets:** All `.dds`, `.png`, and `.mu` files are **All Rights Reserved**. You may not redistribute or re-use these assets without express permission from the author.
- **Everything else:** Original source code, configuration files, documentation, and other non-art files are distributed under the **MIT License**, subject to its terms.

See the full [LICENSE](LICENSE) file for the MIT permission notice, conditions, and warranty disclaimer. Third-party content and dependencies retain their respective licenses; this notice does not grant rights to third-party assets.

## Dependency downloads

Install required dependencies separately before using this mod. Optional and feature-specific dependencies are only needed for the indicated integrations. CKAN can manage dependencies when available.

| Dependency | Use |
|---|---|
| [ModuleManager](https://github.com/sarbian/ModuleManager/releases) | Required |
| [B9 Part Switch](https://github.com/blowfishpro/B9PartSwitch/releases) | Required |
| [Kerbalism](https://github.com/Kerbalism/Kerbalism/releases) | Optional life-support integration |
| [Community Resource Pack](https://github.com/BobPalmer/CommunityResourcePack) | For optional Kerbalism integration |

Third-party mods remain the property of their respective authors and are distributed under their own licenses. Follow their installation instructions and use versions compatible with your KSP installation.
