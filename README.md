# RoosterWorks Station Support v1.0.1

**Author:** SockedRooster · **License:** MIT · **KSP:** 1.12.5  
**Repository:** https://github.com/SockedRooster/RoosterWorks-Station-Support

RoosterWorks Station Support adds six custom orbital station components: four structural girders with built-in ElectricCharge and MonoPropellant storage, plus two stack adapters. The girders can switch between **Open Frame** and **Armored Panels** using stock KSP part variants. No additional plugin is required. Designed with Kerbalism use in mind, but Kerbalism is not required.

## Changes in v1.0.1

- **Armored variants now weigh 25% more (dry mass)** than the corresponding Open Frame girders. Armoring does not change their resource capacities.
- **All six parts support improved radial attachment:** outer polygon-face attachment nodes and added invisible perimeter collision surfaces help other parts attach to the exterior rather than snap toward internal tanks and batteries.
- All six approved visible models, textures, names, stack attachment positions, fuel/charge capacities, part IDs and costs are unchanged from v1.0.0.

### Part capacities and mass

| Part | Diameter × height | ElectricCharge | MonoPropellant | Open dry mass | Armored dry mass |
|---|---|---:|---:|---:|---:|
| Octo XL Girder | 2.5 m × 4.75 m | 9,000 | 1,500 | 3.200 t | 4.000 t |
| Octo Medium Girder | 2.5 m × 2.65 m | 4,500 | 750 | 1.850 t | 2.3125 t |
| Hex Long Girder | 1.25 m × 3.15 m | 1,200 | 200 | 0.760 t | 0.950 t |
| Hex Medium Girder | 1.25 m × 1.75 m | 600 | 100 | 0.420 t | 0.525 t |
| Octo → 2.5 m Adapter | 2.5 m × 0.74 m | — | — | 0.280 t | — |
| Hex → 1.25 m Adapter | 1.25 m × 0.56 m | — | — | 0.140 t | — |

Stock KSP MonoPropellant mass is 0.004 t per unit. Masses above are **dry** mass, not fueled mass. The two adapters have no armor variant.

## Installation and updating

1. Close KSP and back up saves/craft files.
2. Remove the older `GameData/RoosterWorksStationSupport` folder to prevent mixed-version files. If an earlier prototype `GameData/RoosterWorksKerbalismAdditions` still exists, remove it to avoid duplicate part IDs.
3. Extract **`RoosterWorks-Station-Support-v1.0.1.zip`** into the **KSP installation root**; it creates `GameData/RoosterWorksStationSupport/`.
4. In the VAB, look for the six parts under **Structural**. Existing attachment nodes and part names are preserved.

## Notes and limitations

- The new perimeter collision surfaces are present in **both** Open Frame and Armored Panels modes. The gaps between visible open truss rails can therefore behave like solid side faces for attachment/physics.
- Armor currently changes visible plating and part dry mass; no additional impact-resistance or shielding mechanics are claimed.
- Green battery LEDs are static; KSP materials are simplified; high-detail models may cost performance on very large stations.
- Resources use ordinary persistent stock `RESOURCE` definitions. Exhaustive Kerbalism background simulation testing is not claimed.

### Verification

The author confirmed that the v1.0.1 gameplay tests passed, including the variant mass and radial attachment checks. Automated package checks were also run on the final release archive; these do not replace every possible gameplay compatibility test.

## License and source

MIT. Original RoosterWorks assets; no Near Future Construction files are distributed. Blender sources and model conversion scripts are provided separately in the GitHub source archive.
