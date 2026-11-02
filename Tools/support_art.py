"""Original native geometry and deterministic engineering texture assets."""
from pathlib import Path
import sys,math,copy,shutil
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'.build-deps'),str(R/'Source'),str(R/'Tools')]
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import build_hab250 as h
from normal_tools import tangents,save_normal_dds
M=R/'GameData/RoosterWorksStationSupport/Models';ART=R/'Source/Textures'
COLORS=dict(steel=(152,162,166),frame=(62,73,79),white=(213,217,208),bronze=(165,124,66),tank=(177,187,188),black=(27,36,41),blue=(53,104,164),yellow=(212,173,49),led=(71,222,118),grey=(103,119,128))

def unit(v):
    v=np.array(v,dtype=float);return v/max(np.linalg.norm(v),1e-12)

def node(name):return dict(name=name,position=(0,0,0),rotation=(0,0,0,1),scale=(1,1,1),tag='Untagged',layer=0,children=[])

def textures():
    rng=np.random.default_rng(714);n=1024;y,x=np.mgrid[:n,:n]
    grain=rng.normal(0,1,(n,n));lines=rng.normal(0,1,(n,1));cloud=np.array(Image.fromarray(rng.integers(0,255,(32,32),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC),float)/255-.5
    for key,color in COLORS.items():
        detail=grain*.8+cloud*5+(lines*1.5 if key in ('steel','tank') else 0)
        arr=np.uint8(np.clip(np.array(color)[None,None,:]+detail[:,:,None],0,255));im=Image.fromarray(arr)
        spec=150 if key in ('steel','tank','bronze') else (25 if key in ('black','blue','green') else 65)
        im.putalpha(Image.fromarray(np.uint8(np.clip(spec+cloud*20,0,255))));im.save(M/f'rwss_{key}.png',optimize=True)
    ht=cloud*.04+grain*.003+lines*.006;dy,dx=np.gradient(ht);nn=np.stack((-dx*6,dy*6,np.ones_like(dx)),axis=-1);nn/=np.linalg.norm(nn,axis=-1,keepdims=True);rgb=np.uint8(np.clip(nn*.5+.5,0,1)*255)
    Image.fromarray(rgb).save(ART/'rwss_metal_normal_rgb.png');save_normal_dds(rgb,M/'rwss_metal_NRM.dds')
    for name in ('rwss_insulation.png','rwss_insulation_NRM.dds'):shutil.copyfile(ART/name,M/name)
    im=Image.new('RGB',(1024,1024),(37,48,54));d=ImageDraw.Draw(im)
    bold=lambda size:ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',size)
    for row,title in enumerate(('POWER / CELL ARRAY','PRESSURE / SERVICE','DATA / UMBILICAL','RW / ACCESS')):
        y0=row*256;d.rounded_rectangle((12,y0+12,1012,y0+244),18,fill=(61,72,77),outline=(165,174,170),width=4)
        d.rectangle((30,y0+30,994,y0+73),fill=(28,38,44));d.text((49,y0+34),title,font=bold(30),fill=(218,223,206))
        for j in range(12):d.rounded_rectangle((48+j*54,y0+102,82+j*54,y0+196),5,fill=(19,27,32),outline=(102,116,120),width=2)
        d.text((735,y0+111),'RW-'+str(41+row),font=bold(39),fill=(210,218,210));d.text((735,y0+167),'SERVICE / 01',font=bold(21),fill=(161,179,177))
        for xx in (30,994):
            for yy in (y0+28,y0+228):d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=(159,166,161));d.line((xx-4,yy,xx+4,yy),fill=(39,47,48),width=2)
        d.rectangle((27,y0+215,696,y0+223),fill=(164,124,64))
    im.putalpha(Image.new('L',im.size,80));im.save(M/'rwss_atlas.png');im.save(ART/'rwss_atlas.png')

class Batch:
    def __init__(self):self.meshes={}
    def __getitem__(self,key):return self.meshes.setdefault(key,h.Mesh())

def quad(m,pts,uv=None):
    pts=[np.array(p) for p in pts];no=unit(np.cross(pts[1]-pts[0],pts[2]-pts[0]));m.quad([tuple(p) for p in pts],[tuple(no)]*4,uv or ((0,0),(1,0),(1,1),(0,1)))

