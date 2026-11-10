"""Native mesh, variant, capacity, collision and matching-interface checks."""
from pathlib import Path
import sys,json,struct,hashlib
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'Tools'),str(R/'Source'),str(R/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
import numpy as np
from native_model import load,walk
from config_nodes import parse
from build_support_revamp import SPECS,SERVICE_LANES,CORE_WIRE_OFFSETS,OUTER_WIRE_OFFSETS,core_wire_point,harness_path
GD=R/'GameData/RoosterWorksStationSupport';BASE=R/'Source/RevampBaseline/GameData/RoosterWorksStationSupport';M=GD/'Models'
report=json.loads((R/'Reports/SUPPORT_REVAMP_01.json').read_text());stats=dict(models=0,parts=0,external_colliders=0,stock_appearance_options=0,storage_options=0,hollow_options=0,resource_definitions=0,interface_caps=0,max_mesh_vertices=0,visible_triangle_counts={})
models={}
for f in M.glob('*.mu'):
    model=load(f);old=load(BASE/'Models'/f.name);nodes=list(walk(model.root));models[f.stem]=model;name=f.stem.replace('_Hollow','');sides,diam,length,bays=SPECS[name]
    assert len(model.materials)==1+max(i for p,n in nodes for i in n.get('materials',[])),(f.name,'material table mismatch')
    assert len(model.textures)==1+max(v['index'] for m in model.materials for v in m['properties'].values() if isinstance(v,dict)),(f.name,'texture table mismatch')
    newco={n['name']:n for p,n in nodes if 'collider' in n and not n['name'].startswith('RWSS_')}
    for p,n in walk(old.root):
        if 'collider' in n and n['name']!='EquipmentCollider':assert n==newco[n['name']],(f.name,p,'external collision changed');stats['external_colliders']+=1
    for p,n in nodes:
        if 'mesh' not in n:continue
        m=n['mesh'];v=np.array(m['vertices']);tri=np.array([t for sub in m['submeshes'] for t in sub]);stats['max_mesh_vertices']=max(stats['max_mesh_vertices'],len(v))
        assert 0<len(v)<65535 and len(tri)>0;assert len(v)==len(m['normals'])==len(m['uvs'])
        assert all(np.isfinite(m[k]).all() for k in ('vertices','normals','uvs'));assert tri.min()>=0 and tri.max()<len(v)
        assert abs(v[:,1]).max()<=length/2+1e-5,(f.name,p,'extends through mating face',abs(v[:,1]).max(),length/2)
        area=np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1);assert area.min()>1e-12,(f.name,p,'zero-area triangle')
        assert np.allclose(np.linalg.norm(m['normals'],axis=1),1,atol=1e-4)
        for idx in n['materials']:
            mat=model.materials[idx];props=mat['properties']
            for key in ('_MainTex','_BumpMap'):
                if key in props:
                    texture=model.textures[props[key]['index']]['name'];assert any((M/(texture+ext)).exists() for ext in ('.png','.dds')),(f.name,texture)
            if '_BumpMap' in props:assert len(m['tangents'])==len(v) and np.isfinite(m['tangents']).all()
    # Actual cap rings of the two external blue/yellow lanes, at identical angular interfaces.
    s=diam/2.5
    for color,delta in (('steel',0),('blue',.065),('yellow',.092)):
        vertices=np.concatenate([n['mesh']['vertices'] for p,n in nodes if n['name'].startswith('RWSS_Frame_'+color)])
        for a in (np.pi*2/3,np.pi*4/3):
            for y in (-length/2,length/2):
                radius=(1.30 if color=='steel' else 1.272)*s
                c=np.array((radius*np.sin(a+delta),y,radius*np.cos(a+delta)));near=vertices[(abs(vertices[:,1]-y)<1e-6)&(np.linalg.norm(vertices-c,axis=1)<.02*s)]
                assert len(near)>12 and np.linalg.norm(near.mean(0)-c)<1e-5,(f.name,color,'unaligned cap');stats['interface_caps']+=1
    stats['models']+=1
