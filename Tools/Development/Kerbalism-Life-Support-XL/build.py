"""Build the optional Octo XL payload using the Station Support v1.0.9 sources."""
from pathlib import Path
import sys, math, shutil, copy, json, zipfile, hashlib
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
DEFAULT = HERE.parent / 'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT
sys.path[:0] = [str(BASE/'Tools'), str(BASE/'Source'), str(BASE/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
from build_support_revamp import Batch, group, node, h, tube, plate, beam, bolt, lathe, vessel, terminal_interface, frame_radius, np, write, load, walk
from PIL import Image, ImageDraw, ImageFont

ADDON = 'RoosterWorksKerbalismSupport'
GD = HERE/'GameData'/ADDON
M = GD/'Models'
M.mkdir(parents=True, exist_ok=True)
ORIGINAL = BASE/'GameData/RoosterWorksStationSupport/Models'
source = load(ORIGINAL/'RW_OctoSupport_XL.mu')
model = SimpleNamespace(name='RWSS_KLS_XL', root=node('RWSS_KLS_Model'),
                        materials=copy.deepcopy(source.materials), textures=copy.deepcopy(source.textures))
payload = node('RWSS_KLS_Payload')
model.root['children'].append(payload)
def mount(name, batch, collider_center=None, collider_size=None):
    from support_art import emit
    part = node(name)
    payload['children'].append(part)
    emit(model, part, name, batch)
    if collider_size:
        collision = node(name+'_Collider')
        collision['collider'] = dict(type='box',trigger=0,center=tuple(collider_center),size=collider_size)
        part['children'].append(collision)

atlas = Image.new('RGB',(1024,1024))
draw = ImageDraw.Draw(atlas)
font = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',104)
small = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',32)
for i,(label,accent) in enumerate([('OXYGEN','#6daed0'),('NITROGEN','#bdac74'),('FOOD','#a5b47a'),('WATER','#86bbcf')]):
    y=i*256
    draw.rectangle((0,y,1023,y+255),fill='#2e373b')
    draw.rectangle((12,y+12,1011,y+243),outline=accent,width=8)
    draw.text((54,y+18),'RW   /   STATION CONSUMABLES',font=small,fill=accent)
    draw.text((50,y+72),label,font=font,fill='#ecece1')
atlas.save(M/'rwkls_markings.png')

# Two banks, four pressure vessels around the central manifold per bank.
for tier,(gas,y,band) in enumerate([('Nitrogen',-1.50,'bronze'),('Oxygen',-.01,'blue')]):
    for j in range(4):
        a=j*math.pi/2
        normal=np.array((math.sin(a),0,math.cos(a)))
        tangent=(math.cos(a),0,-math.sin(a))
        center=np.array(h.point(.54,a,y))
        b=Batch()
        vessel(b,center,.35,1.30,'frame')
        for dy in (-.28,.28):
            lathe(b[band],[(dy-.025,.356),(dy+.025,.356)],center,32)
            beam(b['steel'],center+normal*.34+(0,dy,0),h.point(frame_radius(2.5,a),a,y+dy),.105,.075,(0,1,0))
        plate(b,center+normal*.352,tangent,(0,1,0),.35,.14,.016,'frame',1-tier)
        tube(b[band],center+(0,.715,0),(0,y+.715,0),.018,10)
        mount(f'KLS_{gas}_{j+1}',b,center,(.48,1.17,.48))

for i,(kind,y,band) in enumerate([('Water',1.11,'blue'),('Food',1.84,'bronze')]):
    b=Batch()
    profile=[(-.34,.045),(-.34,.80),(-.30,.89),(-.25,.92),(.25,.92),(.30,.89),(.34,.80),(.34,.045)]
    lathe(b['white'],profile,(0,y,0),48)
    for dy in (-.265,.265):
        lathe(b['frame'],[(dy-.022,.921),(dy+.022,.921)],(0,y,0),48)
    lathe(b[band],[(-.17,.924),(-.13,.924)],(0,y,0),48)
    for j in range(8):
        a=j*math.pi/4
        norm=(math.sin(a),0,math.cos(a))
        beam(b['steel'],h.point(.92,a,y-.25),h.point(.92,a,y+.25),.024,.02,norm)
        if j%2==0:
            plate(b,h.point(.923,a,y+.04),(math.cos(a),0,-math.sin(a)),(0,1,0),.50,.17,.02,'frame',3-i)
            beam(b['steel'],h.point(.90,a,y-.25),h.point(frame_radius(2.5,a),a,y-.25),.10,.07,(0,1,0))
    mount('KLS_'+kind,b,(0,y,0),(1.30,.62,1.30))
b=Batch()
tube(b['frame'],(0,-2.21,0),(0,2.21,0),.10,20)
terminal_interface(b,2.5,4.75)
mount('KLS_Carrier',b)

# Strip unused material slots and textures, preserving each renderer mapping.
used=sorted({idx for _,n in walk(model.root) for idx in n.get('materials',[])})
for _,n in walk(model.root):
    if 'materials' in n:n['materials']=[used.index(idx) for idx in n['materials']]
model.materials=[model.materials[idx] for idx in used]
indices=sorted({value['index'] for mat in model.materials for value in mat['properties'].values() if isinstance(value,dict)})
for mat in model.materials:
    if mat['name']=='RWSS_atlas':mat['name']='KLS_markings'
    for value in mat['properties'].values():
        if isinstance(value,dict):value['index']=indices.index(value['index'])
model.textures=[model.textures[idx] for idx in indices]
for texture in model.textures:
    if texture['name']=='rwss_atlas':
        texture['name']='rwkls_markings'
    else:
        filename=texture['name']+('.dds' if texture['type']==1 else '.png')
        shutil.copyfile(ORIGINAL/filename,M/filename)
write(model,M/'RWSS_KLS_XL.mu')

# Values from the installed ModuleManager.ConfigCache: B9 base volumes and
# per-unit ratios for the Big radial tank and 2.5 m inline supply container.
resources={'Oxygen':4*289*200,'Nitrogen':4*289*180,'Food':3270,'Water':3270}
volume=8*289+2*3270
needs=':NEEDS[RoosterWorksStationSupport,Kerbalism,ProfileDefault,CommunityResourcePack,B9PartSwitch]'
cfg='B9_TANK_TYPE'+needs+'\n{\n    name = RWSS_KLS_XL_Loadout\n'
cfg+=f'    tankMass = {volume*.000106275:.9f}\n    tankCost = {volume*.15:.2f}\n'
for resource,amount in resources.items():
    cfg+=f'    RESOURCE\n    {{\n        name = {resource}\n        unitsPerVolume = {amount}\n        percentFilled = 100\n    }}\n'
cfg+='}\n\n@PART[RW_OctoSupport_XL]:HAS[@MODULE[ModuleB9PartSwitch]:HAS[#moduleID[SupportStorage],#baseVolume[1]]]'+needs+'''
{
    MODEL
    {
        model = RoosterWorksKerbalismSupport/Models/RWSS_KLS_XL
    }
    @MODULE[ModuleB9PartSwitch]:HAS[#moduleID[SupportStorage]]
    {
        SUBTYPE
        {
            name = RWSS_KerbalismLifeSupport
            title = Kerbalism Life Support
            primaryColor = #759188
            secondaryColor = #486d89
            tankType = RWSS_KLS_XL_Loadout
            transform = RWSS_KLS_Payload
            addedMass = -1.06
            addedCost = 5550
        }
    }
}
'''
(GD/'LifeSupport.cfg').write_text(cfg,encoding='utf-8')
shutil.copyfile(BASE/'LICENSE',GD/'LICENSE')

exported=load(M/'RWSS_KLS_XL.mu')
nodes=list(walk(exported.root))
assert len([n for _,n in nodes if 'collider' in n])==10
for name in ('Oxygen','Nitrogen'):
    assert all(any(n['name']==f'KLS_{name}_{j}' for _,n in nodes) for j in range(1,5))
assert any(n['name']=='RWSS_KLS_Payload' for _,n in nodes)
for _,n in nodes:
    if 'mesh' not in n:continue
    v=np.array(n['mesh']['vertices'])
    assert np.isfinite(v).all() and len(v)<65535 and abs(v[:,1]).max()<2.37501
    for tris in n['mesh']['submeshes']:
        t=np.array(tris);assert t.min()>=0 and t.max()<len(v)
        assert np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1).min()>1e-12
assert cfg.count(needs)==2 and resources==dict(Oxygen=231200,Nitrogen=208080,Food=3270,Water=3270)
print('Export verified:',resources,flush=True)