def beam(m,a,b,width,depth=None,out=(0,0,1)):
    """Closed eight-sided beveled rectangular beam with physical UV scale."""
    a=np.array(a);b=np.array(b);t=unit(b-a);out=np.array(out);v=out-t*np.dot(out,t)
    if np.linalg.norm(v)<.1:v=np.cross(t,(1,0,0) if abs(t[0])<.8 else (0,0,1))
    v=unit(v);u=unit(np.cross(t,v));w=width/2;d=(depth or width)/2;c=min(w,d)*.23
    poly=[(-w+c,-d),(w-c,-d),(w,-d+c),(w,d-c),(w-c,d),(-w+c,d),(-w,d-c),(-w,-d+c)]
    aa=[a+u*x+v*y for x,y in poly];bb=[b+u*x+v*y for x,y in poly]
    for j in range(8):
        k=(j+1)%8;pts=[aa[j],bb[j],bb[k],aa[k]]
        if np.dot(np.cross(pts[1]-pts[0],pts[2]-pts[0]),(aa[j]+aa[k])/2-a)<0:pts.reverse()
        quad(m,pts,((0,0),(np.linalg.norm(b-a)*2,0),(np.linalg.norm(b-a)*2,.25),(0,.25)))
    for ring,center,normal in ((aa,a,-t),(bb,b,t)):
        for j in range(8):
            pts=[center,ring[j],ring[(j+1)%8]]
            if np.dot(np.cross(pts[1]-pts[0],pts[2]-pts[0]),normal)<0:pts.reverse()
            m.triangle([tuple(p) for p in pts],[tuple(normal)]*3,[(.5,.5),(0,0),(1,1)])

def tube(m,a,b,r=.01,sides=10):
    a=np.array(a);b=np.array(b);t=unit(b-a);u=unit(np.cross(t,(0,0,1) if abs(t[2])<.9 else (1,0,0)));v=np.cross(t,u)
    rings=[[p+r*(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides)) for j in range(sides)] for p in (a,b)]
    for j in range(sides):
        k=(j+1)%sides;points=[rings[0][j],rings[0][k],rings[1][k],rings[1][j]];ns=[unit(points[0]-a),unit(points[1]-a),unit(points[2]-b),unit(points[3]-b)]
        if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),ns[0])<0:points.reverse();ns.reverse()
        m.quad([tuple(p) for p in points],[tuple(n) for n in ns])
    for ring,center,normal in ((rings[0],a,-t),(rings[1],b,t)):
        for j in range(sides):
            pts=[center,ring[j],ring[(j+1)%sides]]
            if np.dot(np.cross(pts[1]-pts[0],pts[2]-pts[0]),normal)<0:pts.reverse()
            m.triangle([tuple(p) for p in pts],[tuple(normal)]*3,[(.5,.5),(0,0),(1,1)])

def bolt(batch,p,normal,size):
    p=np.array(p);normal=unit(normal);tube(batch['black'],p-normal*size*.08,p+normal*size*.12,size*.72,10);tube(batch['steel'],p,p+normal*size*.50,size*.48,6)

def plate(batch,p,right,up,width,height,depth,key='frame',slot=None):
    p=np.array(p);right=unit(right);up=unit(up);normal=unit(np.cross(right,up))
    beam(batch[key],p-up*height/2,p+up*height/2,width,depth,normal)
    if slot is not None:
        pts=[p+right*x+up*y+normal*(depth/2+.0003) for x,y in ((-width*.44,-height*.42),(width*.44,-height*.42),(width*.44,height*.42),(-width*.44,height*.42))]
        # Atlas rows are authored top-down, Unity UV V is upward.
        lo=1-(slot+1)/4;hi=1-slot/4;quad(batch['atlas'],pts,((0,lo),(1,lo),(1,hi),(0,hi)))
    return normal

