#!/usr/bin/env python3
"""RoosterWorks Kerbalism Additions: generate original KSP1 .mu parts without Blender.

Requires Pillow and NumPy. This script creates original textures, six models and part configs. No Near Future Construction assets, meshes or textures are used.
"""
from pathlib import Path
import math, struct, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
GD=ROOT/'GameData'/'RoosterWorksKerbalismAdditions'
MD=GD/'Models'; PD=GD/'Parts'
MD.mkdir(parents=True, exist_ok=True); PD.mkdir(parents=True, exist_ok=True)

class Mesh:
    def __init__(self): self.verts=[];self.normals=[];self.uv=[];self.tris=[]
    def add(self, p,n,uv):
        self.verts.append(tuple(map(float,p)));self.normals.append(tuple(map(float,n)));self.uv.append(tuple(map(float,uv)))
        return len(self.verts)-1
    def tri(self,a,b,c):self.tris.append((a,b,c))
    def merge(self,other):
        off=len(self.verts);self.verts+=other.verts;self.normals+=other.normals;self.uv+=other.uv
        self.tris += [tuple(x+off for x in t) for t in other.tris]

def normalize(v):
    d=math.sqrt(sum(x*x for x in v)) or 1
    return tuple(x/d for x in v)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,t):return tuple(x*t for x in a)

def solid_box(center,size,angle=0):
    cx,cy,cz=center;sx,sy,sz=[x/2 for x in size]
    verts=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    ca,sa=math.cos(angle),math.sin(angle)
    verts=[(cx+ca*x+sa*z,cy+y,cz-sa*x+ca*z) for x,y,z in verts]
    faces=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    m=Mesh()
    for face in faces:
        a,b,c,d=[verts[k] for k in reversed(face)]  # outward winding
        n=normalize(cross(sub(b,a),sub(c,a)))
        q=[m.add(v,n,uv) for v,uv in zip((a,b,c,d),((0,0),(1,0),(1,1),(0,1)))]
        m.tri(q[0],q[1],q[2]);m.tri(q[0],q[2],q[3])
    return m

def rod(a,b,r=0.035,sides=9):
    # low-poly sealed steel/bronze structural tubes; oriented between any 3D points
    axis=normalize(sub(b,a));basis=normalize(cross(axis,(1,0,0) if abs(axis[0])<0.9 else (0,0,1)))
    other=normalize(cross(axis,basis));m=Mesh();rs=[]
    for pos,v in [(a,0),(b,1)]:
        ring=[]
        for j in range(sides+1):
            theta=j*math.tau/sides
            n=add(mul(basis,math.cos(theta)),mul(other,math.sin(theta)))
            p=add(pos,mul(n,r));ring.append(m.add(p,n,(j/sides,v)))
        rs.append(ring)
    for j in range(sides):
        u,v,w,x=rs[0][j],rs[1][j],rs[0][j+1],rs[1][j+1]
        m.tri(u,v,w);m.tri(w,v,x)
    for yidx,(p,n) in enumerate(((a,mul(axis,-1)),(b,axis))):
        center=m.add(p,n,(.5,.5))
        row=rs[yidx]
        for j in range(sides):
            if yidx==0:m.tri(center,row[j+1],row[j])
            else:m.tri(center,row[j],row[j+1])
    return m

def closed_tank(cx,cz,y0,y1,r,sides=32):
    m=Mesh(); rings=[]
    for yy,v in [(y0,0),(y1,1)]:
        row=[]
        for j in range(sides+1):
            a=j*math.tau/sides;x=math.cos(a);z=math.sin(a)
            row.append(m.add((cx+r*x,yy,cz+r*z),(x,0,z),(j/sides,v)))
        rings.append(row)
    for j in range(sides):
        a,b,c,d=rings[0][j],rings[1][j],rings[0][j+1],rings[1][j+1]
        m.tri(a,b,c);m.tri(c,b,d)
    for yy,ny in ((y0,-1),(y1,1)):
        center=m.add((cx,yy,cz),(0,ny,0),(.5,.5))
        rim=[]
        for j in range(sides):
            a=j*math.tau/sides;co,si=math.cos(a),math.sin(a)
            rim.append(m.add((cx+r*co,yy,cz+r*si),(0,ny,0),(.5+.5*co,.5+.5*si)))
        for j in range(sides):
            k=(j+1)%sides
            if ny<0:m.tri(center,rim[j],rim[k])
            else:m.tri(center,rim[k],rim[j])
    return m

