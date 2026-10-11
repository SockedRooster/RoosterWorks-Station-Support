# CKAN Publishing Guide — RoosterWorks Station Support

**Mod:** RoosterWorks Station Support  
**Author:** SockedRooster  
**CKAN identifier:** `RoosterWorksStationSupport`  
**KSP compatibility declared:** 1.12.5  
**License:** MIT

## Current submission

The initial CKAN indexing request is [KSP-CKAN/NetKAN #11672](https://github.com/KSP-CKAN/NetKAN/issues/11672). **Do not create another request for v1.0.1.** Instead, add a comment with the updated release URL after publishing.

The metadata source remains `CKAN/RoosterWorksStationSupport.netkan`. It selects GitHub release assets named `RoosterWorks-Station-Support-vX.Y.Z.zip` and installs **only** the `RoosterWorksStationSupport` folder into `GameData`. No additional plugin dependencies are required.

## Publish v1.0.1

1. Ensure `main` contains the approved v1.0.1 GameData assets and up-to-date `README.md`, `CHANGELOG.md`, and `RELEASE_NOTES.md`.
2. **Fix the stale `v1.0.1` Git tag:** the tag left behind when the earlier release was removed pointed at the original v1.0.0 commit. Delete **only** the incorrect lowercase `v1.0.1` tag, then recreate `v1.0.1` at the final v1.0.1 commit on `main`. Leave the original `V1.0.0` tag and release unchanged.
3. Create the new [GitHub release](https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/new) using the corrected `v1.0.1` tag. Title: **RoosterWorks Station Support v1.0.1**.
4. Attach **`RoosterWorks-Station-Support-v1.0.1.zip`**, containing only the installable `GameData/RoosterWorksStationSupport/` tree. This is the player package; do not use the developer source ZIP as the CKAN target.
5. Use `RELEASE_NOTES.md` for the release description. Publish as the latest stable release.
6. Verify the uploaded ZIP opens with a `GameData/` directory and contains the six `.mu` models, six `.cfg` files and `RoosterWorksStationSupport.version`.
7. Comment on [NetKAN request #11672](https://github.com/KSP-CKAN/NetKAN/issues/11672) with the v1.0.1 release link: `https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/tag/v1.0.1`.

## Notes

- The existing `.netkan` handles both the old uppercase `V1.0.0` tag and lowercase `v1.0.1` via its version-normalization rule. No metadata change is required for this maintenance release.
- CKAN inclusion is subject to the maintainers' review; a submitted issue is not an approval.
- Keep documentation and developer source in the GitHub repository or an optional separate source archive, not at the top level of the player's install ZIP.
- This guide covers release packaging; it does not change part assets, capacity, models, attachment behavior or mass settings.
