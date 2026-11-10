"""Record accepted adapter hashes and document this integration release."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
old=R.parent/'RoosterWorks-Support-Load-Fix-02/GameData/RoosterWorksStationSupport'
hashes={p.relative_to(old).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder,pattern in [('Models','*Adapter.mu'),('Parts','*Adapter.cfg')] for p in (old/folder).glob(pattern)}
(R/'Reports/ADAPTER_BASELINE_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
report=json.loads((R/'Reports/SUPPORT_REVAMP_01.json').read_text())
rows=[]
for item in report['capacities']:
    if item['option']!='LFO':continue
    fuel=item['resources'];x=next(v['resources']['XenonGas'] for v in report['capacities'] if v['part']==item['part'] and v['option']=='Xenon')
    rows.append(f"| {item['part']} | {fuel['LiquidFuel']:g} / {fuel['Oxidizer']:g} | {sum(fuel.values()):g} | {x:g} |")
doc='''# Station Support v1.0.8-dev.3 — Integrated interiors

Each of the six main girder sizes now has one Storage selector with nine choices: Standard equipment, Battery Only, Empty Frame, Central Service Core, LF/Ox, Liquid Fuel, Oxidizer, Monopropellant and Xenon. Armor is still independent. The six original Hollow part IDs retain their original Interior selector for old craft, but are hidden from the editor catalog. All 15 legacy IDs and attachment nodes remain present. The three adapter configurations and two shared adapter models are unchanged from dev.2.

Battery drawer width/depth is increased, banks move outward, mounting ties connect the banks to their carriers, and the battery-only center bank is larger. Standard retains a larger central monopropellant vessel. Liquid tanks have larger diameters and less wasted axial space. Supports sit on the cylindrical restraint belts, continue to frame columns, and tie into the end rings. Xenon bottles are enlarged too. Bottom manifold supports now reach the surrounding frame.

Every occupied interior has matching end coupling collars and radial end supports, with blue/yellow harness branches meeting the external service lanes. Stacked service cores and tank or battery interiors now meet at the same central collar instead of ending with an exposed gap. These are service conduits, not crew passages. All switching remains editor-only.

## Capacity

New fuel capacities follow the enlarged modeled vessels. Existing Standard and Battery electrical/monopropellant capacities are retained for compatibility and balance; the battery enlargement is visual. Liquid volume uses 200 units per cubic metre with 85% usable volume; xenon uses the existing gameplay compression assumption. These are gameplay values, not certified physical tank ratings.

| Part | LF / Ox | LF-only, Ox-only or Mono | Xenon |
|---|---:|---:|---:|
'''+ '\n'.join(rows)+'''

## Install

Close KSP. Extract the Install ZIP into the Kerbal Space Program folder, merge GameData, and replace matching RoosterWorksStationSupport files. Keep B9PartSwitch and ModuleManager installed. Restart KSP fully. Use the main girder entries and their Storage selector for new builds; existing Hollow parts still load under their original IDs. No game or save files were modified during development.

## Validation and source

Offline checks cover all 15 IDs, 42 resource choices plus 12 new main-part empty/core choices, legacy hollow selectors, finite meshes, material/texture loader tables, integer entryCost, matching coupling collars and exterior service-lane endpoints, active interior colliders, resources, positive mass/cost, and unchanged adapter hashes. Three exact-MU Blender previews show tanks, batteries and a core/tank stack. Blender was limited to two CPU cores/threads at idle priority, 800 px and 16 samples; build/check/package workers use one core at idle priority. In-game acceptance of dev.3 remains pending.

Current previews: Previews/SupportIntegration03/Review.png. Packed editable review: Source/Blender/RW_SupportIntegration03.blend. Older preview folders and notes are historical.

Rebuild with Python plus NumPy/Pillow: Tools/build_support_revamp.py, then Tools/validate_support_revamp.py. Render with Blender --background --threads 2 --python Tools/render_support_revamp.py. Package with Tools/package_support_revamp.py. The supplied adapter hash manifest is the accepted baseline and should not be regenerated on rebuild. Tools/fix_load_02.py and Tools/document_integration_03.py are one-time historical migration/documentation utilities, not rebuild steps.
'''
(R/'SUPPORT_INTEGRATION_03.md').write_text(doc,encoding='utf-8')
readme=R/'README.md';text=readme.read_text();text=text.replace('v1.0.8-dev.2','v1.0.8-dev.3').replace('[SUPPORT_REVAMP_01.md](SUPPORT_REVAMP_01.md)','[SUPPORT_INTEGRATION_03.md](SUPPORT_INTEGRATION_03.md)').replace('Previews/SupportRevamp01/Review.png','Previews/SupportIntegration03/Review.png');readme.write_text(text)
notes=R/'RELEASE_NOTES.md';notes.write_text('# v1.0.8-dev.3\n\nIntegrated empty/core choices into the main selector; retained hidden legacy Hollow IDs. Enlarged tanks and battery banks, added frame-mounted restraints and common end transitions. Adapters unchanged. See SUPPORT_INTEGRATION_03.md.\n\n'+notes.read_text())
