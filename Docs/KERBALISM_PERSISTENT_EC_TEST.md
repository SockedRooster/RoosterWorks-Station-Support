# Kerbalism persistent-power test (in-place, unreleased)

This patch is an experimental attempt to address Station Support battery charge depletion on **unloaded** craft running Kerbalism. The goal is for all **six existing part IDs** to work normally—no extra parts, no new editor controls, no save-breaking renames.

File: `GameData/RoosterWorksStationSupport/Compatibility/KerbalismPersistentEC.cfg`.

The patch adds a stock ElectricCharge resource to each original part prefab when Kerbalism and B9PartSwitch are installed. The existing B9PartSwitch Storage selector remains authoritative for the nine configurations, including **Standard (EC + MonoPropellant)** and **Battery Only**. Fuel and empty variants remain selectable. This is deliberately different from the old Near Future Construction approach that locked cloned parts into a single mode.

| Existing part | Standard EC | Standard MP | Battery EC |
|---|---:|---:|---:|
| `RW_HexSupport_Medium` | 240 | 40 | 2000 |
| `RW_HexSupport_Long` | 480 | 80 | 4000 |
| `RW_OctoSupport_Medium` | 1800 | 300 | 15000 |
| `RW_OctoSupport_XL` | 3600 | 600 | 30000 |
| `RW_Octo375Support_Medium` | 3949 | 658 | 33000 |
| `RW_Octo375Support_XL` | 7898 | 1316 | 66000 |

**Not verified in-game.** B9 still adjusts EC dynamically; seeding a prefab resource may or may not be sufficient to resolve Kerbalism's unloaded EC behavior. This is a development test, not a confirmed permanent fix.

## In-game acceptance test

1. Back up your save and install the patch at the original path above; remove any separately installed duplicate patch. Fully restart KSP.
2. In the VAB, verify **no new parts** and the same nine modes. Check Standard and Battery capacities. Verify LFO/Empty/Xenon modes have no unexpected EC resource.
3. Make a sunlit station with a new original girder using Standard mode and sufficient solar generation. Record initial EC, net generation and consumption in Kerbalism's monitor.
4. Switch to another craft, advance time with the station in sunlight, and compare the unloaded-vessel Kerbalism monitor before returning. It must not unexpectedly reset or lose EC when generation exceeds consumption.
5. Repeat with Battery Only and then with an existing saved vessel. Save/reload and verify stable capacity and charge across both switches.
6. If depleted, check KSP.log, ModuleManager.ConfigCache and whether unloaded solar generation exceeded electrical consumption. Do not mark the fix as validated.

Do not publish a v1.0.9 stable release until both modes pass. Published v1.0.8 is unchanged.
