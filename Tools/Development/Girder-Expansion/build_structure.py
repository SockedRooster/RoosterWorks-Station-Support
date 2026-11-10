"""Three structural reducers and a six-way storage hub. Build against Support v1.0.9."""
from pathlib import Path
from types import SimpleNamespace
from itertools import combinations, product
import sys, math, shutil, copy, json
ROOT=Path(__file__).resolve().parent
BASE=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(BASE/'Tools'),str(BASE/'Source'),str(BASE/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
from support_art import *
from build_support_revamp import frame_radius
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
GD=ROOT/'GameData/RoosterWorksGirderExpansion';MODELS=GD/'Models';PARTS=GD/'Parts'
for folder in (MODELS,PARTS):folder.mkdir(parents=True,exist_ok=True)
ORIG=BASE/'GameData/RoosterWorksStationSupport'
source=load(ORIG/'Models/RW_OctoSupport_Medium.mu')
template=parse((ORIG/'Parts/RW_OctoSupport_Medium.cfg').read_bytes().decode('cp1252')).children[0]
Y=np.array((0.,1.,0.))
lanes=(2*math.pi/3,4*math.pi/3)
lines=(('steel',0,1.30,.014),('blue',.065,1.272,.007),('yellow',.092,1.272,.007))
audit={}

def pos(r,a,y):
    return np.array(h.point(r,a,y))

def conduit(mesh,centers,radii,guide):
    directions=[unit(q-p) for p,q in zip(centers,centers[1:])]
    axes=[directions[0]]+[unit(p+q) for p,q in zip(directions,directions[1:])]+[directions[-1]]
    rings=[];normals=[]
    for center,radius,axis in zip(centers,radii,axes):
        u=unit(np.cross(axis,guide));v=unit(np.cross(axis,u))
        ns=[u*math.cos(j*math.tau/12)+v*math.sin(j*math.tau/12) for j in range(12)]
        normals.append(ns);rings.append([center+radius*n for n in ns])
    for row in range(len(rings)-1):
        for j in range(12):
            k=(j+1)%12;indices=((row,j),(row,k),(row+1,k),(row+1,j))
            mesh.quad([rings[n][i] for n,i in indices],[normals[n][i] for n,i in indices])
    for row,sign in ((0,-1),(-1,1)):
        for j in range(12):
            k=(j+1)%12
            a,b=(k,j) if sign<0 else (j,k)
            mesh.triangle([centers[row],rings[row][a],rings[row][b]],[sign*axes[row]]*3,[(.5,.5),(0,0),(1,1)])

class Girder:
    def __init__(self,name):
        self.name=name
        self.model=SimpleNamespace(name=name,root=node(name),materials=copy.deepcopy(source.materials),textures=copy.deepcopy(source.textures))
        self.frame=Batch();self.armor=[Batch(),Batch()];self.endpoints=[];self.panel_colliders=[]

    def strut(self,p,q,width,collision=False,key='steel'):
        axis=unit(q-p);beam(self.frame[key],p,q,width,width*.78,axis)
        if collision:
            body=node('BeamCollider_'+str(len(self.model.root['children'])))
            quat=np.array((axis[2],0,-axis[0],1+axis[1]))
            body['rotation']=tuple(unit(quat)) if np.linalg.norm(quat)>1e-7 else (1,0,0,0)
            body['position']=tuple((p+q)/2)
            body['collider']=dict(type='box',trigger=0,size=(width*.8,float(np.linalg.norm(q-p)),width*.8),center=(0,0,0))
            self.model.root['children'].append(body)

    def rib(self,ring,width,collision=False):
        for p,q in zip(ring,ring[1:]+ring[:1]):self.strut(p,q,width,collision)

    def panel(self,points):
        center=np.mean(points,axis=0);normal=unit(np.cross(points[1]-points[0],points[-1]-points[0]))
        if np.dot(normal,center)<0:normal=-normal;points=list(reversed(points))
        face=[center+(p-center)*.93+normal*.022 for p in points]
        back=[p-normal*.026 for p in face]
        count=len(face)
        triangles=[(0,j,j+1) for j in range(1,count-1)]+[(count,count+j+1,count+j) for j in range(1,count-1)]
        for j in range(count):
            k=(j+1)%count
            triangles.extend([(j,j+count,k+count),(j,k+count,k)])
        co=node('PanelCollider_'+str(len(self.panel_colliders)))
        co['collider']=dict(type='mesh',trigger=0,convex=1,mesh=dict(vertices=face+back,submeshes=[triangles]))
        self.panel_colliders.append(co)
        for b,k in zip(self.armor,('white','grey')):
            def surface(vertices,n):
                for j in range(1,len(vertices)-1):b[k].triangle([vertices[0],vertices[j],vertices[j+1]],[n]*3,[(0,0),(1,0),(1,1)])
            surface(face,normal);surface(list(reversed(back)),-normal)
            for j in range(len(face)):
                m=(j+1)%len(face);quad(b['frame'],[face[j],back[j],back[m],face[m]])
                bolt(b,center+(points[j]-center)*.76+normal*.024,normal,.018)

    def export(self):
        for group,b in zip(('ArmorPanels','ArmorPanelsGrey'),self.armor):
            parent=node(group);self.model.root['children'].append(parent);emit(self.model,parent,group,b)
            parent['children'].extend(copy.deepcopy(self.panel_colliders))
        emit(self.model,self.model.root,'RWG_Frame',self.frame)
        write(self.model,MODELS/(self.name+'.mu'))
        model=load(MODELS/(self.name+'.mu'));nodes=list(walk(model.root))
        meshes=[n for _,n in nodes if 'mesh' in n]
        for n in meshes:
            mesh=n['mesh'];v=np.asarray(mesh['vertices']);assert len(v)<65535 and np.isfinite(v).all()
            for triangles in mesh['submeshes']:
                tri=np.asarray(triangles);assert tri.min()>=0 and tri.max()<len(v)
                assert np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1).min()>1e-12
        for key,center,normal,r in self.endpoints:
            v=np.concatenate([n['mesh']['vertices'] for n in meshes if n['name'].startswith('RWG_Frame_'+key+'_')])
            delta=v-center
            ring=v[(abs(delta@normal)<2e-6)&(abs(np.linalg.norm(delta,axis=1)-r)<2e-6)]
            assert len(ring)>=12 and np.linalg.norm(ring.mean(0)-center)<2e-5,(self.name,key,'interface mismatch')
        for tex in model.textures:
            f=tex['name']+('.dds' if tex['type']==1 else '.png')
            shutil.copyfile(ORIG/'Models'/f,MODELS/f)
        audit[self.name]={'checked_wire_and_rail_caps':len(self.endpoints),'mesh_objects':len(meshes),'colliders':sum('collider' in n for _,n in nodes)}

