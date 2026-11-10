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
