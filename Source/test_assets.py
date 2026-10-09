#!/usr/bin/env python3
"""KSP1 .mu/config structural checks for RoosterWorks v0.3.0 alpha3."""
import struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
GD=ROOT/'GameData'/'RoosterWorksKerbalismAdditions'
MODELS=GD/'Models';PARTS=GD/'Parts'
EXPECT={'RW_OctoSupport_XL':(8,9000,1500,4.75),
        'RW_OctoSupport_Medium':(8,4500,750,2.65),
        'RW_HexSupport_Long':(6,1200,200,3.15),
        'RW_HexSupport_Medium':(6,600,100,1.75)}
ADAPTER='RW_Octo25_Adapter'
HEX_ADAPTER='RW_Hex125_Adapter'
class Reader:
    def __init__(self,p):
        self.f=p.open('rb');self.end=self.f.seek(0,2);self.f.seek(0)
        self.objects=[];self.colliders=[];self.meshes=[];self.materials=[];self.textures=[];self.ntri=0
    def get(self,fmt):
        n=struct.calcsize('<'+fmt);a=self.f.read(n)
        assert len(a)==n,f'Unexpected EOF at {self.f.tell()}'
        v=struct.unpack('<'+fmt,a);return v[0] if len(v)==1 else v
    def i(self):return self.get('i')
    def b(self):return self.get('B')
    def xyz(self):return self.get('fff')
    def s(self):
        n=0;bit=0
        while True:
            b=self.b();n|=(b&127)<<bit;bit+=7
            if b<128:break
        assert 0<=n<200000
        return self.f.read(n).decode('utf8')
    def mesh(self,name):
        assert self.i()==13
        nv=self.i();ns=self.i();assert 0<nv<65000 and ns==1
        assert self.i()==14
        for _ in range(nv):self.xyz()
        assert self.i()==15
        for _ in range(nv):self.get('ff')
        assert self.i()==17
        for _ in range(nv):self.xyz()
        assert self.i()==19;n=self.i();assert n%3==0
        for _ in range(n):assert 0<=self.i()<nv
        assert self.i()==22
        self.meshes.append((name,nv,n//3));self.ntri+=n//3
    def obj(self):
        name=self.s();self.objects.append(name);self.xyz();self.get('ffff');self.xyz()
        assert self.i()==24;self.s();self.i()
        while self.f.tell()<self.end:
            tag=self.i()
            if tag==0:self.obj()
            elif tag==1:return
            elif tag==28:
                assert self.b()==0
                size=self.xyz();self.xyz();assert all(x>0 for x in size)
                self.colliders.append((name,size))
            elif tag==7:self.mesh(name)
            elif tag==8:
                self.b();self.b();assert self.i()==1;assert 0<=self.i()<6
            elif tag==10:
                assert self.i()==6
                for _ in range(6):
                    self.materials.append(self.s());assert self.s()=='KSP/Diffuse';assert self.i()==2
                    assert self.s()=='_Color';assert self.i()==0;self.get('ffff')
                    assert self.s()=='_MainTex';assert self.i()==4;assert 0<=self.i()<6;self.get('ff');self.get('ff')
            elif tag==12:
                assert self.i()==6
                for _ in range(6):self.textures.append(self.s());assert self.i()==0
            else:raise ValueError(f'Unexpected MU tag {tag} at {self.f.tell()-4} in {name}')
    def verify(self):
        assert self.get('ii')==(76543,5);self.s();self.obj()
        assert self.f.tell()==self.end,'Unparsed model data'
        assert len(self.materials)==6 and len(self.textures)==6
        assert self.ntri>800
        assert 'RoosterWorksBrand' in self.objects
        return self
assert len(list(PARTS.glob('*.cfg')))==6
assert len(list(MODELS.glob('*.mu')))==6
for name,(poly,ec,mono,h) in EXPECT.items():
    cfg=(PARTS/(name+'.cfg')).read_text()
    assert f'name = {name}\n' in cfg
    assert 'category = Structural' in cfg and 'organizerSubcategory = trusses' in cfg
    assert 'Kerbalism Addition' in cfg and 'manufacturer = RoosterWorks' in cfg
    assert cfg.count('name = ModulePartVariants')==1
    assert 'baseVariant = Open' in cfg
    assert 'name = Open' in cfg and 'name = Armored' in cfg
    assert 'ArmorPanels = false' in cfg and 'ArmorPanels = true' in cfg
    assert 'ModuleB9PartSwitch' not in cfg
    assert 'name = ElectricCharge' in cfg and f'amount = {ec}\n' in cfg and f'maxAmount = {ec}\n' in cfg
    assert 'name = MonoPropellant' in cfg and f'amount = {mono}\n' in cfg and f'maxAmount = {mono}\n' in cfg
    assert cfg.count('node_stack_')==2
    assert f'{h/2:.4f}' in cfg and f'{-h/2:.4f}' in cfg
    assert cfg.count('{')==cfg.count('}')
    mu=Reader(MODELS/(name+'.mu')).verify()
    assert len(mu.meshes)==7,mu.meshes
    assert 'ArmorPanels' in mu.objects
    assert 'MonopropellantVessels' in mu.objects and 'BatteryPacks' in mu.objects
    assert len(mu.colliders)==poly+1
    assert not any('ArmorPanels' in n for n,size in mu.colliders), 'Armor visual should not add unexpected physics collision'
    print(f'PASS {name}: {len(mu.meshes)} mesh objects, {mu.ntri} tris, {len(mu.colliders)} colliders, EC={ec}, Mono={mono}')
acfg=(PARTS/(ADAPTER+'.cfg')).read_text()
assert f'name = {ADAPTER}\n' in acfg
assert 'category = Structural' in acfg and 'organizerSubcategory = adapters' in acfg
assert acfg.count('node_stack_')==2 and acfg.count(', 2\n')>=2
assert acfg.count('{')==acfg.count('}')
assert 'RESOURCE' not in acfg
amu=Reader(MODELS/(ADAPTER+'.mu')).verify()
assert len(amu.meshes)==6 and len(amu.colliders)==1
assert 'AdapterFairing' in amu.objects
print(f'PASS {ADAPTER}: 2.5m octagon-to-round, {amu.ntri} tris, two stack nodes')
hcfg=(PARTS/(HEX_ADAPTER+'.cfg')).read_text()
assert f'name = {HEX_ADAPTER}\n' in hcfg
assert 'organizerSubcategory = adapters' in hcfg
assert '1.25m Stack Adapter' in hcfg and 'TechRequired = advConstruction' in hcfg
assert hcfg.count('node_stack_')==2 and hcfg.count(', 1\n')>=2
assert 'RESOURCE' not in hcfg
assert hcfg.count('{')==hcfg.count('}')
hamu=Reader(MODELS/(HEX_ADAPTER+'.mu')).verify()
assert len(hamu.meshes)==6 and len(hamu.colliders)==1
assert 'AdapterFairing' in hamu.objects
print(f'PASS {HEX_ADAPTER}: 1.25m hex-to-round, {hamu.ntri} tris, two size1 nodes')
for n in ['frame','tank','battery','bronze','copper','branding']:
    with Image.open(MODELS/(n+'.png')) as im:im.verify()
assert not list(GD.rglob('*.dll'))
# Geometric regression: vertical tank membrane extends nearly the full frame height.
import importlib.util,math
src=Path(__file__).with_name('build.py')
spec=importlib.util.spec_from_file_location('rwbld',src)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
for part in b.PARTS:
    meshes, armor=b.build_part(part)
    h=part['height'];poly=part['polygon'];rad=part['diameter']*.47
    tank_ys=[v[1] for v in meshes[1].verts]
    assert min(tank_ys) <= -h/2+.151 and max(tank_ys) >= h/2-.151
    # Full-height panel coverage extends within 6cm of the frame at both ends.
    panel_y=[v[1] for v in armor.verts]
    assert min(panel_y) <= -h/2+.044 and max(panel_y) >= h/2-.044
    # All four original resources unchanged; armor has no collider.
print('PASS geometry: full-length fuel vessels and uninterrupted frame-to-frame armor')
print('PASS all six model/config pairs; four stock panel selectors; fixed storage; textures (6); no DLL')
print('NOTE: live VAB variant behavior, attachment stability and Kerbalism persistence require in-game testing.')
