#!/usr/bin/env python3
"""RoosterWorks Station Support FBX -> KSP .mu converter.

Converts supplied APPROVED Blender FBX mesh/UV geometry to native KSP v5 .mu,
keeping optional armor and corrected 3D nameplates. This is an experimental test tool;
Blender's procedural materials cannot be transferred automatically to KSP.
Version 0.8.4 preserves those fixes and flips Octo XL battery modules outward;
both Octo badges move 17 mm farther from the truss center.
Requires numpy, scipy, pillow (only for regenerating placeholder textures).
"""
from pathlib import Path
from collections import defaultdict, Counter
import struct, math, argparse
import numpy as np
from scipy.spatial.transform import Rotation
from PIL import Image, ImageDraw
from parse_rw_fbx import fbx_load, arr

ROOT=Path(__file__).resolve().parents[2]
MD=ROOT/'GameData'/'RoosterWorksStationSupport'/'Models'
PARTS={
 'RW_OctoSupport_XL': (8,2.5,4.75),
 'RW_OctoSupport_Medium': (8,2.5,2.65),
 'RW_HexSupport_Long': (6,1.25,3.15),
 'RW_HexSupport_Medium': (6,1.25,1.75),
 'RW_Octo25_Adapter': (8,2.5,.74),
 'RW_Hex125_Adapter': (6,1.25,.56),
}


MATKEYS=['steel','frame','white','bronze','titanium','battery','LED','label']
COLORS={'steel':(112,125,137),'frame':(37,52,65),'white':(202,211,209),
 'bronze':(174,121,64),'titanium':(181,193,195),'battery':(25,42,56),
 'LED':(54,255,92),'label':(244,246,242)}
COLOR_BY_NAME={
 'RW_01_Painted_Solid_Steel':'steel',
 'RW_02_Dark_Frame':'frame',
 'RW_03_Ceramic_White':'white',
 'RW_04_Anodized_Gold':'bronze',
 'RW_05_Brushed_Titanium_Tank':'titanium',
 'RW_06_Power_Bank_Dark':'battery',
 'RW_09_LED_Green_Emissive':'LED',
 'RW_08_White_Label':'label'
}

class W:
 def __init__(self,p):self.fh=p.open('wb')
 def close(self):self.fh.close()
 def i(self,*vs):self.fh.write(struct.pack('<'+'i'*len(vs),*vs))
 def f(self,*vs):self.fh.write(struct.pack('<'+'f'*len(vs),*vs))
 def b(self,v):self.fh.write(bytes([v]))
 def string(self,s):
  b=s.encode('utf8');n=len(b)
  while n>=128:self.b((n&127)|128);n>>=7
  self.b(n);self.fh.write(b)
 def xyz(self,xyz):self.f(*xyz)

def node_start(w,name,pos=(0,0,0),collider=None):
 w.string(name);w.xyz(pos);w.f(0,0,0,1);w.xyz((1,1,1))
 w.i(24);w.string('Untagged');w.i(0)
 if collider:
  w.i(28);w.b(0);w.xyz(collider);w.xyz((0,0,0))

def child_start(w,name,pos=(0,0,0),collider=None):
 w.i(0);node_start(w,name,pos,collider)
def child_end(w):w.i(1)

class Mesh:
 def __init__(self):self.verts=[];self.normals=[];self.uv=[];self.tris=[];self.vcache={}
 def has_room(self,n):return len(self.verts)+n<=50000
 def get(self,key,pos,norm,uv):
  if key in self.vcache:return self.vcache[key]
  idx=len(self.verts);self.vcache[key]=idx
  self.verts.append(tuple(map(float,pos)))
  self.normals.append(tuple(map(float,norm)))
  self.uv.append(tuple(map(float,uv)))
  return idx
 def triangle(self,t):self.tris.append(t)

def mesh_node(w,m,name,matid):
 assert len(m.verts)<65535 and m.tris
 child_start(w,name)
 w.i(7);w.i(13,len(m.verts),1);w.i(14)
 for v in m.verts:w.xyz(v)
 w.i(15)
 for uv in m.uv:w.f(*uv)
 w.i(17)
 for n in m.normals:w.xyz(n)
 w.i(19,len(m.tris)*3)
 for face in m.tris:w.i(*face)
 w.i(22);w.i(8);w.b(1);w.b(1);w.i(1,matid)
 child_end(w)

