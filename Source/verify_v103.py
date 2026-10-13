"""Offline v1.0.3 regression checks; requires the v1.0.2 player ZIP."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import argparse, tempfile, zipfile, re, json, math
from read_mu import Reader
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'GameData/RoosterWorksStationSupport'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-zip',type=Path,required=True)
args=p.parse_args()

def parse(text):
    root={'values':{},'children':[]}; stack=[root]; pending=None
    for line in text.splitlines():
        line=line.split('//',1)[0].strip()
        if not line: continue
        if line=='{':
            assert pending
            node={'name':pending,'values':{},'children':[]}
            stack[-1]['children'].append(node); stack.append(node); pending=None
        elif line=='}':
            assert len(stack)>1
            stack.pop()
        elif '=' in line:
            k,v=map(str.strip,line.split('=',1)); assert k not in stack[-1]['values']
            stack[-1]['values'][k]=v
        else: assert pending is None; pending=line
    assert len(stack)==1 and pending is None
    return root['children'][0]

def children(node,name): return [n for n in node['children'] if n['name']==name]
def resources(node): return {r['values']['name']:r['values'] for r in children(node,'RESOURCE')}
def meshes(model): return {m['node']['name']:m for m in model.meshes}
def equal_mesh(a,b):
    for k in ('verts','uv','normals','tris','material'): assert a[k]==b[k], k

paths=list((GAME/'Parts').glob('*.cfg'))
assert len(paths)==15
assert len(list((GAME/'Models').glob('*.mu')))==10
expected={'RW_HexSupport_Long':(480,80),'RW_HexSupport_Medium':(240,40),
          'RW_OctoSupport_XL':(3600,600),'RW_OctoSupport_Medium':(1800,300),
          'RW_Octo375Support_XL':(12150,2025),'RW_Octo375Support_Medium':(6075,1013)}
with zipfile.ZipFile(args.baseline_zip) as baseline:
    for path in paths:
        part=parse(path.read_text(encoding='utf-8')); v=part['values']; pid=path.stem
        assert v['name']==pid
        model=children(part,'MODEL')[0]['values']['model'].split('/')[-1]
        assert (GAME/'Models'/f'{model}.mu').is_file()
        scale=Decimal(v['rescaleFactor'])
        large='375' in pid
        assert scale==Decimal('1.5' if large else '1')
        if pid in expected:
            res=resources(part)
            assert set(res)=={'ElectricCharge','MonoPropellant'}
            for key,capacity in zip(('ElectricCharge','MonoPropellant'),expected[pid]):
                assert res[key]['amount']==res[key]['maxAmount']==str(capacity)
        else: assert not resources(part)
        oldid=pid.replace('RW_Octo375Support','RW_OctoSupport').replace('RW_Octo375_Adapter','RW_Octo25_Adapter')
        old=parse(baseline.read(f'GameData/RoosterWorksStationSupport/Parts/{oldid}.cfg').decode('utf-8'))
        ratio=Decimal('3.375') if large else Decimal(1)
        for key in ('mass','cost','entryCost'):
            assert Decimal(v[key])==Decimal(old['values'][key])*ratio
        for key in ('node_stack_top','node_stack_bottom','node_attach'):
            vals=[Decimal(x.strip()) for x in v[key].split(',')]
            orig=[Decimal(x.strip()) for x in old['values'][key].split(',')]
            assert vals[:6]==orig[:6], 'Node double-scaled or moved'
            if key!='node_attach': assert vals[6]==(3 if large else orig[6])
        assert v['bulkheadProfiles']==('size3' if large else old['values']['bulkheadProfiles'])
        if 'Support' in pid:
            module=[m for m in children(part,'MODULE') if m['values'].get('name')=='ModulePartVariants'][0]
            assert module['values']['baseVariant']=='Open'
            variants={a['values']['name']:a for a in children(module,'VARIANT')}
            assert list(variants)==['Open','Armored','ArmoredGrey']
            oldmodule=[m for m in children(old,'MODULE') if m['values'].get('name')=='ModulePartVariants'][0]
            oldarmor=children(oldmodule,'VARIANT')[1]['values']
            for name,variant in variants.items():
                q=variant['values']; obj=children(variant,'GAMEOBJECTS')[0]['values']
                assert obj=={'ArmorPanels':'true' if name=='Armored' else 'false',
                             'ArmorPanelsGrey':'true' if name=='ArmoredGrey' else 'false'}
                assert Decimal(q['cost'])==(Decimal(0) if name=='Open' else Decimal(v['cost'])/10)
                assert Decimal(q['mass'])==(Decimal(0) if name=='Open' else Decimal(oldarmor['mass'])*ratio)
        else: assert not children(part,'MODULE')
        print(f'PASS {pid}: resources, scaling, nodes, pricing, finishes')
    for path in sorted((GAME/'Models').glob('*.mu')):
        current=Reader(path)
        old=Reader(baseline.read('GameData/RoosterWorksStationSupport/Models/'+path.name))
        mm,om=meshes(current),meshes(old)
        for name,mesh in om.items(): equal_mesh(mesh,mm[name])
        if 'Adapter' in path.name:
            assert set(mm)==set(om)
            assert path.read_bytes()==baseline.read('GameData/RoosterWorksStationSupport/Models/'+path.name)
        else:
            assert set(mm)-set(om)=={'GreyArmor_white_00','GreyArmor_bronze_00'}
            for name in ('white','bronze'):
                grey=mm[f'GreyArmor_{name}_00']; white=mm[f'Armor_{name}_00']
                for key in ('verts','normals','uv','tris'): assert grey[key]==white[key]
                assert grey['material']==(0 if name=='white' else white['material'])
            assert len([n for n in current.nodes if n['name']=='ArmorPanelsGrey'])==1
        def colliders(m): return [{k:n[k] for k in ('name','pos','rot','scale','size','center')} for n in m.nodes if 'size' in n]
        assert colliders(current)==colliders(old), 'Collision geometry changed'
        if '_Hollow' in path.name: assert all(n['name']!='EquipmentCollider' for n in current.nodes)
        for m in current.meshes:
            assert all(0<=i<len(m['verts']) for tri in m['tris'] for i in tri)
            assert all(math.isfinite(x) for vertex in m['verts'] for x in vertex)
        print(f'PASS {path.stem}: all previous mesh data and colliders identical; grey panels verified')
    for path in (GAME/'Models').glob('*.png'):
        assert path.read_bytes()==baseline.read('GameData/RoosterWorksStationSupport/Models/'+path.name)
assert json.loads((GAME/'RoosterWorksStationSupport.version').read_text())['VERSION']==dict(MAJOR=1,MINOR=0,PATCH=3,BUILD=0)
print('PASS v1.0.3: 15 parts, 10 shared models, all regression checks passed.')
print('NOT RUN: KSP editor, flight, saved-craft resource migration, or Kerbalism tests.')
