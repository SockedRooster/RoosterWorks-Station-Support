"""Verify final part configs and ship the complete girder expansion test."""
from pathlib import Path
import sys,zipfile,hashlib
R=Path(__file__).resolve().parent
base=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(base/'Tools'),str(base/'Source')]
from low_impact import limit_worker
limit_worker(1)
from config_nodes import parse
from native_model import load,walk
life=R.parent/'Kerbalism-Life-Support-Family'
addon=R/'GameData/RoosterWorksGirderExpansion'
host=base/'GameData/RoosterWorksStationSupport'
types={n.get('name'):n for n in parse((host/'Compatibility/BatterySwitch_RW_OctoSupport_Medium.cfg').read_text()).children}
parts=list((addon/'Parts').glob('*.cfg'))
assert len(parts)==6
rows=[]
for f in sorted(parts):
    part=parse(f.read_text(encoding='utf-8')).children[0]
    scale=float(part.get('rescaleFactor'))
    model=next(n.get('model') for n in part.children if n.header=='MODEL')
    nodes=list(walk(load(R/'GameData'/(model+'.mu')).root))
    names={n['name'] for _,n in nodes}
    stock=next(n for n in part.children if n.get('name')=='ModulePartVariants')
    assert {v.get('name') for v in stock.children}=={'Open','Armored','ArmoredGrey'}
    for variant in stock.children:
        vis={k:v for child in variant.children if child.header=='GAMEOBJECTS' for k,v in child.values}
        assert set(vis)=={'ArmorPanels','ArmorPanelsGrey'} and set(vis)<=names
        assert sum(value=='true' for value in vis.values())==(0 if variant.get('name')=='Open' else 1)
    ports=[tuple(float(v) for v in value.split(',')) for k,value in part.values if k.startswith('node_stack_')]
    if 'Hub' not in f.stem:
        assert len(ports)==2 and sorted(int(p[6]) for p in ports)==sorted(int(v)//125 for v in f.stem.split('_')[-2:])
        continue
    assert len(ports)==6 and len({p[3:6] for p in ports})==6
    assert all(int(p[6])==round(2*scale) for p in ports)
    switch=next(n for n in part.children if n.get('moduleID')=='HubStorage')
    assert {n.get('name') for n in switch.children}=={'Empty','Standard','Battery','LFO','LF','Ox','Mono','Xenon'}
    capacities={}
    for subtype in switch.children:
        key=subtype.get('name')
        if key=='Empty':assert subtype.get('defaultSubtypePriority')=='1';continue
        assert subtype.get('transform') in names
        group=next(n for p,n in nodes if n['name']==subtype.get('transform'))
        assert any('collider' in n for p,n in walk(group))
        tank=types[subtype.get('tankType')]
        capacities[key]={n.get('name'):float(n.get('unitsPerVolume'))*float(switch.get('baseVolume')) for n in tank.children}
    assert capacities['LFO']['LiquidFuel']/capacities['LFO']['Oxidizer']==9/11
    rows.append(f"| {2.5*scale:g} m | {capacities['Battery']['ElectricCharge']:g} | {capacities['LFO']['LiquidFuel']:g} / {capacities['LFO']['Oxidizer']:g} | {capacities['Xenon']['XenonGas']:g} |")
readme='''# Girder Expansion • KSP 1.12.5 test build

Requires RoosterWorks Station Support v1.0.9, ModuleManager and B9PartSwitch. Close KSP, extract the install ZIP into the KSP root and restart. If upgrading the optional XL-only Kerbalism test, replace its GameData/RoosterWorksKerbalismSupport folder with the one here. Both new addon folders belong beside RoosterWorksStationSupport.

Find the three **Girder Adapters** and three **Six-Way Girder Hubs** in Structural. The reducers join 1.25–2.5 m, 2.5–3.75 m and 1.25–3.75 m girders. Each has the larger stack node at the bottom. Open Frame, Armored Panels and Armored Grey are stock appearance choices. Blue and yellow conduits and the handrail reach the port planes at the girder clocks. Rotating an attached girder changes its cable clock.

Each hub has six equal-size stack ports. The 1.25 m rims are hexagonal; 2.5 m and 3.75 m rims are octagonal. Select Storage separately from the armor. Empty is the default. Choose EC + MonoPropellant, Battery Only, LF/Ox, LF, Oxidizer, Monopropellant or Xenon. External wires terminate in sockets around the hub port rims. Stored equipment has a switchable collider and the open frame has beam colliders.

| Hub | Battery Only (EC) | LF / Ox | Xenon |
|---|---:|---:|---:|
'''+ '\n'.join(rows)+'''

Capacities scale by hub volume. The 2.5 m hub uses half of the 2.5 m Medium girder storage as a gameplay balance choice.

The included optional Kerbalism add-on adds Life Support to all six main straight girders when Kerbalism Default and Community Resource Pack are present. It carries four oxygen bottles, four nitrogen bottles, a Food drum and a Water drum. See LIFE_SUPPORT.md for capacities.

Offline checks cover six new part IDs, port sizes, switch transforms, geometry, wiring endpoint positions, hub resource references and archive integrity. Live KSP checks still needed: attach each size in the VAB, switch armor and storage, and reload the assembled craft. Test package built separately from the prepared Station Support release.
'''
(R/'README.md').write_text(readme,encoding='utf-8')
runtime=[(f,f.relative_to(root).as_posix()) for root in (R,life) for f in sorted((root/'GameData').rglob('*')) if f.is_file()]
runtime.extend([(R/'README.md','README.md'),(life/'README.md','LIFE_SUPPORT.md')])
for kind in ('Install','Developer-Source'):
    files=list(runtime)
    if kind=='Developer-Source':
        files=[(p,p.relative_to(R.parent).as_posix()) for p,_ in runtime]
        files += [(p,p.relative_to(R.parent).as_posix()) for p in (R/'build_structure.py',R/'preview.py',R/'package.py',R/'Girder-Expansion.png',life/'build.py',life/'payload.py')]
    target=R/f'RoosterWorks-Girder-Expansion-v0.1.0-test.1-{kind}.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p,name in files:z.write(p,name)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None and len(set(z.namelist()))==len(files)
        for p,name in files:assert hashlib.sha256(z.read(name)).digest()==hashlib.sha256(p.read_bytes()).digest()
    print(target.name,'verified')
print(*rows,sep='\n')