def getprop(model,name,default):
 pp=model.first('Properties70')
 if pp:
  for child in pp.ch:
   if child.name=='P' and child.p and child.p[0]==name:
    return child.p[4:]
 return default

def mat4(model):
 p=np.array(getprop(model,'Lcl Translation',[0,0,0]),dtype=float)
 degrees=np.array(getprop(model,'Lcl Rotation',[0,0,0]),dtype=float)
 scale=np.array(getprop(model,'Lcl Scaling',[1,1,1]),dtype=float)
 pre=np.array(getprop(model,'PreRotation',[0,0,0]),dtype=float)
 # FBX Blender-exported standard XYZ Euler. All frame objects use default pivots.
 rot=Rotation.from_euler('xyz',pre,degrees=True).as_matrix()@Rotation.from_euler('xyz',degrees,degrees=True).as_matrix()
 m=np.eye(4);m[:3,:3]=rot @ np.diag(scale);m[:3,3]=p
 return m

def ref_element(layer,data_name,idx_name,polygon_slot,control_point,face_index=0):
 if layer is None:return None
 mapping=layer.first('MappingInformationType').p[0]
 reference=layer.first('ReferenceInformationType').p[0]
 vals=arr(layer.first(data_name).p[0])
 if mapping=='ByPolygonVertex':k=polygon_slot
 elif mapping=='ByVertice' or mapping=='ByVertex':k=control_point
 elif mapping=='AllSame':k=0
 elif mapping=='ByPolygon':k=face_index
 else:raise ValueError(f'Unknown mapping: {mapping}')
 if reference=='IndexToDirect':
  k=arr(layer.first(idx_name).p[0])[k]
 elif reference!='Direct':raise ValueError(f'Unknown reference: {reference}')
 return vals,k

def get_elements(g):
 # parsed once per object rather than re-decompress each layer in hot loop
 out={}
 for kind,name,idx in [('normal','Normals','NormalsIndex'),('uv','UV','UVIndex')]:
  layer=g.first('LayerElementNormal' if kind=='normal' else 'LayerElementUV')
  if layer is None:out[kind]=None;continue
  out[kind]=dict(mapping=layer.first('MappingInformationType').p[0],
     reference=layer.first('ReferenceInformationType').p[0],
     vals=np.array(arr(layer.first(name).p[0]),dtype=float).reshape((-1,3 if kind=='normal' else 2)),
     indices=np.array(arr(layer.first(idx).p[0]),dtype=int) if layer.first(idx) else None)
 return out

def lookup(el,corner,v_id,face_id):
 if el is None:return None,-1
 mapping=el['mapping']
 if mapping=='ByPolygonVertex':i=corner
 elif mapping in ('ByVertex','ByVertice'):i=v_id
 elif mapping=='ByPolygon':i=face_id
 elif mapping=='AllSame':i=0
 else:raise ValueError(f'Unknown mapping: {mapping}')
 if el['reference']=='IndexToDirect':i=el['indices'][i]
 return el['vals'][i],int(i)

def generate_materials():
 # KSP/Diffuse material textures are deliberately simple stand-ins.
 # Blender procedural noise, metalness, bump, and animated emissive LEDs
 # cannot be transferred automatically in this direct conversion.
 for name,color in COLORS.items():
  im=Image.new('RGB',(128,128),color)
  dr=ImageDraw.Draw(im)
  if name=='battery':
   for y in range(0,128,32):
    dr.line((3,y,124,y),fill=(37,65,78),width=2)
  if name=='titanium':
   for y in range(12,128,45):dr.line((0,y,127,y),fill=(192,204,204),width=1)
  if name=='bronze':
   for y in range(15,128,47):dr.line((0,y,127,y),fill=(194,150,76),width=1)
  im.save(MD/f'rw_{name}.png')

