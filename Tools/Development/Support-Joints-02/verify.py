from pathlib import Path
import sys, zipfile, math, json
here=Path(__file__).resolve().parent
base=here.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(base/'Source'),str(base/'Tools'),str(base/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
import numpy as np
from native_model import load,walk
from config_nodes import parse

with zipfile.ZipFile(here/'RoosterWorks-Station-Support-v1.0.10-test.2-Install.zip') as z:
    z.extractall(here/'Build')
gd=here/'Build/GameData/RoosterWorksStationSupport'
cache={};checks=0;faces=0;core_choices=0
for cfg in sorted((gd/'Parts').glob('*.cfg')):
    raw=cfg.read_bytes()
    try:text=raw.decode('utf-8')
    except UnicodeDecodeError:text=raw.decode('cp1252')
    part=parse(text).children[0]
    filename=next(child.get('model').split('/')[-1] for child in part.children if child.header=='MODEL')
    if filename not in cache:cache[filename]=load(gd/'Models'/(filename+'.mu'))
    m=cache[filename];nodes=list(walk(m.root));names={n['name'] for _,n in nodes}
    scale=float(part.get('rescaleFactor'))
    if 'Hub' in filename or 'Adapter' in filename or 'Reducer' in filename:
        switch=next(n for n in part.children if n.get('moduleID') in ('HubStorage','AdapterInterior'))
        opts={n.get('name'):n for n in switch.children}
        assert opts['ServiceCore'].get('transform')=='RWJ_Core' and 'RWJ_Core' in names
        assert opts['Empty'].get('defaultSubtypePriority')=='1' and opts['ServiceCore'].get('tankType') is None
        core_choices+=1
        if 'Hub' in filename:
            assert opts['Standard'].get('transform')=='RWJ_Mixed' and opts['Battery'].get('transform')=='RWG_Battery'
            assert all(any(p.startswith('/'+filename+'/RWJ_Mixed/RWJ_'+group) for p,n in nodes) for group in ('Mono_-1','Mono_1','Cell_-1','Cell_1'))
    for p,n in nodes:
        if 'mesh' not in n or '/RWJ_' not in p:continue
        mesh=n['mesh'];v=np.array(mesh['vertices']);tri=np.asarray(mesh['submeshes'][0])
        assert len(v)<65535 and np.isfinite(v).all() and np.isfinite(mesh['normals']).all()
        assert np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1).min()>1e-12,p
    for i,value in enumerate(v for k,v in part.values if k.startswith('node_stack_')):
        v=np.array([float(x) for x in value.split(',')]);center,axis=v[:3],v[3:6]
        diameter=1.25*v[6]/scale;s=diameter/2.5
        # Intersect the exported, planar frame rim with radial sample rays on
        # every side. Sample actual triangles rather than the outer bounding box.
        n=next(n for p,n in nodes if n['name']==f'RWJ_Port{i}_steel_0')
        mesh=n['mesh'];verts=np.array(mesh['vertices'])-center
        u=np.array([1.,0,0]) if abs(axis[0])<.5 else np.array([0.,1.,0])
        b=np.cross(axis,u);tri=verts[np.asarray(mesh['submeshes'][0])]
        tri=tri[np.max(abs(tri@axis),axis=1)<1e-6]
        mid=np.linalg.norm(tri.mean(axis=1),axis=1)
        rim=tri[mid<1.215*s]
        assert len(rim)>=12 and np.max(abs(rim@axis))*scale<.00001
        xy=np.stack((rim@u,rim@b),axis=2)
        boundary=xy[np.linalg.norm(rim,axis=2)>diameter*.47]
        corners=np.unique(np.round(boundary,5),axis=0)
        assert len(corners) in (6,8)
        corners=corners[np.argsort(np.arctan2(corners[:,1],corners[:,0]))]
        def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
        sides=np.roll(xy,-1,axis=1)-xy
        for start,end in zip(corners,np.roll(corners,-1,axis=0)):
            for t in (.1,.3,.5,.7,.9):
                sample=((1-t)*start+t*end)*(.47*diameter)/(.47*diameter+.024*s)
                signs=np.stack([cross(sides[:,j],sample-xy[:,j]) for j in range(3)],axis=1)
                assert ((signs.min(axis=1)>=-1e-7)|(signs.max(axis=1)<=1e-7)).any()
        faces+=1;checks+=len(rim)
assert len(cache)==16 and faces==54 and core_choices==9,(len(cache),faces,core_choices)
print(f'{faces} fitted part ports, {checks} flush rim triangles, {core_choices} core selectors.')