def label_quad(angle,radius,y,width=.65,height=.17,offset=.012):
    # Two explicit faces with independent UVs so the RoosterWorks badge reads correctly
    # from both sides and no face accidentally reuses mirrored winding.
    dx,dz=math.cos(angle),math.sin(angle);tx,tz=dz,-dx
    center=(radius*dx,y,radius*dz)
    def quad(side_sign, flip_u=False):
        n=(dx*side_sign,0,dz*side_sign)
        cx,cy,cz=(center[0]+n[0]*offset,center[1],center[2]+n[2]*offset)
        p0=(cx-width/2*tx,cy-height/2,cz-width/2*tz)
        p1=(cx+width/2*tx,cy-height/2,cz+width/2*tz)
        p2=(cx+width/2*tx,cy+height/2,cz+width/2*tz)
        p3=(cx-width/2*tx,cy+height/2,cz-width/2*tz)
        return (n,[p0,p1,p2,p3],([(1,1),(0,1),(0,0),(1,0)] if flip_u else [(0,1),(1,1),(1,0),(0,0)]))
    m=Mesh()
    for n,pts,uvs in (quad(1,False), quad(-1,True)):
        ids=[m.add(p,n,uv) for p,uv in zip(pts,uvs)]
        if n[0]*dx + n[2]*dz > 0:
            m.tri(ids[0],ids[1],ids[2]);m.tri(ids[0],ids[2],ids[3])
        else:
            m.tri(ids[2],ids[1],ids[0]);m.tri(ids[3],ids[2],ids[0])
    return m

def panel_between(a,b,yl,yh,shade_offset=.967):
    """A double-sided steel panel just behind the main perimeter rails."""
    (ax,az),(bx,bz)=a,b
    cx,cz=(ax+bx)/2,(az+bz)/2
    # Cover almost the entire face; only the main rails remain exposed.
    ax,az=cx+(ax-cx)*.97,cz+(az-cz)*.97
    bx,bz=cx+(bx-cx)*.97,cz+(bz-cz)*.97
    ax,az,bx,bz=ax*shade_offset,az*shade_offset,bx*shade_offset,bz*shade_offset
    normal=normalize((cx,0,cz))
    pts=[(ax,yl,az),(bx,yl,bz),(bx,yh,bz),(ax,yh,az)]
    m=Mesh()
    for side in (1,-1):
        n=mul(normal,side)
        ids=[m.add(v,n,uv) for v,uv in zip(pts,((0,0),(1,0),(1,1),(0,1)))]
        if side==1:
            m.tri(ids[0],ids[1],ids[2]);m.tri(ids[0],ids[2],ids[3])
        else:
            m.tri(ids[2],ids[1],ids[0]);m.tri(ids[3],ids[2],ids[0])
    return m


def octagonal_radius(theta,r):
    """Radius where ray at theta meets an exact regular octagon with circumradius r."""
    sector=math.tau/8
    face_normal=round((theta-sector/2)/sector)*sector+sector/2
    return r*math.cos(math.pi/8)/math.cos(theta-face_normal)


def adapter_shell(r_oct=1.175,r_round=1.25,y0=-.37,y1=.37,n=64):
    """A gentle external transition from octagonal girder ring to 2.5-m circular profile."""
    mesh=Mesh()
    rows=[]
    for yy,phase,v in [(y0,0,0),(0,0.50,.5),(y1,1,1)]:
        ring=[]
        for j in range(n+1):
            a=math.tau*j/n
            radius=octagonal_radius(a,r_oct)*(1-phase)+r_round*phase
            pos=(radius*math.cos(a),yy,radius*math.sin(a))
            ring.append(mesh.add(pos,(math.cos(a),0,math.sin(a)),(j/n,v)))
        rows.append(ring)
    for k in range(len(rows)-1):
        for j in range(n):
            a,b=rows[k][j],rows[k+1][j]
            c,d=rows[k][j+1],rows[k+1][j+1]
            mesh.tri(a,b,c);mesh.tri(c,b,d)
    return mesh


def polygonal_radius(theta,r,npoly):
    """Radius of a regular polygon face intersected by a radial ray."""
    sector=math.tau/npoly
    normal=round((theta-sector/2)/sector)*sector+sector/2
    return r*math.cos(math.pi/npoly)/math.cos(theta-normal)


