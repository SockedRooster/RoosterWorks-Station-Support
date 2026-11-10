"""Build, check, and package the Kerbalism interiors for the six stocked girders."""
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import hashlib
import shutil
import zipfile
from payload import BASE, GD, M, HERE, ADDON, make_payload, load, walk, np
from config_nodes import Node, parse, dump
from build_support_revamp import SPECS

ROOT = BASE/'GameData/RoosterWorksStationSupport'
REFERENCE = {'Oxygen':231200, 'Nitrogen':208080, 'Food':3270, 'Water':3270}
NEEDS = ':NEEDS[RoosterWorksStationSupport,Kerbalism,ProfileDefault,CommunityResourcePack,B9PartSwitch]'
SUBTYPE = 'RWSS_KerbalismLifeSupport'
rows = []
patches = []
models = {}

def read_part(path):
    return parse(path.read_bytes().decode('cp1252')).children[0]

def checked_model(name, diameter, length):
    make_payload(diameter, length, name)
    model = load(M/(name+'.mu'))
    nodes = [n for _,n in walk(model.root)]
    names = {n['name'] for n in nodes}
    assert {'KLS_Food','KLS_Water','RWSS_KLS_Payload'} <= names
    assert all(f'KLS_{gas}_{i}' in names for gas in ('Oxygen','Nitrogen') for i in range(1,5))
    assert sum('collider' in n for n in nodes)==10
    for n in nodes:
        if 'mesh' not in n:continue
        m=n['mesh'];v=np.asarray(m['vertices'])
        assert np.isfinite(v).all() and len(v)<65535
        assert abs(v[:,1]).max()<=length/2+1e-6
        assert np.allclose(np.linalg.norm(m['normals'],axis=1),1,atol=1e-5)
        for sub in m['submeshes']:
            tri=np.asarray(sub)
            assert tri.min()>=0 and tri.max()<len(v)
            assert np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1).min()>1e-12
    for tex in model.textures:assert (M/(tex['name']+('.dds' if tex['type']==1 else '.png'))).exists()

def number(value):
    return format(value.quantize(D('.000000001')).normalize(),'f')

for path in sorted((ROOT/'Parts').glob('*.cfg')):
    part=read_part(path)
    switches=[n for n in part.children if n.header=='MODULE' and n.get('moduleID')=='SupportStorage']
    if not switches:continue
    switch=switches[0]
    assert switch.get('baseVolume')=='1' and SUBTYPE not in [n.get('name') for n in switch.children]
    part_id=part.get('name')
    frame=next(n.get('model').split('/')[-1] for n in part.children if n.header=='MODEL')
    _,diameter,length,_=SPECS[frame]
    model_name='RWSS_KLS_XL' if frame=='RW_OctoSupport_XL' else 'RWSS_KLS_'+frame.removeprefix('RW_')
    if frame not in models:
        checked_model(model_name,diameter,length)
        models[frame]=model_name
    # KSP applies the part's rescaleFactor to both MODEL nodes.
    scale=D(part.get('rescaleFactor','1'))
    ratio=(D(str(diameter))*scale/D('2.5'))**2*(D(str(length))*scale/D('4.75'))
    amounts={key:int((D(amount)*ratio).quantize(D(1),rounding=ROUND_HALF_UP)) for key,amount in REFERENCE.items()}
    tank_name='RWSS_KLS_XL_Loadout' if part_id=='RW_OctoSupport_XL' else 'RWSS_KLS_'+part_id+'_Loadout'
    tank=Node('B9_TANK_TYPE'+NEEDS,[('name',tank_name),('tankMass',number(D(8852)*D('.000106275')*ratio)),('tankCost',number(D(8852)*D('.15')*ratio))])
    tank.children=[Node('RESOURCE',[('name',r),('unitsPerVolume',str(q)),('percentFilled','100')]) for r,q in amounts.items()]
    hollow=read_part(path.with_name(part_id+'_Hollow.cfg'))
    dry_delta=D(hollow.get('mass'))+D('.54')*ratio-D(part.get('mass'))
    cost_delta=D(hollow.get('cost'))+D(12000)*ratio-D(part.get('cost'))
    subtype=Node('SUBTYPE',[('name',SUBTYPE),('title','Kerbalism Life Support'),('primaryColor','#759188'),('secondaryColor','#486d89'),('tankType',tank_name),('transform','RWSS_KLS_Payload'),('addedMass',number(dry_delta)),('addedCost',number(cost_delta))])
    patch=Node('@PART['+part_id+']:HAS[@MODULE[ModuleB9PartSwitch]:HAS[#moduleID[SupportStorage],#baseVolume[1],@SUBTYPE[ServiceCore]]]'+NEEDS)
    patch.children=[Node('MODEL',[('model',ADDON+'/Models/'+model_name)]),Node('@MODULE[ModuleB9PartSwitch]:HAS[#moduleID[SupportStorage]]',children=[subtype])]
    patches.extend([tank,patch])
    rows.append((part_id,number(D(str(diameter))*scale),*amounts.values()))

