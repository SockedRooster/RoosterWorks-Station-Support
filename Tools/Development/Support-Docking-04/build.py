"""Add three single-faced docking collars to the verified single-folder Support build."""
from pathlib import Path
from types import SimpleNamespace
import sys, math, json, os, zipfile

out=Path(__file__).resolve().parent
base=out.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(base/'Tools'),str(base/'Source'),str(base/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
from support_art import Batch,node,emit,materials,beam,tube,bolt,quad,unit,h,np
from native_derivatives import write
from native_model import load,walk
from config_nodes import Node,parse,dump

source=out.parent/'Support-Labels-03/RoosterWorks-Station-Support-v1.0.10-test.3-Install.zip'
with zipfile.ZipFile(source) as archive:files={p:archive.read(p) for p in archive.namelist()}
prefix='GameData/RoosterWorksStationSupport/'
work=out/'Build';work.mkdir(exist_ok=True)

def make(dia,size):
    s=dia/2.5;half=.19*s;count=6 if size==1 else 8
    ident=f'RWG_Docking_{int(dia*100)}'
    model=SimpleNamespace(name=ident,root=node(ident));materials(model)
    frame=Batch();skins=[Batch(),Batch()]
    def point(r,a,y):return np.array(h.point(r*s,a,y*s))
    def segment(batch,key,n,lo,hi,outer,bottom,top,inner,phase=0):
        # Closed sector with four visible surfaces. Ring sections share edges.
        step=math.tau/n
        for i in range(lo,hi):
            a,c=phase+i*step,phase+(i+1)*step
            outline=[(outer,bottom),(outer,top),(inner,top),(inner,bottom)]
            for (r,y),(r1,y1) in zip(outline,outline[1:]+outline[:1]):
                quad(batch[key],[point(r,a,y),point(r,c,y),point(r1,c,y1),point(r1,a,y1)])
            if hi-lo<n:
                if i==lo:quad(batch[key],[point(r,a,y) for r,y in outline])
                if i==hi-1:quad(batch[key],[point(r,c,y) for r,y in outline[::-1]])
    def ring(key,outer,inner,lo,hi,n=64,phase=0):
        segment(frame,key,n,0,n,outer,lo,hi,inner,phase)
    ring('steel',1.205,1.14,-.19,-.137,count,math.pi/2)
    ring('frame',.98,.77,-.145,.145)
    ring('steel',.84,.76,.12,.19)
    ring('black',.873,.84,.155,.189)
    ring('steel',1.11,.873,.133,.172)
    for j in range(12):
        segment(frame,'bronze' if j%3==0 else 'steel',96,j*8,j*8+6,1.083,.172,.188,.977)
        a=(j+.38)*math.tau/12
        bolt(frame,point(.925,a,.172),(0,1,0),.023*s)
    for j in range(count):
        a=math.pi/2+j*math.tau/count;c=a+math.tau/count
        normal=unit(point(1,(a+c)/2,0))
        p,q=point(1.175,a,-.15),point(1.075,a,.135)
        beam(frame['steel'],p,q,.092*s,.077*s,normal)
        beam(frame['frame'],p,point(1.075,c,.135),.041*s,.040*s,normal)
        beam(frame['steel'],point(.80,a,-.145),p,.075*s,.056*s,(0,1,0))
        for batch,color in zip(skins,('white','grey')):
            corners=np.array([p,point(1.175,c,-.15),point(1.075,c,.135),q])
            center=corners.mean(0);outer=center+.91*(corners-center)+normal*.027*s
            inner=outer-normal*.020*s
            quad(batch[color],list(outer));quad(batch['frame'],list(inner[::-1]))
            for k in range(4):quad(batch['frame'],[outer[k],inner[k],inner[(k+1)%4],outer[(k+1)%4]])
            for k in (0,2):bolt(batch,center+(outer[k]-center)*.82+normal*.01*s,normal,.017*s)
        col=node(f'CollarCollider_{j}')
        # Local X spans the tangential chord. The center bore and capture plane stay clear.
        angle=(a+c)/2;col['position']=tuple(point(.91,angle,0))
        col['rotation']=(0,math.sin(angle/2),0,math.cos(angle/2))
        col['collider']=dict(type='box',trigger=0,center=(0,0,0),size=(1.82*s*math.tan(math.pi/count),.29*s,.17*s))
        model.root['children'].append(col)
    for sign in (-1,1):
        face=.19*sign;inside=face-sign*.036
        low,high=sorted((inside,face))
        for key,r0,r1 in [('steel',1.243,1.247),('blue',1.247,1.263),('frame',1.263,1.273),('yellow',1.273,1.289),('steel',1.289,1.314)]:
            ring(key,r1,r0,low,high,96)
        for j in range(count):
            a=math.pi/2+j*math.tau/count
            beam(frame['steel'],point(.99 if sign>0 else 1.165,a,sign*.15),point(1.25,a,sign*.166),.068*s,.032*s,(0,1,0))
    for a in (math.tau/3,2*math.tau/3):
        for key,r,delta,gauge in [('steel',1.30,0,.014),('blue',1.255,.065,.007),('yellow',1.281,.092,.007)]:
            tube(frame[key],point(r,a+delta,-.17),point(r,a+delta,.17),s*gauge,12)
    emit(model,model.root,'Coupling',frame)
    for name,batch in zip(('ArmorPanels','ArmorPanelsGrey'),skins):
        obj=node(name);model.root['children'].append(obj);emit(model,obj,name,batch)
    dock=node('DockFace');dock['position']=(0,half,0)
    dock['rotation']=(-math.sqrt(.5),0,0,math.sqrt(.5));model.root['children'].append(dock)
    path=work/(ident+'.mu');write(model,path);export=load(path)
    nodes=dict((n['name'],n) for _,n in walk(export.root));t=nodes['DockFace']
    x,y,z,w=t['rotation'];forward=np.array([2*(x*z+w*y),2*(y*z-w*x),1-2*(x*x+y*y)])
    assert np.allclose(forward,(0,1,0),atol=1e-6) and np.allclose(t['position'],(0,half,0))
    for n in nodes.values():
        if 'mesh' in n:
            m=n['mesh'];v=np.asarray(m['vertices']);tri=np.asarray(m['submeshes'][0])
            assert abs(v[:,1]).max()<=half+1e-6 and np.isfinite(v).all() and len(v)<65535
            assert np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1).min()>1e-12
    assert all(prefix+'Models/'+tex['name']+('.dds' if tex['type']==1 else '.png') in files for tex in export.textures)
    files[prefix+'Models/'+path.name]=path.read_bytes()
    cfg=parse(files[prefix+'Parts/RWG_Reducer_125_250.cfg'].decode()).children[0]
    cfg.children=[n for n in cfg.children if n.header=='MODEL' or n.get('name')=='ModulePartVariants']
    cfg.values=[(k,v) for k,v in cfg.values if not k.startswith('node_')]
    mass=(.055,.20,.55)[size-1];cost=(320,900,2200)[size-1]
    for k,v in dict(name=ident,title=f'RoosterWorks {dia:g} m Girder Docking Coupler',description=f'Mount the polygonal foot on a {dia:g} m girder. The circular latch face docks with size{size} ports, supports resource crossfeed and releases through Undock.',mass=mass,cost=cost,entryCost=cost*4,category='Coupling',TechRequired='specializedConstruction' if size==1 else 'metaMaterials',bulkheadProfiles=f'size{size}',fuelCrossFeed='True',tags='roosterworks girder docking port coupler truss clamp station').items():cfg.set(k,v)
    cfg.set('node_stack_top',f'0, {half:g}, 0, 0, 1, 0, {size}')
    cfg.set('node_stack_bottom',f'0, {-half:g}, 0, 0, -1, 0, {size}')
    cfg.children[0].set('model','RoosterWorksStationSupport/Models/'+ident)
    for v in cfg.children[1].children:
        if v.get('name')!='Open':v.set('mass',round(mass*.25,6));v.set('cost',round(cost*.1))
    cfg.children.append(Node('MODULE',list(dict(name='ModuleDockingNode',nodeTransformName='DockFace',controlTransformName='DockFace',referenceAttachNode='top',useReferenceAttachNode='true',nodeType=f'size{size}',crossfeed='true',stagingEnabled='false').items())))
    cfgpath=prefix+'Parts/'+ident+'.cfg';files[cfgpath]=dump(cfg).encode('utf-8')
    c=parse(files[cfgpath].decode()).children[0];mod=c.children[-1]
    assert mod.get('nodeType')==f'size{size}' and mod.get('nodeTransformName') in nodes
    for n in ('top','bottom'):
        vals=list(map(float,c.get('node_stack_'+n).split(',')));assert vals[1]==(half if n=='top' else -half) or abs(abs(vals[1])-half)<1e-8
    print(ident, 'verified')

for i,d in enumerate((1.25,2.5,3.75),1):make(d,i)
vf=prefix+'RoosterWorksStationSupport.version';meta=json.loads(files[vf]);meta['VERSION']['BUILD']=4
files[vf]=(json.dumps(meta,indent=2)+'\n').encode()
files[prefix+'INSTALL.txt']=files[prefix+'INSTALL.txt'].replace(b'v1.0.10-test.3',b'v1.0.10-test.4')+b'\nGirder Docking Couplers are in Coupling. Attach the polygonal base to the girder. Target the circular face of a matching docking port.\n'
target=out/'RoosterWorks-Station-Support-v1.0.10-test.4-Install.zip';tmp=target.with_suffix('.partial')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for p,v in sorted(files.items()):z.writestr(p,v)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None and all(p.startswith(prefix) and z.read(p)==v for p,v in files.items())
os.replace(tmp,target)
