"""Correct outward-facing label UVs in the unified test. Run from any directory."""
from pathlib import Path
import json, os, sys, zipfile

out=Path(__file__).resolve().parent
base=out.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(base/'Tools'),str(base/'Source'),str(base/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
import numpy as np
from PIL import Image,ImageDraw
from native_model import load,walk
from native_derivatives import write

prefix='GameData/RoosterWorksStationSupport/'
source=out.parent/'Support-Joints-02/RoosterWorks-Station-Support-v1.0.10-test.2-Install.zip'
work=out/'Build';work.mkdir(exist_ok=True)
with zipfile.ZipFile(source) as archive:
    files={p:archive.read(p) for p in archive.namelist()}
textures={'rwss_atlas','rwkls_markings'}
samples={}
count=0;modified=0

def labels(model):
    for path,n in walk(model.root):
        if 'mesh' not in n:continue
        for index,material in enumerate(n['materials']):
            prop=model.materials[material]['properties']['_MainTex']
            tex=model.textures[prop['index']]['name']
            if tex in textures:
                assert len(n['materials'])==1 and prop['scale']==(1.,1.) and prop['offset']==(0.,0.)
                yield path,n['mesh'],tex

def screen_coords(mesh):
    tris=np.asarray(mesh['submeshes'][0]);v=np.asarray(mesh['vertices'])[tris]
    n=np.asarray(mesh['normals'])[tris[:,0]]
    right=np.cross(n,[0.,1.,0.]);right/=np.linalg.norm(right,axis=1)[:,None]
    up=np.cross(right,n)
    return tris,np.stack(((v*right[:,None,:]).sum(2),(v*up[:,None,:]).sum(2)),axis=2)

def orientation(mesh):
    tri,xy=screen_coords(mesh)
    uv=np.asarray(mesh['uvs'])[tri]
    # Map the U and V basis into the viewer's right/up directions.
    transform=np.linalg.solve(uv[:,1:]-uv[:,:1],xy[:,1:]-xy[:,:1])
    return transform[:,0,0],transform[:,1,1]

for name in list(files):
    if not name.endswith('.mu'):continue
    f=work/Path(name).name;f.write_bytes(files[name]);model=load(f)
    targets=list(labels(model))
    if not targets:continue
    # Verify the serializer round-trips the original before changing coordinates.
    write(model,f);assert f.read_bytes()==files[name],name
    for path,mesh,tex in targets:
        dx,dy=orientation(mesh)
        assert (dx<0).all() and (dy>0).all(),(name,path,'unexpected original orientation')
        mesh['uvs']=[(1-u,v) for u,v in mesh['uvs']]
        if 'tangents' in mesh:mesh['tangents']=[(-x,-y,-z,-w) for x,y,z,w in mesh['tangents']]
    write(model,f);export=load(f)
    for path,mesh,tex in labels(export):
        dx,dy=orientation(mesh)
        assert (dx>0).all() and (dy>0).all(),(name,path)
        count+=len(dx)//2
        kind=next((k for needle,k in [('ArmorPanels/','Armor'),('RWSS_Battery/','Battery'),('KLS_Food/','Food'),('KLS_Water/','Water'),('KLS_Oxygen_1/','Oxygen'),('KLS_Nitrogen_1/','Nitrogen')] if needle in path),None)
        if kind and kind not in samples:
            tri,xy=screen_coords(mesh)
            samples[kind]=(tex,xy[0],np.asarray(mesh['uvs'])[tri[0]])
    modified+=1;files[name]=f.read_bytes()

# A low-CPU proof samples the actual exported UVs from the exterior side.
import io
names=['Armor','Battery','Food','Water','Oxygen','Nitrogen']
sheet=Image.new('RGB',(900,3*150),'#30373b');draw=ImageDraw.Draw(sheet)
for j,kind in enumerate(names):
    tex,xy,uv=samples[kind]
    im=Image.open(io.BytesIO(files[prefix+'Models/'+tex+'.png'])).convert('RGB')
    xy=(xy-xy.min(axis=0))/np.ptp(xy,axis=0)
    xy[:,0]*=420;xy[:,1]=(1-xy[:,1])*105
    pixels=uv*np.array(im.size);pixels[:,1]=im.height-pixels[:,1]
    affine=np.linalg.solve(np.column_stack((xy,np.ones(3))),pixels).T.flatten()
    patch=im.transform((420,105),Image.Transform.AFFINE,affine,Image.Resampling.BICUBIC)
    x=15+450*(j%2);y=9+150*(j//2);draw.text((x,y),kind,fill='white');sheet.paste(patch,(x,y+21))
sheet.save(out/'Label-proof.png')
version_path=prefix+'RoosterWorksStationSupport.version'
version=json.loads(files[version_path]);version['VERSION']['BUILD']=3
files[version_path]=(json.dumps(version,indent=2)+'\n').encode()
files[prefix+'INSTALL.txt']=files[prefix+'INSTALL.txt'].replace(b'v1.0.10-test.2',b'v1.0.10-test.3')
target=out/'RoosterWorks-Station-Support-v1.0.10-test.3-Install.zip';temp=target.with_suffix('.partial')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for p,v in sorted(files.items()):archive.writestr(p,v)
with zipfile.ZipFile(temp) as archive:
    assert archive.testzip() is None
    assert all(p.startswith(prefix) and archive.read(p)==v for p,v in files.items())
os.replace(temp,target)
print(f'{count} exterior labels verified across {modified} models; {len(files)} archive entries verified.')