assert len(models)==4 and len(rows)==6 and len({p.get('name') for p in patches if p.header.startswith('B9_TANK_TYPE')})==6
assert next(row[2:] for row in rows if row[0]=='RW_OctoSupport_XL')==tuple(REFERENCE.values())
config=dump(Node('ROOT',children=patches))
assert len(parse(config).children)==12 and config.count(NEEDS)==12
(GD/'LifeSupport.cfg').write_text(config,encoding='utf-8')
shutil.copyfile(BASE/'LICENSE',GD/'LICENSE')
table='| Girder ID | Diameter (m) | Oxygen | Nitrogen | Food | Water |\n|---|---:|---:|---:|---:|---:|\n'
table+=''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
readme='''# RoosterWorks Kerbalism Life Support • six-girder test build

Extract the Install ZIP into the KSP root. If you have the XL-only test, replace its GameData/RoosterWorksKerbalismSupport folder with this one. Requires Station Support v1.0.9, ModuleManager, B9PartSwitch, Community Resource Pack, and Kerbalism using its Default profile.

Select a main girder in the VAB, then choose **Storage → Kerbalism Life Support**. Open Frame shows four Oxygen bottles, four Nitrogen bottles, one Food drum and one Water drum. Switching Storage moves the entire interior and its colliders with the resource choice. The existing XL subtype name and tank ID are preserved for craft built with the first test.

The 2.5 m XL holds the equivalent of eight installed Kerbalism Big tanks and two dedicated 2.5 m supply containers. Each other size scales from that reference by diameter squared times girder length, rounded to the nearest whole resource unit. The bottles and drums scale to the available height and width. Equipment supports meet the hexagonal or octagonal frame. The 3.75 m parts use the same 1.5× model scale as their host girders. Equipment mass and cost scale with capacity above the size-specific empty frame.

'''+table+'''
The build checks model bounds, triangles, unit normals, materials, all six selector patches, ten equipment colliders per layout, and the XL reference capacities. Editor switching, vessel reload and Kerbalism consumption still require live KSP testing.

To rebuild from source, run python build.py with the path to the Station Support v1.0.9 developer source folder. Requires NumPy, Pillow and the Windows Bahnschrift font.
'''
(HERE/'README.md').write_text(readme,encoding='utf-8')
for suffix in ('Install','Developer-Source'):
    files=sorted(p for p in GD.rglob('*') if p.is_file())+[HERE/'README.md']
    if suffix=='Developer-Source':files += [HERE/'build.py',HERE/'payload.py']
    target=HERE/f'RoosterWorks-Kerbalism-Life-Support-v0.2.0-test.1-{suffix}.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p in files:z.write(p,p.relative_to(HERE).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for p in files:assert hashlib.sha256(z.read(p.relative_to(HERE).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
    print(target.name,'verified')
print(table)