definitions={}
for f in (GD/'Compatibility').glob('BatterySwitch*.cfg'):
    for tank in parse(f.read_text()).children:
        assert tank.header=='B9_TANK_TYPE';name=tank.get('name');assert name not in definitions;definitions[name]=tank
        assert all(float(r.get('unitsPerVolume'))>0 for r in tank.children if r.header=='RESOURCE')
stats['resource_definitions']=len(definitions)
for f in (GD/'Parts').glob('*.cfg'):
    part=parse(f.read_text()).children[0];old=parse((BASE/'Parts'/f.name).read_text(encoding='utf-8-sig')).children[0];modelname=next(n.get('model').split('/')[-1] for n in part.children if n.header=='MODEL');model=models[modelname];nodes=list(walk(model.root));names={n['name'] for p,n in nodes}
    for key,value in old.values:
        if key=='entryCost':assert part.get(key)==str(int(float(value)+.5)),(f.name,'invalid integer entryCost')
        elif key=='category' and f.stem.endswith('_Hollow'):assert part.get(key)=='none'
        elif key!='description':assert part.get(key)==value,(f.name,key,'unexpected config change')
    int(part.get('entryCost'))
    modules=[n for n in part.children if n.header=='MODULE'];stock=next(n for n in modules if n.get('name')=='ModulePartVariants')
    for variant in stock.children:
        if variant.header!='VARIANT':continue
        for objects in variant.children:
            if objects.header=='GAMEOBJECTS':
                for name,value in objects.values:assert name in names and value in ('true','false'),(f.name,name)
        stats['stock_appearance_options']+=1
    if 'Adapter' in f.name:stats['parts']+=1;continue
    switch=next(n for n in modules if n.get('name')=='ModuleB9PartSwitch');assert switch.get('switchInFlight')=='false'
    managed={v for st in switch.children for k,v in st.values if k=='transform'};assert managed<=names
    for subtype in switch.children:
        if subtype.header!='SUBTYPE':continue
        visible={v for k,v in subtype.values if k=='transform'};hidden=managed-visible
        active=[(p,n) for p,n in nodes if not any('/'+name+'/' in p or p.endswith('/'+name) for name in hidden) and '/ArmorPanels/' not in p and '/ArmorPanelsGrey/' not in p]
        assert float(part.get('mass'))+float(subtype.get('addedMass','0'))>0
        assert float(part.get('cost'))+float(subtype.get('addedCost','0'))>=0
        stats['visible_triangle_counts'][part.get('name')+'/'+subtype.get('name')]=sum(len(t) for p,n in active if 'mesh' in n for t in n['mesh']['submeshes'])
        if f.stem.endswith('_Hollow') or subtype.get('name') in ('Empty','ServiceCore'):
            assert not subtype.get('tankType');assert len(visible)==(1 if subtype.get('name')=='ServiceCore' else 0)
            corecolliders=[n for p,n in active if n['name']=='RWSS_CoreCollider'];assert len(corecolliders)==(1 if subtype.get('name')=='ServiceCore' else 0);stats['hollow_options']+=1
        else:
            volume=float(switch.get('baseVolume','0'))+float(subtype.get('volumeAdded','0'));assert volume>0
            tank=definitions[subtype.get('tankType')];resources={n.get('name'):float(n.get('unitsPerVolume'))*volume for n in tank.children if n.header=='RESOURCE'};assert resources
            if subtype.get('name')=='LFO':assert abs(resources['LiquidFuel']/resources['Oxidizer']-9/11)<1e-9
            if subtype.get('name') in ('Standard','Battery'):
                previous=parse((BASE/'Compatibility'/('BatterySwitch_'+part.get('name')+'.cfg')).read_text());legacy=next(n for n in previous.children if n.get('name')==subtype.get('tankType'));expected={n.get('name'):float(n.get('unitsPerVolume')) for n in legacy.children};assert resources==expected
            assert len(visible)==1 and len([n for p,n in active if 'collider' in n and n['name'] in ('EquipmentCollider','RWSS_PressureCollider')])==1
            stats['storage_options']+=1
    stats['parts']+=1