def polygon_to_round_shell(npoly,poly_radius,circle_radius,y0,y1,n=60):
    mesh=Mesh();rows=[]
    for yy,progress in ((y0,0),(0,.5),(y1,1)):
        ring=[]
        for j in range(n+1):
            theta=math.tau*j/n
            r=polygonal_radius(theta,poly_radius,npoly)*(1-progress)+circle_radius*progress
            ring.append(mesh.add((r*math.cos(theta),yy,r*math.sin(theta)),
                                 (math.cos(theta),0,math.sin(theta)),(j/n,progress)))
        rows.append(ring)
    for k in range(2):
        for j in range(n):
            a,b=rows[k][j],rows[k+1][j]
            c,d=rows[k][j+1],rows[k+1][j+1]
            mesh.tri(a,b,c);mesh.tri(c,b,d)
    return mesh


def polygon_end_plate(y,outer_radius,npoly,inner_radius=.17,n=60):
    m=Mesh()
    for ny in (1,-1):
        inner=[];outer=[]
        for j in range(n):
            theta=math.tau*j/n
            inner.append(m.add((inner_radius*math.cos(theta),y,inner_radius*math.sin(theta)),
                               (0,ny,0),(.5,.5)))
            r=polygonal_radius(theta,outer_radius,npoly) if npoly else outer_radius
            outer.append(m.add((r*math.cos(theta),y,r*math.sin(theta)),(0,ny,0),(1,1)))
        for j in range(n):
            k=(j+1)%n
            if ny==1:
                m.tri(inner[j],outer[j],outer[k]);m.tri(inner[j],outer[k],inner[k])
            else:
                m.tri(outer[k],outer[j],inner[j]);m.tri(inner[k],outer[k],inner[j])
    return m


def adapter_end_annulus(y,inner=.34,octagon=False,n=64):
    """Reinforced end plate around a central service opening."""
    m=Mesh()
    rings=[]
    for radfunc in (lambda a: inner,lambda a: octagonal_radius(a,1.175) if octagon else 1.25):
        row=[]
        for j in range(n):
            theta=j*math.tau/n
            r=radfunc(theta)
            row.append((r*math.cos(theta),y,r*math.sin(theta)))
        rings.append(row)
    for up in (1,-1):
        inside=[m.add(point,(0,up,0),(0,0)) for point in rings[0]]
        outside=[m.add(point,(0,up,0),(1,1)) for point in rings[1]]
        for j in range(n):
            k=(j+1)%n
            if up==1:
                m.tri(inside[j],outside[j],outside[k]);m.tri(inside[j],outside[k],inside[k])
            else:
                m.tri(outside[k],outside[j],inside[j]);m.tri(inside[k],outside[k],inside[j])
    return m


def ring_beams(mesh,r,y,octagonal=False,tube=.045,sides=24):
    verts=[]
    count=8 if octagonal else sides
    for j in range(count):
        t=math.tau*j/count
        verts.append((r*math.cos(t),y,r*math.sin(t)))
    for j in range(count):mesh.merge(rod(verts[j],verts[(j+1)%count],tube,8))


class Binary:
    def __init__(self,path): self.fh=open(path,'wb')
    def close(self):self.fh.close()
    def i(self,*vs): self.fh.write(struct.pack('<'+'i'*len(vs),*vs))
    def f(self,*vs): self.fh.write(struct.pack('<'+'f'*len(vs),*vs))
    def b(self,v):self.fh.write(bytes([v]))
    def string(self,s):
        bb=s.encode('utf8');n=len(bb)
        while n>=128:self.b((n&127)|128);n>>=7
        self.b(n);self.fh.write(bb)
    def xyz(self,v):self.f(*v)

def transform(w,name,pos=(0,0,0),mesh=None,mat=0,collider=None):
    w.string(name);w.xyz(pos);w.f(0,0,0,1);w.xyz((1,1,1))
    w.i(24);w.string('Untagged');w.i(0)
    if collider:
        w.i(28);w.b(0);w.xyz(collider);w.xyz((0,0,0))
    if mesh:
        assert len(mesh.verts)<65000
        w.i(7);w.i(13,len(mesh.verts),1);w.i(14)
        for v in mesh.verts:w.xyz(v)
        w.i(15)
        for v in mesh.uv:w.f(*v)
        w.i(17)
        for v in mesh.normals:w.xyz(v)
        w.i(19,len(mesh.tris)*3)
        for tri in mesh.tris:w.i(*tri)
        w.i(22);w.i(8);w.b(1);w.b(1);w.i(1,mat)

