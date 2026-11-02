"""Lossless native MU serializer and native uniform/analytic derivatives.

Preserves shader properties, UVs, normals, hierarchy, triggers and lights.
Imported models are never overwritten; derivative output always has a new ID.
"""
from pathlib import Path
import sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from native_model import load,walk
import build_hab250 as h
GD=ROOT/'GameData/RoosterWorksStationModules';MODELS=GD/'Models'

def write_mesh(w,m):
    w.i(13,len(m['vertices']),len(m['submeshes']));w.i(14)
    for v in m['vertices']:w.f(*v)
    for tag,key in ((15,'uvs'),(16,'uv2'),(17,'normals'),(18,'tangents'),(32,'colors')):
        if key in m:
            w.i(tag)
            for v in m[key]:w.f(*v)
    for tris in m['submeshes']:
        w.i(19,len(tris)*3)
        for tri in tris:w.i(*tri)
    w.i(22)

def write_node(w,n):
    w.s(n['name']);w.f(*n['position'],*n['rotation'],*n['scale']);w.i(24);w.s(n.get('tag','Untagged'));w.i(n.get('layer',0))
    if 'mesh' in n:
        w.i(7);write_mesh(w,n['mesh']);w.i(8)
        for v in n['shadows']:w.b(v)
        w.i(len(n['materials']),*n['materials'])
    if 'collider' in n:
        c=n['collider']
        if c['type']=='mesh':w.i(25);w.b(c['trigger']);w.b(c['convex']);write_mesh(w,c['mesh'])
        else:w.i(28);w.b(c['trigger']);w.f(*c['size'],*c['center'])
    if 'light' in n:
        l=n['light'];w.i(23,l['type']);w.f(l['intensity'],l['range'],*l['color']);w.i(l['cullingMask'] if l['cullingMask']<2**31 else l['cullingMask']-2**32);w.f(l['spotAngle'])
    for child in n['children']:w.i(0);write_node(w,child);w.i(1)

def write(model,target):
    # Avoid the installed KSPCF loader's unused trailing material-table failure.
    highest=max(i for _,n in walk(model.root) for i in n.get('materials',[]))
    materials=model.materials[:highest+1]
    # KSPCF sizes its texture lookup from material references. Trailing unused
    # entries cause TextureError and abort model loading; keep indices stable.
    texture_highest=max((v['index'] for m in materials for v in m['properties'].values()
                         if isinstance(v,dict)),default=-1)
    textures=model.textures[:texture_highest+1]
    w=h.Writer(target);w.i(76543,5);w.s(model.name);write_node(w,model.root)
    w.i(10,len(materials))
    for mat in materials:
        w.s(mat['name']);w.s(mat['shader']);w.i(len(mat['properties']))
        for name,value in mat['properties'].items():
            w.s(name)
            if isinstance(value,dict):w.i(4,value['index']);w.f(*value['scale'],*value['offset'])
            elif isinstance(value,tuple):w.i(0);w.f(*value)
            else:w.i(2);w.f(value)
    w.i(12,len(textures))
    for texture in textures:w.s(texture['name']);w.i(texture['type'])
    w.close()

def scaled_mesh(m,scale):
    m['vertices']=[tuple(v*scale for v in p) for p in m['vertices']]

def derivative(source,target,scale,labels=None):
    model=load(MODELS/(source+'.mu'));model.name=target;model.root['name']=target
    for _,node in walk(model.root):
        node['position']=tuple(v*scale for v in node['position'])
        if 'mesh' in node:scaled_mesh(node['mesh'],scale)
        if 'collider' in node:
            c=node['collider']
            if c['type']=='mesh':scaled_mesh(c['mesh'],scale)
            else:
                c['size']=tuple(v*scale for v in c['size']);c['center']=tuple(v*scale for v in c['center'])
        if 'light' in node:node['light']['range']*=scale
    for texture in model.textures:
        if labels and texture['name'] in labels:texture['name']=labels[texture['name']]
    write(model,MODELS/(target+'.mu'));return model

def export_obj(model,filename,variant='Standard'):
    destination=ROOT/'Source/Blender'/filename;destination.parent.mkdir(exist_ok=True)
    matfile=destination.with_suffix('.mtl')
    matfile.write_text(''.join(f"newmtl MAT{i}\nKd 1 1 1\nmap_Kd ../../GameData/RoosterWorksStationModules/Models/{model.textures[m['properties']['_MainTex']['index']]['name']}.png\n\n" for i,m in enumerate(model.materials)),encoding='utf-8')
    with destination.open('w',encoding='utf-8') as out:
        out.write('mtllib '+matfile.name+'\n');offset=0
        for path,node in walk(model.root):
            if 'mesh' not in node:continue
            if variant=='Standard' and '/SideHatch/' in path:continue
            if variant=='SideHatch' and '/WindowBankStandard/' in path:continue
            assert node['position']==(0.,0.,0.) and node['rotation']==(0.,0.,0.,1.)
            m=node['mesh'];out.write('o '+node['name']+'\n')
            for p in m['vertices']:out.write('v '+' '.join(format(v,'.9g') for v in p)+'\n')
            for uv in m['uvs']:out.write('vt '+' '.join(format(v,'.9g') for v in uv)+'\n')
            for n in m['normals']:out.write('vn '+' '.join(format(v,'.9g') for v in n)+'\n')
            for tris,material in zip(m['submeshes'],node['materials']):
                out.write(f'usemtl MAT{material}\n')
                for tri in tris:out.write('f '+' '.join(f'{i+offset+1}/{i+offset+1}/{i+offset+1}' for i in tri)+'\n')
            offset+=len(m['vertices'])
