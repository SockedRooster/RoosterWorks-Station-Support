# CKAN publishing — RoosterWorks Station Support

## Current stable release

- Tag: `v1.0.8`
- GitHub release: https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/tag/v1.0.8
- Player asset: `RoosterWorks-Station-Support-v1.0.8.zip`
- Metadata: [RoosterWorksStationSupport.netkan](RoosterWorksStationSupport.netkan)
- CKAN listing request: https://github.com/KSP-CKAN/NetKAN/issues/11672

The v1.0.8 player archive is published and the metadata request has been submitted. Submission does **not** establish that indexing has been approved.

## Requirements and packaging

- Kerbal Space Program 1.12.5 (tested target version)
- B9PartSwitch (required)
- ModuleManager (required)
- Neither dependency is bundled with the player ZIP.
- The ZIP must contain `GameData/RoosterWorksStationSupport/` at the expected path.
- CKAN's `$kref` asset filter expects precisely `RoosterWorks-Station-Support-vX.Y.Z.zip`. Attach only the player install ZIP with this name; a developer-source ZIP does not match.

## Future releases

1. Complete in-game testing and offline validation.
2. Update `GameData/RoosterWorksStationSupport/RoosterWorksStationSupport.version`, README, changelog, and release notes.
3. Create a matching GitHub tag and release and upload the player ZIP with the correct filename.
4. Verify the asset downloads, contains the correct `GameData` tree, and does not bundle dependencies.
5. Confirm the CKAN metadata still matches the asset layout and required dependencies. Coordinate any metadata changes with the CKAN maintainers at the request above.
6. Do not broaden the declared KSP compatibility without testing it.

The released v1.0.8 tag is immutable for archival purposes; routine documentation cleanup on `main` does not require a new release.
