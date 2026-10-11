# RoosterWorks Station Support v1.0.1 — Publishing Notes

This is a **local test candidate**, not a release. v1.0.0 is publicly available and CKAN indexing request [#11672](https://github.com/KSP-CKAN/NetKAN/issues/11672) is already open.

1. Install `RoosterWorks-Station-Support-v1.0.1-TEST.zip` into a copy of KSP 1.12.5 and run `TEST_CHECKLIST.md`.
2. Have the user confirm the heavier armor and new radial attachment are working as intended. In particular, check the visible Open Frame with an invisible exterior collider plane.
3. After approval, optionally publish v1.0.1 as a GitHub maintenance release using tag `v1.0.1` and **player ZIP asset named `RoosterWorks-Station-Support-v1.0.1.zip`**, without the `-TEST` suffix, to match the NetKAN asset-name regex. No automatic CKAN change needed if the existing NetKAN accepts vX.Y.Z assets.
4. Do not change live GitHub release or CKAN issue until tested.

The current test ZIP is intentionally named `-TEST.zip` and **does not match** the CKAN release-asset pattern, preventing unverified indexing.
