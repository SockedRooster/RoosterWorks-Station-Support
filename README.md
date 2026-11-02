# RoosterWorks Station Support v1.0.8

**Stable release · SockedRooster · MIT · Kerbal Space Program 1.12.5**

A modular structural support part collection with frame/armor variants, selectable equipment interiors, integrated service wiring, and matching adapters in 1.25 m, 2.5 m, and 3.75 m families.

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for full release changes, dependencies and installation steps.

## Parts and selectors

- **6 main support girders**: Hex 1.25 m Medium/Long, Octo 2.5 m Medium/XL, and Octo 3.75 m Medium/XL.
- **6 legacy Hollow girder IDs**: retained for existing craft, but hidden from the editor; use Empty Frame or Central Service Core on the main girder instead.
- **3 stack adapters**: matching Hex, Octo 2.5 m and Octo 3.75 m connections.
- **Main girder Storage modes**: Standard EC + MonoPropellant; Battery Only; Empty Frame; Central Service Core; LF/Ox; Liquid Fuel; Oxidizer; Monopropellant; Xenon.
- **Main girder appearance modes**: Open Frame, Armored Panels, Armored Grey. Adapter appearance: White or Armored Grey.

| Main girder | Battery-only EC | LF / Ox | LF-only, Ox-only or Mono | XenonGas |
|---|---:|---:|---:|---:|
| Hex 1.25 m Medium | 2,000 | 54 / 66 | 120 | 1,100 |
| Hex 1.25 m Long | 4,000 | 108 / 132 | 240 | 2,100 |
| Octo 2.5 m Medium | 15,000 | 414 / 506 | 920 | 6,200 |
| Octo 2.5 m XL | 30,000 | 783 / 957 | 1,740 | 12,600 |
| Octo 3.75 m Medium | 33,000 | 1,395 / 1,705 | 3,100 | 20,900 |
| Octo 3.75 m XL | 66,000 | 2,655 / 3,245 | 5,900 | 42,700 |

Standard EC and MonoPropellant values retain the previous balancing; the battery-only values refer to Battery Only mode. Tank resource amounts are gameplay capacities, not physical pressure ratings. B9PartSwitch handles the equipment/capacity and appearance is controlled separately by ModulePartVariants.

## Install

Copy the release ZIP's `GameData/RoosterWorksStationSupport` folder into your KSP installation's `GameData` directory after removing an older copy. **B9PartSwitch and ModuleManager are required but not bundled.** Upgrading existing saved craft may require replacing parts in the editor to refresh serialized resources. The release targets KSP 1.12.5.

## Source and validation

The Developer-Source package contains the build toolchain under `Tools/`, original and derived resources under `Source/`, editable Blender scenes, previews, compatibility patches and the latest validation report.

To rebuild the geometry (Python with NumPy and Pillow):

```bash
python Tools/build_support_revamp.py
python Tools/validate_support_revamp.py
python Tools/package_support_revamp.py
```

Optional Blender preview: `blender --background --threads 2 --python Tools/render_support_revamp.py`. Geometry rebuilding can rewrite compiled `.mu` files; use the packaged player release if you just want to install the tested game files. The checker accepts legacy Windows-1252 punctuation in several original KSP display titles without rewriting those config files. `Source/RevampBaseline` and historical release notes are retained for comparison.

## License

MIT · SockedRooster. See [LICENSE](LICENSE).

[Repository](https://github.com/SockedRooster/RoosterWorks-Station-Support) · [Releases](https://github.com/SockedRooster/RoosterWorks-Station-Support/releases)
