# CKAN registration — RoosterWorks Station Support

**Mod identifier:** `RoosterWorksStationSupport`  
**Author:** SockedRooster · **License:** MIT · **KSP:** 1.12.5  
**Current published release:** [v1.0.1](https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/tag/v1.0.1)

## Status and outstanding action

The mod has a published, verified GitHub **v1.0.1** player release. The existing [CKAN request #11672](https://github.com/KSP-CKAN/NetKAN/issues/11672) originally requested v1.0.0; it should be updated rather than duplicated.

**The metadata has not yet been merged into the [KSP-CKAN/NetKAN](https://github.com/KSP-CKAN/NetKAN) index.** Keeping `CKAN/RoosterWorksStationSupport.netkan` in the mod's own repository is useful source material but does not register the mod or notify the indexing bot automatically.

## Submit the metadata

1. In the existing [request #11672](https://github.com/KSP-CKAN/NetKAN/issues/11672), comment with the [v1.0.1 release URL](https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/tag/v1.0.1) and its [player ZIP](https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/download/v1.0.1/RoosterWorks-Station-Support-v1.0.1.zip). No new issue is needed.
2. Follow the [official CKAN adding-a-mod guide](https://github.com/KSP-CKAN/CKAN/wiki/Adding-a-mod-to-the-CKAN). On the [NetKAN repository's `NetKAN/` directory](https://github.com/KSP-CKAN/NetKAN/tree/master/NetKAN), create `RoosterWorksStationSupport.netkan` containing the same metadata as [our maintained proposal](RoosterWorksStationSupport.netkan). GitHub can offer to fork the upstream repository when you lack write access.
3. Open a pull request to **`KSP-CKAN/NetKAN` `master`** and reference **#11672**. CKAN's validation checks will run on the pull request; fix any reported errors, then await maintainer review/merge.
4. Once accepted, verify the CKAN listing and that the game installs only `GameData/RoosterWorksStationSupport/`. CKAN registration and index refresh are not instantaneous.

Suggested comment for the original issue:

> The latest stable RoosterWorks Station Support release is now **v1.0.1**: https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/tag/v1.0.1 . Please index the **player archive** https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/download/v1.0.1/RoosterWorks-Station-Support-v1.0.1.zip rather than GitHub's source ZIP. Updated NetKAN source: https://github.com/SockedRooster/RoosterWorks-Station-Support/blob/main/CKAN/RoosterWorksStationSupport.netkan . The requested identifier remains `RoosterWorksStationSupport`, KSP compatibility is 1.12.5, and there are no required mod dependencies. This updates #11672 instead of creating a duplicate.

## Indexing details

- The metadata's GitHub `asset_match` rule selects only `RoosterWorks-Station-Support-vX.Y.Z.zip` release assets.
- `x_netkan_version_edit` handles the original uppercase `V1.0.0` tag and lowercase `v1.0.1`; the public version number becomes `1.0.1`.
- Releases use the package path `GameData/RoosterWorksStationSupport`; the installer copies the `RoosterWorksStationSupport` directory into `GameData`.
- No plugin dependencies. Kerbalism and VAB Organizer are optional. Pre-release assets are excluded.
- The actual v1.0.1 ZIP includes six KSP `.mu` models, six part `.cfg` files, eight model texture files, and the `.version` JSON (plus root README/LICENSE). Do not install source-build material.

**Do not tag or republish v1.0.1** to resolve CKAN indexing; the tested release ZIP is already available. CKAN indexing is a separate metadata contribution.