def child(w,name,mesh,mat=0,collider=None):
    w.i(0);transform(w,name,mesh=mesh,mat=mat,collider=collider);w.i(1)

def material_textures():
    rng=np.random.default_rng(2026)
    names=[]
    def create(name,base,size=1024,pattern=None):
        a=np.zeros((size,size,3),dtype=np.float64)
        n=rng.normal(0,2.0,(size,size))
        soft=np.sin(np.arange(size)[:,None]*.055)*1.2 + np.cos(np.arange(size)[None,:]*.047)*0.9
        for i,v in enumerate(base):a[:,:,i]=v+n+soft
        im=Image.fromarray(np.uint8(np.clip(a,0,255)),'RGB');d=ImageDraw.Draw(im)
        if pattern:pattern(d,size)
        im.save(MD/(name+'.png'),optimize=True);names.append(name)
    def frame(d,s):
        for t in range(0,s,96):d.line([(0,t),(s,t)],fill=(92,103,113),width=2)
        for t in range(48,s,96):d.line([(0,t),(s,t)],fill=(72,84,94),width=1)
        for t in range(34,s,160):d.line([(t,0),(t,s)],fill=(52,61,70),width=2)
    def ceramic(d,s):
        for t in range(0,s,136):d.line([(0,t),(s,t)],fill=(172,180,184),width=2)
        for t in range(68,s,136):d.line([(0,t),(s,t)],fill=(236,236,230),width=1)
    def batteries(d,s):
        for x in range(18,s,132):
            for y in range(18,s,132):
                d.rounded_rectangle((x,y,x+96,y+96),radius=8,fill=(43,54,66),outline=(102,116,128),width=2)
                for a in range(16,86,18):d.line((x+12,y+a,x+84,y+a),fill=(79,96,113),width=2)
                d.ellipse((x+76,y+76,x+84,y+84),fill=(76,194,203))
    def gold(d,s):
        for t in range(10,s,72):
            d.line((0,t,s,t),fill=(232,177,92),width=2)
            d.line((0,t+4,s,t+4),fill=(121,80,46),width=2)
    def copper(d,s):
        for t in range(0,s,42):d.line((t,0,t,s),fill=(148,101,67),width=2)
    create('frame',(82,91,100),pattern=frame)
    create('tank',(216,220,217),pattern=ceramic)
    create('battery',(47,58,70),pattern=batteries)
    create('bronze',(177,123,63),pattern=gold)
    create('copper',(162,106,71),pattern=copper)
    im=Image.new('RGB',(1536,360),(28,41,53));d=ImageDraw.Draw(im)
    d.rounded_rectangle((8,8,1527,351),radius=22,outline=(225,170,82),width=10)
    d.rectangle((46,48,59,311),fill=(235,170,75))
    heavy='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    f1=ImageFont.truetype(heavy,115);f2=ImageFont.truetype(reg,56)
    d.text((100,36),'RoosterWorks',font=f1,fill=(236,238,241))
    d.text((108,207),'KERBALISM ADDITIONS',font=f2,fill=(226,171,91))
    # Counteract the in-game mirrored sampling seen in prior tests.
    im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    im.save(MD/'branding.png',optimize=True);names.append('branding')
    return names

PARTS=[
    dict(id='RW_OctoSupport_XL',title='RoosterWorks Octo Support Girder XL',polygon=8,diameter=2.5,height=4.75,mono=1500,ec=9000,tanks=4,battery=8,tech='specializedConstruction',mass=3.2,cost=12900,entry=19600,profile='size2',node=2),
    dict(id='RW_OctoSupport_Medium',title='RoosterWorks Octo Support Girder Medium',polygon=8,diameter=2.5,height=2.65,mono=750,ec=4500,tanks=2,battery=4,tech='specializedConstruction',mass=1.85,cost=7900,entry=12900,profile='size2',node=2),
    dict(id='RW_HexSupport_Long',title='RoosterWorks Hex Support Girder Long',polygon=6,diameter=1.25,height=3.15,mono=200,ec=1200,tanks=2,battery=4,tech='advConstruction',mass=.76,cost=2850,entry=5200,profile='size1',node=1),
    dict(id='RW_HexSupport_Medium',title='RoosterWorks Hex Support Girder Medium',polygon=6,diameter=1.25,height=1.75,mono=100,ec=600,tanks=1,battery=2,tech='advConstruction',mass=.42,cost=1650,entry=3100,profile='size1',node=1),
]

