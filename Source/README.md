# RoosterWorks Station Support — developer source (v1.0.8)

The **player-installable files** live in `GameData/RoosterWorksStationSupport/` at the repository root. Do not copy `Source/`, `Tools/`, or `Previews/` into a KSP installation.

## Current development workflow

The active build/validation scripts are in `Tools/`:

```bash
python Tools/build_support_revamp.py
python Tools/validate_support_revamp.py
python Tools/package_support_revamp.py
```

Python dependencies used by the current build include NumPy and Pillow. Review the scripts before running them: rebuilding rewrites tracked `.mu` models and other assets, and should **not** be used to modify a tested release unintentionally. Use the tagged release ZIP for gameplay.

For an optional exact-model Blender preview:

```bash
blender --background --threads 2 --python Tools/render_support_revamp.py
```

The renderer produces its normal-map preview intermediates from the `GameData` DDS textures when it runs. Those generated copies do not need to be committed.

## Editable model sources

- `Blender/`: approved original and revised editable Blender projects and author-written builder scripts.
- `FiveFBXExports/`: approved intermediate FBX exports for the original family.
- `Conversion/`: earlier native `.mu` conversion pipeline, retained for historical reproducibility; **not** the current v1.0.8 rebuild command.
- `RevampBaseline/`: earlier gameplay models/configs used as regression baselines by `Tools/validate_support_revamp.py`. **Do not delete or replace with the current GameData:** the validator explicitly compares against them.
- `Textures/`: editable texture source/intermediates; gameplay textures are in root `GameData/`.
- `BatteryMaps/`: legacy battery placement maps and audit data.
- `SOURCE_NOTES_v*.md` and `SOURCE_NOTES.md`: versioned historical notes, not current installation instructions.

The current validator also uses `Reports/SUPPORT_REVAMP_01.json` and `Reports/ADAPTER_BASELINE_SHA256.json` in the repository root. Preserve these records during development.

## Historical tooling

Older `Source/verify_v*.py`, preview helpers and `Conversion/` scripts were created for earlier releases. They are retained as reference material and may have legacy version assumptions. Two one-time migration scripts that could rewrite current files to development-state content were removed from the active `Tools/` directory; both remain retrievable in Git history.

## Release compatibility

v1.0.8 includes 15 part IDs (six main girders, six legacy Hollow IDs and three adapters). The legacy Hollow IDs remain loadable for existing craft even though they are hidden from the part catalog. B9PartSwitch and ModuleManager are required and not bundled. In-game testing was reported as passed by the author; offline validation is not a substitute for re-testing modified game assets.

See the root `README.md`, `RELEASE_NOTES.md`, and `CKAN/PUBLISHING_GUIDE.md` for current installation and distribution details.
