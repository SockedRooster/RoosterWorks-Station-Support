# CKAN Publishing Guide — RoosterWorks Station Support

**Mod:** RoosterWorks Station Support  
**Author:** SockedRooster  
**CKAN identifier:** `RoosterWorksStationSupport`  
**Declared KSP compatibility:** 1.12.5  
**License:** MIT

## CKAN registration

The existing indexing request is [KSP-CKAN/NetKAN #11672](https://github.com/KSP-CKAN/NetKAN/issues/11672). Do **not** open a duplicate for a maintenance release. When the new release is available, add its URL to the existing discussion.

`RoosterWorksStationSupport.netkan` targets the versioned GitHub release ZIP, installs only `RoosterWorksStationSupport` into `GameData`, and needs no additional plugin dependencies. It normalizes tags using either uppercase `V` or lowercase `v`.

## v1.0.1 release

1. Verify `main` contains the reviewed v1.0.1 gameplay assets, `RoosterWorksStationSupport.version` with PATCH=1, the SHA-256 manifest, and current README/changelog/release notes.
2. Check that `v1.0.1` does **not** point to an older commit; if absent, create it at the final v1.0.1 release commit. Preserve the existing `V1.0.0` release.
3. Run `python Source/verify_v101.py` and `sha256sum -c CHECKSUMS-SHA256.txt` to validate assets before packaging. If a local v1.0.0 ZIP is available, supply `--baseline-zip` for stronger binary regression checks.
4. Publish a GitHub release tagged **`v1.0.1`**, titled **RoosterWorks Station Support v1.0.1**, attaching **`RoosterWorks-Station-Support-v1.0.1.zip`**. The archive must contain `GameData/RoosterWorksStationSupport/` with six model files, six part configs, eight textures and the version JSON. A root README and LICENSE are fine.
5. Paste the committed `RELEASE_NOTES.md` as the release description and mark it as the latest stable release. Never offer the auto-generated GitHub source ZIP as the installer.
6. Comment on [NetKAN #11672](https://github.com/KSP-CKAN/NetKAN/issues/11672) with the [v1.0.1 release link](https://github.com/SockedRooster/RoosterWorks-Station-Support/releases/tag/v1.0.1) after publishing.

The GitHub Actions workflow `.github/workflows/publish-v1.0.1.yml` is a one-time release helper that verifies checksums, packages the exact GameData files and creates the tag/release if GitHub Actions and write access permit it. Publication must still be confirmed on GitHub; a workflow file in the repository is not itself a published release.

CKAN indexing is subject to review by CKAN maintainers. This release process does not modify gameplay assets.