assert stats['models']==10 and stats['parts']==15 and stats['storage_options']==42 and stats['hollow_options']==24 and stats['resource_definitions']==42
adapter_hashes=json.loads((R/'Reports/ADAPTER_BASELINE_SHA256.json').read_text())
for path,digest in adapter_hashes.items():assert hashlib.sha256((GD/path).read_bytes()).hexdigest()==digest,(path,'accepted adapter changed')
for f in (GD/'Parts').glob('*.cfg'):
    part=parse(f.read_text()).children[0]
    if 'Adapter' in f.name:continue
    if f.stem.endswith('_Hollow'):
        assert part.get('category')=='none' and part.get('TechHidden')=='True'
    else:
        sw=next(n for n in part.children if n.get('moduleID')=='SupportStorage')
        assert {n.get('name') for n in sw.children}=={'Standard','Battery','Empty','ServiceCore','LFO','LF','Ox','Mono','Xenon'}
for key,model in models.items():
    if 'Adapter' in key:continue
    n,d,length,bays=SPECS[key.replace('_Hollow','')];s=d/2.5
    for parent in model.root['children']:
        if parent['name'] not in ('RWSS_Standard','RWSS_Battery','RWSS_TankPack','RWSS_XenonPack','RWSS_ServiceCore'):continue
        vertices=np.concatenate([node['mesh']['vertices'] for p,node in walk(parent) if 'mesh' in node])
        for sign in (-1,1):
            # Every occupied interior reaches the identical axial coupling collar.
            ring=vertices[(abs(vertices[:,1]-sign*length/2)<1e-6)&(abs(np.linalg.norm(vertices[:,[0,2]],axis=1)-.30*s)<1e-6)]
            assert len(ring)>=48,(key,parent['name'],'missing mating collar')
for file in M.glob('*NRM.dds'):
    data=file.read_bytes();assert data[:4]==b'DDS ' and struct.unpack_from('<I',data,28)[0]==11 and data[84:88]==b'DXT5'
stats['core_wiring_junctions']=0
for key,model in models.items():
    if 'Adapter' in key:continue
    n,d,length,bays=SPECS[key.replace('_Hollow','')];s=d/2.5
    nodes=list(walk(model.root))
    for color in CORE_WIRE_OFFSETS:
        vertices=np.concatenate([node['mesh']['vertices'] for p,node in nodes if node['name'].startswith('RWSS_ServiceCore_'+color)])
        for a in SERVICE_LANES:
            for sign in (-1,1):
                pts=harness_path(d,length,sign,a,color);start=np.array(pts[0]);end=np.array(pts[-1])
                # Branch begins on the trunk centerline; inspect the exported
                # branch cap and trunk cap vertices, not just path definitions.
                assert np.linalg.norm(start-np.array(core_wire_point(d,a,color,sign*(length/2-.19*s))))<1e-10
                assert sum(abs(np.linalg.norm(vertices-start,axis=1)-.007*s)<2e-6)>=12,(key,color,'branch cap missing')
                cap=np.array(core_wire_point(d,a,color,sign*length/2))
                assert sum((abs(vertices[:,1]-cap[1])<1e-6)&(abs(np.linalg.norm(vertices-cap,axis=1)-.010*s)<2e-6))>=12,(key,color,'trunk cap mismatch')
                expected=np.array([1.272*s*np.sin(a+OUTER_WIRE_OFFSETS[color]),sign*(length/2-.055*s),1.272*s*np.cos(a+OUTER_WIRE_OFFSETS[color])])
                assert np.linalg.norm(end-expected)<1e-10
                assert sum(abs(np.linalg.norm(vertices-end,axis=1)-.007*s)<2e-6)>=12,(key,color,'outer junction missing')
                other=harness_path(d,length,sign,a,'yellow' if color=='blue' else 'blue')
                assert min(np.linalg.norm(p-q) for p,q in zip(pts,other))>.014*s,'cables overlap'
                stats['core_wiring_junctions']+=1
report.update(status='PASS offline; KSP selector, visual and gameplay acceptance pending',validation=stats)
(R/'Reports/SUPPORT_REVAMP_01.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status']);print(json.dumps({k:v for k,v in stats.items() if k!='visible_triangle_counts'},indent=2))