def main(fbx, part_id, destination=None):
 global MD
 if part_id not in PARTS: raise ValueError('Unsupported part: '+part_id)
 n_sides, diameter, height = PARTS[part_id]
 MD = Path(destination or (ROOT/'GameData'/'RoosterWorksStationSupport'/'Models'))
 MD.mkdir(parents=True,exist_ok=True)
 fbx = Path(fbx)
 if not fbx.is_file(): raise FileNotFoundError(fbx)
 nodes=fbx_load(fbx);o=next(n for n in nodes if n.name=='Objects');cons=next(n for n in nodes if n.name=='Connections')
 byid={a.p[0]:a for a in o.ch if a.p}
 models={i:a for i,a in byid.items() if a.name=='Model'}
 geometries={i:a for i,a in byid.items() if a.name=='Geometry'}
 materials={i:a for i,a in byid.items() if a.name=='Material'}
 model_parent={}; geo_owner={}; material_owner={}
 for n in cons.ch:
  if n.name!='C' or len(n.p)<3 or n.p[0]!='OO':continue
  a,b=n.p[1:3]
  if a in models and b in models:model_parent[a]=b
  elif a in geometries and b in models:geo_owner[a]=b
  elif a in materials and b in models:material_owner[b]=a
 assert len(geometries)==len(geo_owner),'Unattached geometry'
 top=[i for i in models if i not in model_parent]
 assert len(top)==1
 rootid=top[0]
 assert part_id in models[rootid].p[1], (part_id,models[rootid].p[1])
 def name(i):return models[i].p[1].split('\x00')[0]
 armor_ids=[i for i in models if name(i).startswith('ArmorPanels')]
 assert len(armor_ids)<=1
 armor_id=armor_ids[0] if armor_ids else None
 if armor_id is not None: assert model_parent[armor_id]==rootid
 def under_armor(i):
  if armor_id is None: return False
  while i in model_parent:
   if i==armor_id:return True
   i=model_parent[i]
  return i==armor_id
 cache={}
 def globalmat(i):
  if i in cache:return cache[i]
  local=mat4(models[i]);cache[i]=globalmat(model_parent[i])@local if i in model_parent else local
  return cache[i]
 grouped=defaultdict(list)
 counts=Counter();boundslo=np.array([1e9]*3);boundshi=-boundslo
 for idx,(gid,g) in enumerate(geometries.items()):
  mid=geo_owner[gid];mat_id=material_owner.get(mid)
  assert mat_id is not None,f'Missing material {name(mid)}'
  mname=materials[mat_id].p[1].split('\x00')[0]
  mkey=next((v for k,v in COLOR_BY_NAME.items() if mname.startswith(k)),None)
  assert mkey is not None,(name(mid),mname)
  group='armor' if under_armor(mid) else 'body'
  # FBX encodes its global scene units in centimeters: scale to meters.
  wm=globalmat(mid);wm[:3,:]=wm[:3,:]*.01
  nmat=np.linalg.inv(wm[:3,:3]).T
  det=np.linalg.det(wm[:3,:3])
  verts=np.array(arr(g.first('Vertices').p[0]),dtype=float).reshape((-1,3))
  polyindices=arr(g.first('PolygonVertexIndex').p[0])
  els=get_elements(g)
  # Text only: mirror local X to correct left/right reversed lettering seen
  # in KSP.  Badge backing, trim, tanks and every other source mesh are untouched.
  badge_text= name(mid).startswith('RoosterWorks_') and '_Text_' in name(mid)
  if badge_text:
   verts[:,0]*=-1
   if els['normal'] is not None:
    els['normal']['vals'][:,0]*=-1
  transformed=(wm[:3,:3]@verts.T).T+wm[:3,3]
  objname=name(mid)
  shell_fix = part_id in ('RW_Octo25_Adapter','RW_Hex125_Adapter') and objname in ('Octagonal_To_Round_Shell','Hexagonal_To_Round_Shell')
  # Blender's adapter loft uses an inside-out triangle order. Swap winding AND
  # normal direction on only the exterior loft; the end rings stay intact.
  # Preserve both the full 360-degree shell silhouette and its standard UVs.
  # Hex Long: shrink the original four pressure vessels by 20% in diameter.
  # Reposition wall-mounted battery modules toward their hexagonal exterior so
  # the tanks/collars and housings have >1cm clearance in the tightest sector.
  if part_id=='RW_HexSupport_Long':
   tankmatch=__import__('re').match(r'^Monopropellant_(\d+)_',objname)
   if tankmatch and not objname.endswith('_Propellant_Line'):
    tankidx=int(tankmatch.group(1))-1
    tankcenters=[(-.202,-.202),(-.202,.202),(.202,-.202),(.202,.202)]
    if tankidx not in range(4):raise ValueError('Unexpected Hex Long tank number: '+objname)
    tx,tz=tankcenters[tankidx]
    transformed[:,0]=tx+(transformed[:,0]-tx)*.80
    transformed[:,2]=tz+(transformed[:,2]-tz)*.80
   battmatch=__import__('re').match(r'^Battery_Face_(\d+)_',objname)
   if battmatch:
    faceidx=int(battmatch.group(1))-1
    if faceidx not in range(6):raise ValueError('Unexpected Hex Long battery face: '+objname)
    theta=(faceidx+.5)*math.tau/6
    transformed[:,0]+=math.cos(theta)*.040
    transformed[:,2]+=math.sin(theta)*.040
  # v0.8.4: the approved Octo XL battery banks were still showing their inner
  # faces. Rotate each complete Battery_Face assembly (housing, rail, cable,
  # LEDs) by 180 degrees around the local vertical axis THROUGH the pack center.
  # This is a proper 180-degree rotation (determinant +1), not a mirror:
  # mesh winding and UVs remain valid. Non-battery geometry is unchanged.
  battery_flip = part_id == 'RW_OctoSupport_XL' and objname.startswith('Battery_Face_')
  if battery_flip:
   import re
   mm=re.match(r'^Battery_Face_(\d{2})_',objname)
   if not mm:raise ValueError('Unexpected Octo XL battery object: '+objname)
   face_id=int(mm.group(1))-1
   if face_id not in range(8):raise ValueError('Invalid battery face index')
   theta=(face_id+.5)*math.tau/8
   pack_radius=diameter*.47*math.cos(math.pi/8)-.108
   cx=pack_radius*math.cos(theta);cz=pack_radius*math.sin(theta)
   transformed[:,0]=2*cx-transformed[:,0]
   transformed[:,2]=2*cz-transformed[:,2]
  # Put the rear of the badge almost flush against the armor panel/shell.
  # Translate backing, gold trim, and lettering together to retain type size,
  # readability and proportions. Octo XL's approved text mirroring is retained.
  badgepart=objname.startswith('RoosterWorks_Identification_Plate_') or objname.startswith('RoosterWorks_Adapter_ID_')
  if badgepart:
   theta=math.pi/n_sides
   apothem=(diameter*.47)*math.cos(math.pi/n_sides)
   if 'Adapter' in part_id:
    # Adapter shell is midway between polygon and round profile at y=0.
    shell_face_radius=(apothem+diameter*.5)/2
    badge_current=apothem+.065
    badge_target=shell_face_radius+.012  # ~2 mm backing-to-skin clearance
   else:
    badge_current=apothem+.075
    # v0.8.4: nudge only the two Octo badges 17mm outward. The metal backing
    # remains close to the painted shell and readable outside both variants.
    badge_target=apothem+(.026 if part_id.startswith('RW_OctoSupport_') else .009)
   displacement=badge_target-badge_current
   transformed[:,0]+=math.cos(theta)*displacement
   transformed[:,2]+=math.sin(theta)*displacement
  boundslo=np.minimum(boundslo,transformed.min(axis=0));boundshi=np.maximum(boundshi,transformed.max(axis=0))
  # Small material chunks avoid Unity/old KSP vertex-index overflow.
  key=(group,mkey);lst=grouped[key]
  if not lst:lst.append(Mesh())
  pending=[];facei=0
  def emit(pending,faceid):
   nonlocal lst
   chunk=lst[-1]
   if not chunk.has_room(len(pending)):
    chunk=Mesh();lst.append(chunk)
   face=[]
   for corner,vid,sidx in pending:
    uv,iu=lookup(els['uv'],sidx,vid,faceid)
    no,inorm=lookup(els['normal'],sidx,vid,faceid)
    if no is None:no=np.array((0,1,0))
    no=nmat@no;no=no/(np.linalg.norm(no) or 1)
    if battery_flip:
     no[0]*=-1
     no[2]*=-1
    if shell_fix:no=-no  # outward-facing lighting on reversed loft
    if uv is None:uv=(0,0)
    ident=(gid,vid,inorm,iu)
    face.append(chunk.get(ident,transformed[vid],no,uv))
   for j in range(1,len(face)-1):
    a,b,c=face[0],face[j],face[j+1]
    # Negative FBX determinant or intentional text mirroring changes handedness.
    # Reverse text triangle indices, too, to retain outward-facing lettering.
    if (det<0) ^ badge_text ^ shell_fix:b,c=c,b
    if a!=b and b!=c and c!=a:chunk.triangle((a,b,c))
   counts[(group,mkey)]+=len(face)-2
  for slot,raw in enumerate(polyindices):
   last=raw<0;vid=-raw-1 if last else raw
   pending.append((slot,vid,slot))
   if last:
    emit(pending,facei);pending=[];facei+=1
  assert not pending
 spans=boundshi-boundslo
 assert diameter*.70 < spans[0] < diameter*1.25,(part_id,boundslo,boundshi)
 assert height*.70 < spans[1] < height*1.25,(part_id,boundslo,boundshi)
 assert diameter*.70 < spans[2] < diameter*1.25,(part_id,boundslo,boundshi)
 generate_materials()
 out=MD/(part_id+'.mu')
 w=W(out);w.i(76543,5);w.string(part_id);node_start(w,part_id)
 mats={m:i for i,m in enumerate(MATKEYS)}
 # first grouped bodies and armored subgroup under root
 for (gr,m),meshes in grouped.items():
  if gr!='body':continue
  for partno,mesh in enumerate(meshes):
   if mesh.tris:mesh_node(w,mesh,f'Body_{m}_{partno:02}',mats[m])
 if armor_id is not None:
  child_start(w,'ArmorPanels')
  for (gr,m),meshes in grouped.items():
   if gr!='armor':continue
   for partno,mesh in enumerate(meshes):
    if mesh.tris:mesh_node(w,mesh,f'Armor_{m}_{partno:02}',mats[m])
  child_end(w)
 # Simplified fixed collision. No moving or animated bodies.
 radius=diameter*.47
 if 'Adapter' not in part_id:
  for i in range(n_sides):
   t=math.tau*i/n_sides
   d=.21 if diameter>2 else .13
   child_start(w,f'RailCollider_{i:02}',pos=(radius*math.cos(t),0,radius*math.sin(t)),collider=(d,max(.10,height-.15),d));child_end(w)
  d=diameter*.42
  child_start(w,'EquipmentCollider',collider=(d,height*.72,d));child_end(w)
 else:
  child_start(w,'AdapterCollider',collider=(diameter*.73,height*.72,diameter*.73));child_end(w)
 w.i(10,len(MATKEYS))
 for i,m in enumerate(MATKEYS):
  w.string('RW_'+m);w.string('KSP/Diffuse');w.i(2)
  w.string('_Color');w.i(0);w.f(1,1,1,1)
  w.string('_MainTex');w.i(4,i);w.f(1,1);w.f(0,0)
 w.i(12,len(MATKEYS))
 for m in MATKEYS:w.string('rw_'+m);w.i(0)
 w.close()
 print('GEOMETRY:',len(geometries),'objects')
 print('MATERIALS:',MATKEYS)
 print('GROUPS:',sorted((k,sum(len(v.verts) for v in meshes),sum(len(v.tris) for v in meshes)) for k,meshes in grouped.items()))
 print('BBOX_METERS',np.round(boundslo,4).tolist(),np.round(boundshi,4).tolist())
 print('TRIANGLES',sum(counts.values()),'MU_BYTES',out.stat().st_size)
 print('OUTPUT',out)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description='Convert one original RoosterWorks FBX to KSP mu')
 parser.add_argument('--part',required=True,choices=list(PARTS))
 parser.add_argument('--fbx',required=True,type=Path)
 parser.add_argument('--models',type=Path,default=None)
 options=parser.parse_args()
 main(options.fbx,options.part,options.models)
