"""Upgrade the unified Support test ZIP in isolation, preserving saved identifiers."""
from pathlib import Path
import sys, math, json, zipfile, os
from contextlib import nullcontext
from collections import Counter
from types import SimpleNamespace

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
BASE=ROOT/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(BASE/'Tools'),str(BASE/'Source'),str(BASE/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
from support_art import Batch,node,emit,beam,tube,plate,vessel,bolt,lathe,quad,unit,h,np,materials
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump

prefix='GameData/RoosterWorksStationSupport/'
source=ROOT/'Girder-Expansion/RoosterWorks-Station-Support-v1.0.10-test.1-Install.zip'
with zipfile.ZipFile(source) as z:data={n:z.read(n) for n in z.namelist()}
original=dict(data)
Y=np.array([0.,1.,0.])
counts=Counter()
def point(r,a,y):return np.array(h.point(r,a,y))
def basis(axis):
    if abs(axis[1])>.9:return np.diag([1.,axis[1],1.])
    k=np.cross(Y,axis)
    return np.stack([np.cross(k,p)+k*np.dot(k,p) for p in np.eye(3)],axis=1)

def install_mesh(model,parent,name,batch,mat=None,offset=None):
    if mat is not None:
        for mesh in batch.meshes.values():
            mesh.vertices=list(np.asarray(mesh.vertices)@mat.T+offset)
            mesh.normals=list(np.asarray(mesh.normals)@mat.T)
            if np.linalg.det(mat)<0:mesh.triangles=[(a,c,b) for a,b,c in mesh.triangles]
    emit(model,parent,name,batch)

def ring(b,key,n,profile,phase=0):
    # Closed annular section; each profile segment has an explicit outward normal.
    for (r0,y0),(r1,y1) in zip(profile,profile[1:]+profile[:1]):
        for i in range(n):
            a=phase+i*math.tau/n;c=phase+(i+1)*math.tau/n
            points=[point(r0,a,y0),point(r0,c,y0),point(r1,c,y1),point(r1,a,y1)]
            quad(b[key],points)

def flange(model,port,index):
    center,axis,diam,sides=port;rot=basis(axis);s=diam/2.5
    b=Batch()
    # Both frame rings now reach the node continuously, including the straight girders.
    radius=.47*diam
    ring(b,'steel',sides,[(radius+.030*s,-.063*s),(radius+.030*s,-.006*s),(radius+.024*s,0),(radius-.033*s,0),(radius-.033*s,-.063*s)],math.pi/2)
    # Recess each original exterior cable tip into a dedicated terminal.
    for key,track in [('blue',1.255),('yellow',1.281)]:
        tips=[]
        for path,obj in walk(model.root):
            if 'mesh' not in obj or not obj['name'].startswith(('RWG_Frame_'+key,'RWSS_Frame_'+key)):continue
            verts=obj['mesh']['vertices'];v=(np.asarray(verts)-center)@rot
            indices=np.flatnonzero((abs(v[:,1])<2e-6)&(abs(np.linalg.norm(v[:,[0,2]],axis=1)-1.272*s)<.011*s))
            for i in indices:
                tips.append(v[i]);verts[i]=tuple(np.asarray(verts[i])-.062*s*axis)
        assert tips,(model.name,index,key)
        rest=np.asarray(tips);groups=0
        while len(rest):
            mask=np.linalg.norm(rest-rest[0],axis=1)<.026*s
            tip=rest[mask].mean(0);rest=rest[~mask];a=math.atan2(tip[0],tip[2])
            p=point(1.272*s,a,-.062*s);q=point(track*s,a,-.029*s)
            tube(b[key],p,q,.007*s,12);tube(b[key],q,point(track*s,a,-.002*s),.007*s,12)
            groups+=1
        assert groups==2,(model.name,index,key,groups)
        counts['cable_tips']+=groups
    def band(key,r0,r1,lo,hi):
        ring(b,key,96,[(r1*s,lo*s),(r1*s,hi*s),(r0*s,hi*s),(r0*s,lo*s)])
    band('frame',1.243,1.314,-.042,-.004)
    for key,lo,hi in [('steel',1.243,1.247),('blue',1.247,1.263),('frame',1.263,1.273),('yellow',1.273,1.289),('steel',1.289,1.314)]:
        band(key,lo,hi,-.004,0)
    for a in [math.pi/2+j*math.tau/sides for j in range(sides)]:
        beam(b['frame'],point(radius,a,-.030*s),point(1.25*s,a,-.030*s),.048*s,.020*s,Y)
    install_mesh(model,model.root,'RWJ_Port'+str(index),b,rot,center)
    counts['ports']+=1

def box(parent,name,center,size):
    obj=node(name);obj['collider']=dict(type='box',trigger=0,size=tuple(size),center=tuple(center));parent['children'].append(obj)

def mixed(model):
    parent=node('RWJ_Mixed');model.root['children'].append(parent)
    for side in (-1,1):
        x=side*.40;b=Batch()
        vessel(b,(x,0,0),.34,1.58,'tank')
        for y in (-.28,.28):
            lathe(b['bronze'],[(y-.022,.347),(y+.022,.347)],(x,0,0))
            beam(b['steel'],np.array((x,y,0)),np.array((side*1.19,y,.78)),.07,.07)
            beam(b['frame'],np.array((side*1.19,y,.78)),np.array((side*1.19,0,1.175)),.075,.075)
        tube(b['bronze'],(x,.84,0),(0,.84,0),.022,12)
        install_mesh(model,parent,'RWJ_Mono_'+str(side),b)
        box(parent,'MonoCollider'+str(side),(x,0,0),(.48,1.46,.48))
        b=Batch()
        for y in (-.35,0,.35):
            plate(b,(0,y,.63*side),(side,0,0),Y,.76,.31,.22,'frame',0)
        beam(b['frame'],np.array((0,-.52,.54*side)),np.array((0,.52,.54*side)),.48,.08)
        beam(b['steel'],np.array((0,0,.54*side)),np.array((0,1.175,1.19*side)),.075,.075)
        install_mesh(model,parent,'RWJ_Cell_'+str(side),b)
        box(parent,'CellCollider'+str(side),(0,0,.63*side),(.76,1.02,.22))

def core_arm(model,parent,index,rot,lo,hi,d0,d1,hand,hub=False,hex_end=False):
    b=Batch();s0=d0/2.5;s1=d1/2.5
    def size(y):return s0+(s1-s0)*(y-lo)/(hi-lo)
    section=[(lo,.25*s0),(hi,.25*s1)]
    lathe(b['insulation'],section);lathe(b['frame'],[(hi,.22*s1),(lo,.22*s0)])
    for y,sign in [(hi,1)]+([] if hub else [(lo,-1)]):
        s=size(y)
        ring(b,'steel',48,[(.30*s,y-sign*.048*s),(.30*s,y),(.22*s,y),(.22*s,y-sign*.048*s)][::sign])
        anchor=y-sign*.055*s
        for a in [math.pi/2+j*math.pi/2 for j in range(4)]:
            outer=.47*size(y)*2.5
            if abs(math.cos(a))>.9 and ((d1 if sign==1 else d0)<2 or hex_end):outer*=math.cos(math.pi/6)
            beam(b['steel'],point(.25*s,a,anchor),point(outer,a,anchor),.055*s,.045*s,Y)
    for y in np.linspace(lo+(hi-lo)*.2,hi-(hi-lo)*.2,3):
        s=size(y);lathe(b['frame'],[(y-.022*s,.26*size(y-.022*s)),(y+.022*s,.26*size(y+.022*s))])
    for angle in (math.tau/3,2*math.tau/3):
        for key,delta in [('blue',.065),('yellow',.18)]:
            a=angle+hand*delta
            tube(b[key],point(.28*s0,a,lo),point(.28*s1,a,hi),.007*min(s0,s1),12)
    install_mesh(model,parent,'RWJ_CoreArm'+str(index),b,rot,np.zeros(3))
    size_box=np.abs(rot)@np.array((.31*min(s0,s1),hi-lo,.31*min(s0,s1)))
    box(parent,'CoreCollider'+str(index),rot@(Y*((lo+hi)/2)),size_box)

specs={}
for path,v in original.items():
    if not path.startswith(prefix+'Parts/') or not path.endswith('.cfg'):continue
    try:content=v.decode('utf-8')
    except UnicodeDecodeError:content=v.decode('cp1252')
    part=parse(content).children[0]
    model=next(n.get('model').split('/')[-1] for n in part.children if n.header=='MODEL')
    scale=float(part.get('rescaleFactor','1'))
    ports=[]
    for k,val in part.values:
        if not k.startswith('node_stack_'):continue
        p=np.array([float(x) for x in val.split(',')]);diam=1.25*p[6]/scale
        physical=p[6]*1.25
        ports.append((p[:3],p[3:6],diam,6 if physical==1.25 else 8))
    if model not in specs:specs[model]=ports
    if not (model.startswith('RWG_') or 'Adapter' in model):continue
    hub='Hub' in model
    if hub:
        sw=next(n for n in part.children if n.get('moduleID')=='HubStorage')
        next(n for n in sw.children if n.get('name')=='Standard').set('transform','RWJ_Mixed')
    else:
        sw=Node('MODULE',[('name','ModuleB9PartSwitch'),('moduleID','AdapterInterior'),('switcherDescription','Interior'),('switchInFlight','false')])
        sw.children.append(Node('SUBTYPE',[('name','Empty'),('title','Empty Frame'),('defaultSubtypePriority','1')]))
        part.children.append(sw)
    sw.children.append(Node('SUBTYPE',[('name','ServiceCore'),('title','Central Service Core'),('transform','RWJ_Core'),('addedMass',str(round(.07*scale**3,5))),('addedCost',str(round(240*scale**3)))]))
    data[path]=dump(part).encode('utf-8')

(OUT/'Build').mkdir(exist_ok=True)
with nullcontext(OUT/'Build') as tmp:
    f=Path(tmp)/'part.mu'
    for name,ports in specs.items():
        path=prefix+'Models/'+name+'.mu';f.write_bytes(data[path]);m=load(f)
        # All these assets use the original indexed Support material palette.
        old=m.materials;materials(m);assert [x['name'] for x in old]==[x['name'] for x in m.materials[:len(old)]]
        for i,port in enumerate(ports):flange(m,port,i)
        if name.startswith('RWG_') or 'Adapter' in name:
            parent=node('RWJ_Core');m.root['children'].append(parent)
            if 'Hub' in name:
                mixed(m)
                b=Batch();vessel(b,(0,0,0),.40,.78,'frame');install_mesh(m,parent,'RWJ_Distributor',b)
                for i,(center,axis,d,sides) in enumerate(ports):
                    core_arm(m,parent,i,basis(axis),.24,np.linalg.norm(center),d,d,1 if abs(axis[1])>.9 else -1,True,sides==6)
            else:
                low,high=sorted(ports,key=lambda p:p[0][1])
                core_arm(m,parent,0,np.eye(3),low[0][1],high[0][1],low[2],high[2],1)
        write(m,f);data[path]=f.read_bytes();out=load(f)
        tree=list(walk(out.root))
        for i,(center,axis,d,sides) in enumerate(ports):
            s=d/2.5
            for key,r0,r1 in [('blue',1.247,1.263),('yellow',1.273,1.289)]:
                vs=np.concatenate([n['mesh']['vertices'] for _,n in tree if n['name'].startswith('RWJ_Port'+str(i)+'_'+key+'_')])-center
                axial=vs@axis;face=vs[abs(axial)<1e-6];r=np.linalg.norm(face,axis=1)/s
                for radius in (r0,r1):
                    pts=face[abs(r-radius)<2e-6]@basis(axis)
                    angles=np.unique(np.round(np.arctan2(pts[:,2],pts[:,0])%(2*math.pi),5))
                    assert max(np.diff(np.r_[angles,angles[0]+2*math.pi]))<.067
                assert r1*math.cos(math.pi/96)>r0 # overlap even at worst relative roll
            counts['verified_faces']+=1
        print(name,flush=True)
version=prefix+'RoosterWorksStationSupport.version'
meta=json.loads(data[version]);meta['VERSION']['BUILD']=2;data[version]=(json.dumps(meta,indent=2)+'\n').encode()
data[prefix+'INSTALL.txt']=data[prefix+'INSTALL.txt'].replace(b'v1.0.10-test.1',b'v1.0.10-test.2')
target=OUT/'RoosterWorks-Station-Support-v1.0.10-test.2-Install.zip'
temp=target.with_suffix('.partial')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for path,v in sorted(data.items()):z.writestr(path,v)
with zipfile.ZipFile(temp) as z:
    assert z.testzip() is None and set(z.namelist())==set(original)
    for path,v in data.items():assert path.startswith(prefix) and z.read(path)==v
os.replace(temp,target)
print(dict(counts))