def build_part(p):
    poly=p['polygon'];rad=p['diameter']*.5*.94;h=p['height'];half=h/2
    circum=[(rad*math.cos(j*math.tau/poly),rad*math.sin(j*math.tau/poly)) for j in range(poly)]
    mats=[Mesh() for _ in range(6)]
    armor=Mesh()
    thick=.088 if rad>.8 else .058
    rail_sides=14 if rad>.8 else 12
    diag_sides=12 if rad>.8 else 10
    for k,(x,z) in enumerate(circum):
        nx,nz=circum[(k+1)%poly]
        mats[0].merge(rod((x,-half,z),(x,half,z),thick,rail_sides))
        for sy in (-half,half):
            mats[0].merge(rod((x,sy,z),(nx,sy,nz),thick*.96,rail_sides))
            mats[3].merge(solid_box((x,sy*.964,z),(.18,.12,.18) if rad>.8 else (.12,.08,.12)))
        if k%2==0:
            mats[0].merge(rod((x,-half*.80,z),(nx,half*.80,nz),thick*.48,diag_sides))
        else:
            mats[0].merge(rod((x,half*.80,z),(nx,-half*.80,nz),thick*.48,diag_sides))
        mats[0].merge(rod((x,0,z),(nx,0,nz),thick*.68,diag_sides))
        panel_bottom=-half+.040
        panel_top=half-.040
        armor.merge(panel_between((x,z),(nx,nz),panel_bottom,panel_top,shade_offset=.979))
    for y in (-half*.92,half*.92):
        for k,(x,z) in enumerate(circum):
            nx,nz=circum[(k+1)%poly]
            mats[3].merge(rod((x*.95,y,z*.95),(nx*.95,y,nz*.95),.024 if rad>.8 else .017,10))
    for y0 in (-half+.065,half-.065):
        for k,(x,z) in enumerate(circum):
            nx,nz=circum[(k+1)%poly]
            mats[0].merge(rod((x*.64,y0,z*.64),(nx*.64,y0,nz*.64),.036 if rad>.8 else .024,10))
    mats[0].merge(solid_box((0,0,0),(.20,h*.80,.20) if rad>.8 else (.12,h*.80,.12)))
    # Monopropellant vessels: almost full height, thicker per request, with cleaner fittings.
    tank_positions=[]
    if p['tanks']==4:
        tank_positions=[(.42*rad*math.cos(math.tau*j/4+.20),.42*rad*math.sin(math.tau*j/4+.20)) for j in range(4)]
    elif p['tanks']==2:
        tank_positions=[(-rad*.28,0),(rad*.28,0)]
    else:
        tank_positions=[(0,0)]
    base_r=rad*(.18 if p['tanks']>=4 else .25 if p['tanks']==2 else .30)
    t_r=base_r*1.5
    max_r=(rad*math.cos(math.pi/poly)-0.09)
    if p['tanks']>=4:
        max_center=max(math.sqrt(x*x+z*z) for x,z in tank_positions)
        t_r=min(t_r,max_r-max_center)
    elif p['tanks']==2:
        max_center=max(abs(x) for x,z in tank_positions)
        t_r=min(t_r,max_r-max_center)
    else:
        t_r=min(t_r,max_r)
    ylo=-half+.12 if rad>.8 else -half+.08
    yhi=half-.12 if rad>.8 else half-.08
    for x,z in tank_positions:
        mats[1].merge(closed_tank(x,z,ylo,yhi,t_r,32 if rad>.8 else 28))
        for yy in (ylo+.045,yhi-.045,(ylo+yhi)/2):
            mats[3].merge(rod((x-t_r*1.02,yy,z),(x+t_r*1.02,yy,z),.015 if rad>.8 else .010,12))
        mats[4].merge(rod((x,ylo,z),(0,-half+.070,0),.012 if rad>.8 else .008,10))
        mats[4].merge(rod((x,yhi,z),(0,half-.070,0),.012 if rad>.8 else .008,10))
        mats[3].merge(solid_box((x,ylo-.035,z),(.13,.055,.13) if rad>.8 else (.075,.038,.075)))
        mats[3].merge(solid_box((x,yhi+.035,z),(.13,.055,.13) if rad>.8 else (.075,.038,.075)))
    # Battery banks: continuous vertical wall modules mounted flush to polygon faces.
    face_apothem=rad*math.cos(math.pi/poly)
    face_width=2*rad*math.sin(math.pi/poly)
    n_battery=p['battery']
    unique_faces=min(poly,n_battery)
    face_ids=sorted({int(round(i*poly/unique_faces))%poly for i in range(unique_faces)})
    if len(face_ids)<unique_faces:
        face_ids=list(range(0,poly,max(1,poly//unique_faces)))[:unique_faces]
    for face_id in face_ids:
        theta=(face_id+.5)*math.tau/poly
        angle=math.pi/2-theta
        inward=face_apothem-(.11 if rad>.8 else .07)
        x,z=inward*math.cos(theta),inward*math.sin(theta)
        wid=face_width*.70
        pack_h=h*.84 if rad>.8 else h*.82
        thickness=.10 if rad>.8 else .062
        mats[2].merge(solid_box((x,0,z),(wid,pack_h,thickness),angle=angle))
        tang=(math.sin(theta),-math.cos(theta))
        for side in (-1,1):
            offset=wid*.46*side
            px,pz=x+offset*tang[0],z+offset*tang[1]
            mats[3].merge(rod((px,-pack_h*.50,pz),(px,pack_h*.50,pz),.011 if rad>.8 else .007,8))
        mats[4].merge(rod((x,-pack_h*.52,z),(x,-half+.11,z),.010 if rad>.8 else .006,8))
        mats[4].merge(rod((x,pack_h*.52,z),(x,half-.11,z),.010 if rad>.8 else .006,8))
    tagAngle=math.pi/poly
    mats[5].merge(label_quad(tagAngle,rad*math.cos(math.pi/poly)*.994, min(h*.13,.28),width=rad*.80,height=min(h*.15,.27)))
    w=Binary(MD/(p['id']+'.mu'));w.i(76543,5);w.string(p['id']);transform(w,'RoosterWorksGirder')
    for k,(name,mesh) in enumerate(zip(['Frame','MonopropellantVessels','BatteryPacks','BronzeClamps','FluidLines','RoosterWorksBrand'],mats)):
        assert mesh.tris, name
        child(w,name,mesh,k)
    child(w,'ArmorPanels',armor,1)
    for k,(x,z) in enumerate(circum):
        w.i(0);transform(w,f'RailCollider_{k:02}',pos=(x,0,z),collider=(.20 if rad>.8 else .13,h,.20 if rad>.8 else .13));w.i(1)
    w.i(0);transform(w,'EquipmentCollider',collider=(rad*.92,h*.72,rad*.92));w.i(1)
    write_materials(w)
    w.close()
    return mats,armor

def part_config(p):
    h=p['height'];desc=('A dedicated RoosterWorks Kerbalism Addition. Original '+('octagonal' if p['polygon']==8 else 'hexagonal')+
        ' structural support girder with visible internal monopropellant pressure vessels and fixed battery banks. '+
        'Liquid configuration switching removed; ElectricCharge and MonoPropellant are stored as permanent resources '+
        'for persistent support during long-duration missions.')
    name=p['id'];return f'''PART
{{
    name = {name}
    module = Part
    author = SockedRooster
    MODEL
    {{
        model = RoosterWorksKerbalismAdditions/Models/{name}
    }}
    rescaleFactor = 1
    node_stack_top = 0, {h/2:.4f}, 0, 0, 1, 0, {p['node']}
    node_stack_bottom = 0, {-h/2:.4f}, 0, 0, -1, 0, {p['node']}
    TechRequired = {p['tech']}
    entryCost = {p['entry']}
    cost = {p['cost']}
    category = Structural
    subcategory = 0
    VABORGANIZER
    {{
        organizerSubcategory = trusses
    }}
    title = {p['title']} - Kerbalism Addition
    manufacturer = RoosterWorks
    description = {desc} Optional external armor panels can be selected in the VAB without changing storage capacity.
    attachRules = 1,0,1,1,0
    bulkheadProfiles = {p['profile']}
    tags = roosterworks kerbalism support persistent electriccharge monopropellant battery girder truss station
    mass = {p['mass']}
    dragModelType = default
    maximum_drag = 0.2
    minimum_drag = 0.2
    angularDrag = 2
    crashTolerance = 18
    breakingForce = 200
    breakingTorque = 200
    maxTemp = 2200
    skinMaxTemp = 2600
    fuelCrossFeed = True
    MODULE
    {{
        name = ModulePartVariants
        baseVariant = Open
        useMultipleDragCubes = false
        VARIANT
        {{
            name = Open
            displayName = Open Frame
            primaryColor = #485763
            secondaryColor = #C18B49
            GAMEOBJECTS
            {{
                ArmorPanels = false
            }}
        }}
        VARIANT
        {{
            name = Armored
            displayName = Armored Panels
            primaryColor = #D5D9D5
            secondaryColor = #C18B49
            GAMEOBJECTS
            {{
                ArmorPanels = true
            }}
        }}
    }}
    RESOURCE
    {{
        name = ElectricCharge
        amount = {p['ec']}
        maxAmount = {p['ec']}
    }}
    RESOURCE
    {{
        name = MonoPropellant
        amount = {p['mono']}
        maxAmount = {p['mono']}
    }}
}}
'''

def build_adapter():
    name='RW_Octo25_Adapter';height=.74
    mats=[Mesh() for _ in range(6)]
    mats[1].merge(adapter_shell())
    mats[0].merge(adapter_end_annulus(-height/2,octagon=True))
    mats[0].merge(adapter_end_annulus(height/2,octagon=False))
    ring_beams(mats[0],1.175,-height/2,octagonal=True,tube=.075)
    ring_beams(mats[0],1.25,height/2,octagonal=False,tube=.070)
    ring_beams(mats[3],1.15,-height/2+.055,octagonal=True,tube=.021)
    ring_beams(mats[3],1.23,height/2-.045,octagonal=False,tube=.021)
    # Recessed central maintenance bus is original artwork, not a resource tank.
    mats[0].merge(solid_box((0,0,0),(.55,.6,.55)))
    mats[2].merge(solid_box((0,.05,0),(.46,.33,.46)))
    for k in range(8):
        a=math.tau*(k+.5)/8
        x,z=1.02*math.cos(a),1.02*math.sin(a)
        mats[3].merge(solid_box((x,-.24,z),(.11,.10,.11)))
        mats[4].merge(rod((x,-.28,z),(x*.90,.24,z*.90),.012,8))
    mats[5].merge(label_quad(math.pi/8,1.22,0,width=.50,height=.12))
    w=Binary(MD/(name+'.mu'));w.i(76543,5);w.string(name);transform(w,'RWAdapterRoot')
    for k,(obj,mesh) in enumerate(zip(['AdapterFrame','AdapterFairing','AdapterServiceBay','AdapterRims','AdapterLines','RoosterWorksBrand'],mats)):
        assert mesh.tris,obj
        child(w,obj,mesh,k)
    # Rigid inset approximate collider, avoids creating an interference at the stack nodes.
    w.i(0);transform(w,'AdapterCollider',collider=(2.04,.63,2.04));w.i(1)
    write_materials(w)
    w.close()
    config=f"""PART
{{
    name = {name}
    module = Part
    author = SockedRooster
    MODEL
    {{
        model = RoosterWorksKerbalismAdditions/Models/{name}
    }}
    rescaleFactor = 1
    node_stack_top = 0, 0.3700, 0, 0, 1, 0, 2
    node_stack_bottom = 0, -0.3700, 0, 0, -1, 0, 2
    TechRequired = specializedConstruction
    entryCost = 6000
    cost = 1750
    category = Structural
    subcategory = 0
    VABORGANIZER
    {{
        organizerSubcategory = adapters
    }}
    title = RoosterWorks Octo to 2.5m Stack Adapter - Kerbalism Addition
    manufacturer = RoosterWorks
    description = Original RoosterWorks rigid octagonal-girder to round 2.5-meter stack adapter. Two size2 stack nodes, no storage resources or fuel switching.
    attachRules = 1,0,1,1,0
    bulkheadProfiles = size2
    tags = roosterworks octo round 2.5 adapter girder station structural
    mass = 0.28
    dragModelType = default
    maximum_drag = 0.2
    minimum_drag = 0.2
    angularDrag = 2
    crashTolerance = 18
    breakingForce = 230
    breakingTorque = 230
    maxTemp = 2200
    skinMaxTemp = 2600
    fuelCrossFeed = True
}}
"""
    (PD/(name+'.cfg')).write_text(config)
    return mats


def build_hex_adapter():
    """Original six-sided 1.25m girder to round 1.25m spacecraft stack adapter."""
    name='RW_Hex125_Adapter'; height=.56
    r_hex=.5875;r_round=.625;half=height/2
    mats=[Mesh() for _ in range(6)]
    mats[1].merge(polygon_to_round_shell(6,r_hex,r_round,-half,half))
    mats[0].merge(polygon_end_plate(-half,r_hex,6))
    mats[0].merge(polygon_end_plate(half,r_round,None))
    # Hex lower ring and circular upper ring, different shapes on opposite faces.
    ring_beams(mats[0],r_hex,-half,octagonal=False,tube=.043,sides=6)
    ring_beams(mats[0],r_round,half,octagonal=False,tube=.04,sides=24)
    ring_beams(mats[3],r_hex*.94,-half+.04,octagonal=False,tube=.015,sides=6)
    ring_beams(mats[3],r_round*.94,half-.04,octagonal=False,tube=.015,sides=24)
    mats[0].merge(solid_box((0,0,0),(.26,.43,.26)))
    mats[2].merge(solid_box((0,.03,0),(.30,.20,.30)))
    for j in range(6):
        ang=(j+.5)*math.tau/6
        x,z=.47*math.cos(ang),.47*math.sin(ang)
        mats[3].merge(solid_box((x,-.18,z),(.065,.065,.065)))
        mats[4].merge(rod((x,-.19,z),(x*.95,.19,z*.95),.007,8))
    mats[5].merge(label_quad(math.pi/6,.605,0,width=.28,height=.09))
    w=Binary(MD/(name+'.mu'));w.i(76543,5);w.string(name);transform(w,'RWAdapterRoot')
    for k,(obj,mesh) in enumerate(zip(['AdapterFrame','AdapterFairing','AdapterServiceBay','AdapterRims','AdapterLines','RoosterWorksBrand'],mats)):
        assert mesh.tris,obj
        child(w,obj,mesh,k)
    w.i(0);transform(w,'AdapterCollider',collider=(.97,.44,.97));w.i(1)
    write_materials(w);w.close()
    cfg=f"""PART
{{
    name = {name}
    module = Part
    author = SockedRooster
    MODEL
    {{
        model = RoosterWorksKerbalismAdditions/Models/{name}
    }}
    rescaleFactor = 1
    node_stack_top = 0, {half:.4f}, 0, 0, 1, 0, 1
    node_stack_bottom = 0, {-half:.4f}, 0, 0, -1, 0, 1
    TechRequired = advConstruction
    entryCost = 2700
    cost = 850
    category = Structural
    subcategory = 0
    VABORGANIZER
    {{
        organizerSubcategory = adapters
    }}
    title = RoosterWorks Hex to 1.25m Stack Adapter - Kerbalism Addition
    manufacturer = RoosterWorks
    description = Original RoosterWorks hexagonal-girder to round 1.25-meter stack adapter. Two size1 stack nodes; no fuel or ElectricCharge storage.
    attachRules = 1,0,1,1,0
    bulkheadProfiles = size1
    tags = roosterworks hex round 1.25 adapter girder station structural
    mass = 0.14
    dragModelType = default
    maximum_drag = 0.2
    minimum_drag = 0.2
    angularDrag = 2
    crashTolerance = 18
    breakingForce = 160
    breakingTorque = 160
    maxTemp = 2200
    skinMaxTemp = 2600
    fuelCrossFeed = True
}}
"""
    (PD/(name+'.cfg')).write_text(cfg)
    return mats


def write_materials(w):
    names=['frame','tank','battery','bronze','copper','branding']
    w.i(10,len(names))
    for i,nam in enumerate(['RWSpaceframe','RWCeramicPressure','RWPowerCell','RWAnodizedBronze','RWPiping','RWMarkings']):
        w.string(nam);w.string('KSP/Diffuse');w.i(2)
        w.string('_Color');w.i(0);w.f(1,1,1,1)
        w.string('_MainTex');w.i(4,i);w.f(1,1);w.f(0,0)
    w.i(12,len(names))
    for t in names:w.string(t);w.i(0)


def run():
    material_textures()
    for p in PARTS:
        meshes,panels=build_part(p)
        (PD/(p['id']+'.cfg')).write_text(part_config(p))
        print(p['id'],'triangles',[len(m.tris) for m in meshes],
              'panel triangles',len(panels.tris), 'EC',p['ec'],'Mono',p['mono'])
    adapter=build_adapter()
    print('RW_Octo25_Adapter','triangles',[len(m.tris) for m in adapter])
    hex_adapter=build_hex_adapter()
    print('RW_Hex125_Adapter','triangles',[len(m.tris) for m in hex_adapter])

if __name__=='__main__':run()
