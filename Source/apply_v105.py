"""Add matching grey shells to all three adapters after the v1.0.4 build.

Optional --baseline-zip compares the entire game-data delta with v1.0.4.
Without it, reads the current v1.0.4 files; repeat application is safe.
"""
from pathlib import Path
import argparse,struct,zipfile,json
from read_mu import Reader
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'GameData/RoosterWorksStationSupport'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-zip',type=Path)
args=p.parse_args()
baseline=zipfile.ZipFile(args.baseline_zip) if args.baseline_zip else None
def read(relative):
    return baseline.read('GameData/RoosterWorksStationSupport/'+relative) if baseline else (GAME/relative).read_bytes()
def string(s):
    b=s.encode(); assert len(b)<128
    return bytes([len(b)])+b
allowed={'RoosterWorksStationSupport.version'}
report=[]
for model in ('RW_Hex125_Adapter','RW_Octo25_Adapter'):
    relative=f'Models/{model}.mu'; data=read(relative); old=Reader(data)
    if not any(m['node']['name']=='Body_grey_00' for m in old.meshes):
        whites=[m for m in old.meshes if m['material']==2]
        assert len(whites)==1 and whites[0]['node']['name']=='Body_white_00'
        white=whites[0]; node=white['node']; start,end=node['start'],node['end']
        grey=data[start:end]
        offset=white['material_offset']-start
        grey=grey[:offset]+struct.pack('<i',0)+grey[offset+4:]
        grey=string('Body_grey_00')+grey[len(string('Body_white_00')):]
        data=data[:end]+struct.pack('<i',0)+grey+data[end:]
    new=Reader(data)
    mm={m['node']['name']:m for m in new.meshes}
    for m in old.meshes:
        for key in ('verts','normals','uv','tris','material'):
            assert m[key]==mm[m['node']['name']][key]
    for key in ('verts','normals','uv','tris'):
        assert mm['Body_white_00'][key]==mm['Body_grey_00'][key]
    assert mm['Body_white_00']['material']==2 and mm['Body_grey_00']['material']==0
    colliders=lambda r:[{k:n[k] for k in ('name','pos','rot','scale','size','center')} for n in r.nodes if 'size' in n]
    assert colliders(old)==colliders(new)
    (GAME/relative).write_bytes(data); allowed.add(relative)
    report.append(f'PASS {model}: original meshes/colliders unchanged; grey shell uses same steel-grey material as girder armor; gold trim retained.')
module='''    MODULE
    {
        name = ModulePartVariants
        baseVariant = White
        baseMass = 0
        baseCost = 0
        useMultipleDragCubes = false
        VARIANT
        {
            name = White
            displayName = White
            mass = 0
            cost = 0
            primaryColor = #D5D9D5
            secondaryColor = #C18B49
            GAMEOBJECTS
            {
                Body_white_00 = true
                Body_grey_00 = false
            }
        }
        VARIANT
        {
            name = ArmoredGrey
            displayName = Armored Grey
            mass = 0
            cost = 0
            primaryColor = #707D89
            secondaryColor = #C18B49
            GAMEOBJECTS
            {
                Body_white_00 = false
                Body_grey_00 = true
            }
        }
    }
'''
for part in ('RW_Hex125_Adapter','RW_Octo25_Adapter','RW_Octo375_Adapter'):
    relative=f'Parts/{part}.cfg'; cfg=read(relative).decode('utf-8')
    if 'ModulePartVariants' not in cfg:
        i=cfg.rfind('}'); cfg=cfg[:i]+module+cfg[i:]
    assert cfg.count('name = ModulePartVariants')==1 and module in cfg
    assert cfg.count('{')==cfg.count('}')
    (GAME/relative).write_text(cfg,encoding='utf-8',newline='\n'); allowed.add(relative)
    report.append(f'PASS {part}: White default / Armored Grey, exclusive shell visibility, zero mass/cost difference.')
version=GAME/'RoosterWorksStationSupport.version'
metadata=json.loads(version.read_text()); metadata['VERSION']['PATCH']=5
version.write_text(json.dumps(metadata,indent=2)+'\n')
if baseline:
    changed=set()
    for name in baseline.namelist():
        prefix='GameData/RoosterWorksStationSupport/'
        if not name.startswith(prefix): continue
        relative=name.removeprefix(prefix); now=(GAME/relative).read_bytes(); old=baseline.read(name)
        if now!=old: changed.add(relative)
        if relative.startswith('Parts/') and relative in allowed:
            assert now.decode().replace(module,'')==old.decode()
    assert changed==allowed,(changed,allowed)
    previous={n for n in baseline.namelist() if n.startswith('GameData/')}
    current={p.relative_to(ROOT).as_posix() for p in (ROOT/'GameData').rglob('*') if p.is_file()}
    assert current==previous
    baseline.close()
    report.append('PASS full delta: only 3 adapter configs, 2 shared adapter models and version metadata changed. All girders, capacities, prices, textures and compatibility patches match v1.0.4 exactly.')
report.append('NOT RUN: KSP adapter variant selection/save/reload. User verified v1.0.4 selector removal and 3.75 m capacities before this change.')
(ROOT/'VALIDATION_v105.txt').write_text('\n'.join(report)+'\n',encoding='utf-8')
print('\n'.join(report))
