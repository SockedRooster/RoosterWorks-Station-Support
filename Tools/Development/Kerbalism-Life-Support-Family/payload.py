"""Build the optional Octo XL payload using the Station Support v1.0.9 sources."""
from pathlib import Path
import sys, math, shutil, copy
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
def make_payload(diameter,length,model_name):
    scale=np.array((diameter/2.5,length/4.75,diameter/2.5))
    source = load(ORIGINAL/'RW_OctoSupport_XL.mu')
    model = SimpleNamespace(name=model_name, root=node('RWSS_KLS_Model'),
                            materials=copy.deepcopy(source.materials), textures=copy.deepcopy(source.textures))
    payload = node('RWSS_KLS_Payload')
    model.root['children'].append(payload)
    def mount(name, batch, collider_center=None, collider_size=None, scaled=True):
        if scaled:
            for mesh in batch.meshes.values():
                mesh.vertices = [tuple(v) for v in np.asarray(mesh.vertices)*scale]
                normals = np.asarray(mesh.normals)/scale
                mesh.normals = [tuple(v) for v in normals/np.linalg.norm(normals,axis=1)[:,None]]
        from support_art import emit
        part = node(name)
        payload['children'].append(part)
        emit(model, part, name, batch)
        if collider_size:
            collision = node(name+'_Collider')
            collision['collider'] = dict(type='box',trigger=0,center=tuple(np.asarray(collider_center)*scale),size=tuple(np.asarray(collider_size)*scale))
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
                beam(b['steel'],center+normal*.34+(0,dy,0),h.point(frame_radius(diameter,a)/scale[0],a,y+dy),.105,.075,(0,1,0))
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
                beam(b['steel'],h.point(.90,a,y-.25),h.point(frame_radius(diameter,a)/scale[0],a,y-.25),.10,.07,(0,1,0))
        mount('KLS_'+kind,b,(0,y,0),(1.30,.62,1.30))
    b=Batch()
    tip=length/2-.165*scale[0]
    tube(b['frame'],(0,-tip,0),(0,tip,0),.10*scale[0],20)
    terminal_interface(b,diameter,length)
    mount('KLS_Carrier',b,scaled=False)
    
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
    write(model,M/(model_name+'.mu'))