def lathe(m,profile,center=(0,0,0),segments=48):
    center=np.array(center)
    for j in range(len(profile)-1):
        y0,r0=profile[j];y1,r1=profile[j+1]
        for k in range(segments):
            a=k*math.tau/segments;b=(k+1)*math.tau/segments
            points=[center+np.array(h.point(r0,a,y0)),center+np.array(h.point(r0,b,y0)),center+np.array(h.point(r1,b,y1)),center+np.array(h.point(r1,a,y1))]
            def normal(index,angle):
                lo=max(0,index-1);hi=min(len(profile)-1,index+1);dy=profile[hi][0]-profile[lo][0];dr=profile[hi][1]-profile[lo][1]
                return unit((math.sin(angle)*dy,-dr,math.cos(angle)*dy))
            nn=[normal(index,t) for index,t in ((j,a),(j,b),(j+1,b),(j+1,a))]
            # Outward faces; profile proceeds bottom to top.
            if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),nn[0])<0:points.reverse();nn.reverse()
            m.quad([tuple(p) for p in points],[tuple(n) for n in nn],((k/segments,j/(len(profile)-1)),((k+1)/segments,j/(len(profile)-1)),((k+1)/segments,(j+1)/(len(profile)-1)),(k/segments,(j+1)/(len(profile)-1))))

def vessel(batch,center,radius,length,key='tank'):
    cap=min(radius,length*.25);cyl=length/2-cap;profile=[]
    for t in np.linspace(-math.pi/2,0,10):profile.append((-cyl+cap*math.sin(t),max(.005,radius*math.cos(t))))
    profile.append((cyl,radius))
    for t in np.linspace(0,math.pi/2,10)[1:]:profile.append((cyl+cap*math.sin(t),max(.005,radius*math.cos(t))))
    lathe(batch[key],profile,center)
    for yy in (-cyl,cyl):
        lathe(batch['frame'],[(yy-.025,radius+.004),(yy+.025,radius+.004)],center)
        for a in np.linspace(0,math.tau,8,endpoint=False):bolt(batch,np.array(center)+h.point(radius+.008,a,yy),(math.sin(a),0,math.cos(a)),.016)
    for sgn in (-1,1):
        p=np.array(center)+(0,sgn*length/2,0);tube(batch['steel'],p,p+(0,sgn*.05,0),radius*.10,16);tube(batch['bronze'],p+(0,sgn*.03,0),p+(0,sgn*.07,0),radius*.065,12)
    return math.pi*radius**2*(length-2*cap)+4*math.pi/3*radius**2*cap

def materials(model):
    model.materials=[];model.textures=[]
    for key in list(COLORS)+['atlas','insulation']:
        ti=len(model.textures);model.textures.append(dict(name='rwss_'+key,type=0));props={'_MainTex':dict(index=ti,scale=(1,1),offset=(0,0)),'_Color':(1,1,1,1),'_SpecColor':(.45,.45,.45,1),'_Shininess':.25}
        shader='KSP/Specular'
        if key in ('steel','frame','white','bronze','tank','grey','insulation'):
            normal='rwss_insulation_NRM' if key=='insulation' else 'rwss_metal_NRM';ni=next((i for i,t in enumerate(model.textures) if t['name']==normal),None)
            if ni is None:ni=len(model.textures);model.textures.append(dict(name=normal,type=1))
            props['_BumpMap']=dict(index=ni,scale=(1,1),offset=(0,0));shader='KSP/Bumped Specular'
        model.materials.append(dict(name='RWSS_'+key,shader=shader,properties=props))

def emit(model,parent,name,batch):
    for key,mesh in batch.meshes.items():
        if not mesh.triangles:continue
        # Split at triangle boundaries, keeping each Unity mesh below 16-bit limits.
        tris=mesh.triangles
        for part,start in enumerate(range(0,len(tris),12000)):
            tt=tris[start:start+12000];used=sorted({v for t in tt for v in t});ids={v:i for i,v in enumerate(used)}
            data=dict(vertices=[mesh.vertices[i] for i in used],normals=[mesh.normals[i] for i in used],uvs=[mesh.uvs[i] for i in used],submeshes=[[tuple(ids[i] for i in t) for t in tt]])
            mat=next(i for i,m in enumerate(model.materials) if m['name']=='RWSS_'+key)
            if '_BumpMap' in model.materials[mat]['properties']:tangents(data)
            child=node(f'{name}_{key}_{part}');child.update(mesh=data,materials=[mat],shadows=(1,1));parent['children'].append(child)