def appearance(mass,cost):
    m=copy.deepcopy(next(n for n in template.children if n.get('name')=='ModulePartVariants'))
    for v in m.children:
        if v.header=='VARIANT' and v.get('name')!='Open':
            v.set('mass',round(mass*.25,4));v.set('cost',round(cost*.10))
    return m

def make_part(g,title,desc,mass,cost,ports,profiles,extra=(),scale=1):
    p=Node('PART:NEEDS[RoosterWorksStationSupport]',[(k,v) for k,v in template.values if not k.startswith('node_')])
    for k,v in dict(name=g.name,title='RoosterWorks '+title,description=desc,rescaleFactor=scale,mass=mass,cost=cost,entryCost=cost*3,category='Structural',attachRules='1,0,1,1,0',bulkheadProfiles=profiles,tags='roosterworks girder truss junction reducer adapter structural storage hub').items():p.set(k,v)
    for label,point,axis,size in ports:
        p.set('node_stack_'+label,', '.join(f'{v:g}' for v in (*point,*axis,size)))
    p.children=[Node('MODEL',[('model','RoosterWorksGirderExpansion/Models/'+g.name)]),Node('VABORGANIZER',[('organizerSubcategory','trusses')]),appearance(mass,cost),*extra]
    (PARTS/(g.name+'.cfg')).write_text(dump(p),encoding='utf-8')
    g.export()

