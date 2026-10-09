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

def closed_tank(cx,cz,y0,y1,r,sides=20):
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

def label_quad(angle,radius,y,width=.65,height=.17):
    # Radially-mounted panel at the outward face, with a readable dedicated UV.
    dx,dz=math.cos(angle),math.sin(angle);tx,tz=dz,-dx
    pts=[]
    for side,yy,u,v in [(-1,y-height/2,0,0),(1,y-height/2,1,0),
                        (1,y+height/2,1,1),(-1,y+height/2,0,1)]:
        pts.append((radius*dx +side*width/2*tx, yy, radius*dz+side*width/2*tz))
    m=Mesh(); n=(dx,0,dz)
    ids=[m.add(p,n,uv) for p,uv in zip(pts,[(1,1),(0,1),(0,0),(1,0)])]
    m.tri(ids[0],ids[1],ids[2]);m.tri(ids[0],ids[2],ids[3])
    # Mirror UV axes to correct in-game reversed/upright RoosterWorks lettering.
    # Second face protects against in-game backface winding variation
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
    def create(name,base,size=512,pattern=None):
        a=np.zeros((size,size,3),dtype=np.float64)
        n=rng.normal(0,3.8,(size,size))
        streak=np.sin(np.arange(size)[:,None]*.16)*2.6
        for i,v in enumerate(base):a[:,:,i]=v+n+streak
        im=Image.fromarray(np.uint8(np.clip(a,0,255)),'RGB');d=ImageDraw.Draw(im)
        if pattern:pattern(d,size)
        im.save(MD/(name+'.png'),optimize=True);names.append(name)
    def frame(d,s):
        for t in range(0,s,64):d.line([(0,t),(s,t)],fill=(89,100,111),width=2)
        for t in range(28,s,96):d.line([(t,0),(t,s)],fill=(40,47,55),width=3)
    def ceramic(d,s):
        for t in range(0,s,112):d.line([(0,t),(s,t)],fill=(161,171,176),width=3)
        for t in range(52,s,112):d.line([(0,t),(s,t)],fill=(249,245,235),width=2)
    def batteries(d,s):
        for x in range(18,s,128):
            for y in range(18,s,128):
                d.rounded_rectangle((x,y,x+93,y+93),radius=6,fill=(39,50,60),outline=(108,122,133),width=3)
                for a in range(16,85,17):d.line((x+12,y+a,x+80,y+a),fill=(71,89,108),width=3)
                d.ellipse((x+72,y+72,x+81,y+81),fill=(76,194,203))
    def gold(d,s):
        for t in range(8,s,58):
            d.line((0,t,s,t),fill=(243,180,93),width=3)
            d.line((0,t+5,s,t+5),fill=(100,66,36),width=3)
    def copper(d,s):
        for t in range(0,s,28):d.line((t,0,t,s),fill=(153,103,63),width=2)
    create('frame',(78,87,97),pattern=frame)
    create('tank',(212,216,213),pattern=ceramic)
    create('battery',(48,57,68),pattern=batteries)
    create('bronze',(177,123,63),pattern=gold)
    create('copper',(162,106,71),pattern=copper)
    # Branding is a real 2D asset on a mesh, not text assembled from external fonts
    im=Image.new('RGB',(1536,360),(28,41,53));d=ImageDraw.Draw(im)
    d.rounded_rectangle((8,8,1527,351),radius=22,outline=(225,170,82),width=10)
    d.rectangle((46,48,59,311),fill=(235,170,75))
    heavy='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    f1=ImageFont.truetype(heavy,115);f2=ImageFont.truetype(reg,56)
    d.text((100,36),'RoosterWorks',font=f1,fill=(236,238,241))
    d.text((108,207),'KERBALISM ADDITIONS',font=f2,fill=(226,171,91))
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
    # Heavy primary rails and clear, simplified cross-bracing.
    armor=Mesh()
    thick=.085 if rad>.8 else .053
    for k,(x,z) in enumerate(circum):
        nx,nz=circum[(k+1)%poly]
        mats[0].merge(rod((x,-half,z),(x,half,z),thick,10))
        for sy in (-half,half):
            mats[0].merge(rod((x,sy,z),(nx,sy,nz),thick*.93,10))
            mats[3].merge(solid_box((x,sy*.964,z),(.22,.14,.22) if rad>.8 else (.14,.09,.14)))
        # One major diagonal brace per face instead of overlapping X braces.
        if k%2==0:
            mats[0].merge(rod((x,-half*.78,z),(nx,half*.78,nz),thick*.52,9))
        else:
            mats[0].merge(rod((x,half*.78,z),(nx,-half*.78,nz),thick*.52,9))
        mats[0].merge(rod((x,0,z),(nx,0,nz),thick*.70,9))
        # Panel-clad truss: continuous full-height armor from lower to upper frame.
        # Three adjoining plates create manufacturing seams, without the old open belt.
        panel_bottom=-half+.043
        panel_top=half-.043
        stops=[panel_bottom, -h/6, h/6, panel_top]
        for q in range(3):
            armor.merge(panel_between((x,z),(nx,nz),stops[q],stops[q+1],shade_offset=.975))
    # Visible bronze collars and thicker end fittings.
    for y in (-half*.92,half*.92):
        for k,(x,z) in enumerate(circum):
            nx,nz=circum[(k+1)%poly]
            mats[3].merge(rod((x*.95,y,z*.95),(nx*.95,y,nz*.95),.028 if rad>.8 else .018,8))
    # Two distinct polyhedral solid end rings, inner frame support
    for y0 in (-half+.065,half-.065):
        for k,(x,z) in enumerate(circum):
            nx,nz=circum[(k+1)%poly]
            mats[0].merge(rod((x*.64,y0,z*.64),(nx*.64,y0,nz*.64),.033 if rad>.8 else .02,8))
    # central service bus, visible between tanks
    mats[0].merge(solid_box((0,0,0),(.23,h*.75,.23) if rad>.8 else (.13,h*.76,.13)))
    # Tank bodies, fittings and copper feed pipes
    tank_positions=[]
    if p['tanks']==4:tank_positions=[(.46*rad*math.cos(math.tau*j/4+.2),.46*rad*math.sin(math.tau*j/4+.2)) for j in range(4)]
    elif p['tanks']==2:tank_positions=[(-rad*.30,0),(rad*.30,0)]
    else:tank_positions=[(0,0)]
    t_r=rad*(.18 if p['tanks']>=4 else .25 if p['tanks']==2 else .30)
    for idx,(x,z) in enumerate(tank_positions):
        ylo=-half+.15 if rad>.8 else -half+.095
        yhi=half-.15 if rad>.8 else half-.095
        mats[1].merge(closed_tank(x,z,ylo,yhi,t_r))
        for yy in (ylo+.035,yhi-.035,(ylo+yhi)/2):
            mats[3].merge(rod((x-t_r*1.08,yy,z),(x+t_r*1.08,yy,z),.018 if rad>.8 else .009,10))
        mats[4].merge(rod((x,ylo,z),(0,-half+.070,0),.014 if rad>.8 else .009,8))
        mats[4].merge(rod((x,yhi,z),(0,half-.070,0),.012 if rad>.8 else .008,8))
        mats[3].merge(solid_box((x,ylo-.038,z),(.14,.062,.14) if rad>.8 else (.075,.04,.075)))
        mats[3].merge(solid_box((x,yhi+.038,z),(.14,.062,.14) if rad>.8 else (.075,.04,.075)))
    # Battery banks bolt flat to the inner octagonal/hexagonal wall faces.
    # Local X is parallel to each flat face; local Z points along its face normal.
    face_apothem=rad*math.cos(math.pi/poly)
    face_width=2*rad*math.sin(math.pi/poly)
    n_battery=p['battery']
    for j in range(n_battery):
        face_id=(j*poly//n_battery) % poly
        theta=(face_id+.5)*math.tau/poly
        # Rotate the rectangular housing to be tangent to the girder's true polygon face.
        angle=math.pi/2-theta
        inward=face_apothem-(.175 if rad>.8 else .107)
        x,z=inward*math.cos(theta),inward*math.sin(theta)
        # Octo XL has eight wall packs; smaller parts distribute packs across faces.
        y=(((-1 if j%2 else 1)*min(h*.175,.62)) if n_battery>=4 else 0)
        wid=face_width*.73
        pack_h=min(h*.22,.72 if rad>.8 else .45)
        thickness=.14 if rad>.8 else .085
        mats[2].merge(solid_box((x,y,z),(wid,pack_h,thickness),angle=angle))
        # Recessed face brackets at either side + visible vertical power conduit.
        tang=(math.sin(theta),-math.cos(theta))
        for side in (-1,1):
            offset=wid*.46*side
            px,pz=x+offset*tang[0],z+offset*tang[1]
            mats[3].merge(rod((px,y-pack_h*.53,pz),(px,y+pack_h*.53,pz),.014 if rad>.8 else .008,7))
        mats[4].merge(rod((x,y-pack_h*.55,z),(x,-half+.13,z),.012 if rad>.8 else .007,7))
    # Brand plate on outer face. UV fix addresses mirrored/upside-down text in KSP.
    tagAngle=math.pi/poly
    mats[5].merge(label_quad(tagAngle,rad*math.cos(math.pi/poly)*.995, min(h*.13, .28),width=rad*.80,height=min(h*.15,.27)))
    w=Binary(MD/(p['id']+'.mu'));w.i(76543,5);w.string(p['id']);transform(w,'RoosterWorksGirder')
    for k,(name,mesh) in enumerate(zip(['Frame','MonopropellantVessels','BatteryPacks','BronzeClamps','FluidLines','RoosterWorksBrand'],mats)):
        assert mesh.tris, name
        child(w,name,mesh,k)
    child(w,'ArmorPanels',armor,1)  # toggled by stock ModulePartVariants (visual only)
    # Physical collision volumes around each fixed rail (no animation)
    for k,(x,z) in enumerate(circum):
        w.i(0);transform(w,f'RailCollider_{k:02}',pos=(x,0,z),collider=(.19 if rad>.8 else .12,h,.19 if rad>.8 else .12));w.i(1)
    # Mid equipment collision, box inset to frame to avoid intersecting neighboring parts
    w.i(0);transform(w,'EquipmentCollider',collider=(rad*.9,h*.68,rad*.9));w.i(1)
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