def adapter(small,large,length,mass,cost):
    g=Girder(f'RWG_Reducer_{int(small*100)}_{int(large*100)}')
    angles=sorted({round((math.pi/2+i*math.tau/n)%math.tau,9) for n in (6 if small==1.25 else 8,8) for i in range(n)})
    low,high=-length/2,length/2
    levels=[(low+.055*large/2.5,large),(low+.19*large/2.5,large),(high-.19*small/2.5,small),(high-.055*small/2.5,small)]
    rings=[[pos(frame_radius(d,a),a,y) for a in angles] for y,d in levels]
    for k,(ring,(_,d)) in enumerate(zip(rings,levels)):g.rib(ring,.08*d/2.5,k in (0,3))
    for i,a in enumerate(angles):
        j=(i+1)%len(angles)
        for k in range(3):
            p,q=rings[k][i],rings[k+1][i]
            g.strut(p,q,.072*small/2.5,k==1)
            corners=[p,rings[k][j],rings[k+1][j],q]
            g.panel(corners)
            if k==1:
                g.strut(p,rings[2][j],.032*small/2.5);g.strut(rings[1][j],q,.032*small/2.5)
                bolt(g.frame,q,unit(pos(1,a,0)),.035*small/2.5)
    for a in lanes:
        for key,offset,r,thick in lines:
            t=a+offset
            path=[(low,large),levels[1],levels[2],(high,small)]
            conduit(g.frame[key],[pos(r*d/2.5,t,y) for y,d in path],[thick*d/2.5 for y,d in path],pos(1,t,0))
            for y,d in levels[1:3]:
                tube(g.frame['frame'],pos(frame_radius(d,t),t,y),pos(r*d/2.5,t,y),.017*d/2.5,8)
            for y,d in [(low,large),(high,small)]:g.endpoints.append((key,pos(r*d/2.5,t,y),Y,thick*d/2.5))
    sizes={1.25:1,2.5:2,3.75:3}
    ports=[('bottom',Y*low,-Y,sizes[large]),('top',Y*high,Y,sizes[small])]
    make_part(g,f'{small:g}–{large:g} m Girder Adapter','Tapered open truss with paired exterior service lanes and selectable white or grey armor.',mass,cost,ports,f'size{sizes[small]}, size{sizes[large]}')

def hub(diameter):
    scale=diameter/2.5
    g=Girder(f'RWG_Hub_{int(diameter*100)}');half=1.42;shoulder=1.19;radius=1.175
    axes=[(k,np.array(a,dtype=float)) for k,a in [('top',(0,1,0)),('bottom',(0,-1,0)),('right',(1,0,0)),('left',(-1,0,0)),('front',(0,0,1)),('back',(0,0,-1))]]
    faces={}
    for label,axis in axes:
        def radial(a):
            p=pos(1,a,0)
            if abs(axis[1])==1:return p
            k=np.cross(Y,axis)
            return np.cross(k,p)+k*np.dot(k,p)
        faces[label]=[axis*shoulder+radial(j*math.pi/4)*radius for j in range(8)]
        sides=6 if diameter==1.25 else 8
        angles=sorted({round((math.pi/2+j*math.tau/n)%math.tau,9) for n in (8,sides) for j in range(n)})
        rings=[[axis*shoulder+radial(a)*frame_radius(2.5,a) for a in angles],
               [axis*(half-.055)+radial(a)*frame_radius(diameter,a)/scale for a in angles]]
        g.rib(rings[0],.08);g.rib(rings[1],.09,True)
        for j in range(len(angles)):
            k=(j+1)%len(angles);g.strut(rings[0][j],rings[1][j],.07)
            g.panel([rings[0][j],rings[0][k],rings[1][k],rings[1][j]])
        for a in lanes:
            for key,delta,r,thick in lines:
                angle=a+(delta if abs(axis[1])==1 else -delta)
                direction=radial(angle);end=axis*half+direction*r
                p=axis*shoulder+direction*r
                tube(g.frame[key],p,end,thick,12)
                # Return into a socket fixed to the shoulder ring.
                seat=axis*shoulder+direction*frame_radius(2.5,angle)
                tube(g.frame[key],p,seat,thick,12)
                tube(g.frame['frame'],seat-direction*.015,seat+direction*.03,.026,10)
                g.endpoints.append((key,end,axis,thick))
    for (a,u),(b,v) in combinations(axes,2):
        if np.dot(u,v)!=0:continue
        w=np.cross(u,v)
        def edge(label,direction):
            near=sorted(faces[label],key=lambda p:-np.dot(p,direction))[:3]
            return sorted(near,key=lambda p:np.dot(p,w))
        x,z=edge(a,v),edge(b,u)
        for p,q in zip(x,z):g.strut(p,q,.085,True)
        for i in range(2):
            corners=[x[i],x[i+1],z[i+1],z[i]]
            g.panel(corners);g.strut(corners[0],corners[2],.045);g.strut(corners[1],corners[3],.045)
    for signs in product((-1,1),repeat=3):
        corner=np.array(signs)
        points=[max(faces[label],key=lambda p:np.dot(p,corner)) for label,axis in axes if np.dot(axis,corner)>0]
        g.panel(points)
    for name in ('Tank','Battery','Xenon'):
        batch=Batch();parent=node('RWG_'+name);g.model.root['children'].append(parent)
        if name=='Tank':vessel(batch,(0,0,0),.76,1.65)
        if name=='Battery':
            for y in (-.51,-.17,.17,.51):
                beam(batch['frame'],np.array((0,y-.145,0)),np.array((0,y+.145,0)),1.18,1.18)
                for a in (0,math.pi/2,math.pi,3*math.pi/2):plate(batch,pos(.593,a,y),(math.cos(a),0,-math.sin(a)),Y,.70,.22,.018,'black',0)
        if name=='Xenon':
            for j in range(4):vessel(batch,pos(.39,j*math.pi/2,0),.26,1.60)
        for j in range(4):
            a=j*math.pi/2
            beam(batch['steel'],pos(.45,a,0),pos(shoulder,a,.98),.085,.075)
            beam(batch['steel'],pos(shoulder,a,.98),pos(shoulder,a,radius),.085,.075)
        collider=node('RWG_'+name+'_Collider');collider['collider']=dict(type='box',trigger=0,size=(1.10,1.40,1.10),center=(0,0,0));parent['children'].append(collider)
        emit(g.model,parent,'RWG_'+name,batch)
    switch=Node('MODULE',[('name','ModuleB9PartSwitch'),('moduleID','HubStorage'),('switcherDescription','Storage'),('baseVolume',str(.5*scale**3)),('switchInFlight','false')])
    switch.children.append(Node('SUBTYPE',[('name','Empty'),('title','Empty Hub'),('defaultSubtypePriority','1')]))
    ref=next(n for n in template.children if n.get('moduleID')=='SupportStorage')
    for v in ref.children:
        key=v.get('name')
        if key in ('ServiceCore','Empty'):continue
        hardware='Battery' if key in ('Standard','Battery') else 'Xenon' if key=='Xenon' else 'Tank'
        label={'Standard':'ElectricCharge + Monopropellant','Battery':'Battery Only'}.get(key,v.get('title'))
        switch.children.append(Node('SUBTYPE',[('name',key),('title',label),('tankType',v.get('tankType')),('transform','RWG_'+hardware),('addedMass',str(.24*scale**3)),('addedCost',str(round(450*scale**3)))]))
    size={1.25:1,2.5:2,3.75:3}[diameter]
    make_part(g,f'{diameter:g} m Six-Way Girder Hub','Six girder ports with a hollow junction or a selectable battery or tank payload. Exterior armor switches independently.',round(1.30*scale**3,5),round(4800*scale**3),[(label,axis*half,axis,size) for label,axis in axes],f'size{size}',[switch],scale)

adapter(1.25,2.5,1.40,.33,1300)
adapter(2.5,3.75,1.65,.68,2500)
adapter(1.25,3.75,2.15,.74,2900)
for diameter in (1.25,2.5,3.75):hub(diameter)
shutil.copyfile(BASE/'LICENSE',GD/'LICENSE')
print(json.dumps(audit,indent=2))
