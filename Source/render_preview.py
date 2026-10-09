#!/usr/bin/env python3
"""Offline engineering illustration from exact procedural model triangles.
This is NOT a real KSP screenshot or a promise that the editor variant loads.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import importlib.util,math
src=Path(__file__).resolve();spec=importlib.util.spec_from_file_location('rwbuild',src.parent/'build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
OUT=src.parents[1]/'Media';OUT.mkdir(exist_ok=True)
W,H=3060,1170
out=Image.new('RGB',(W,H),(20,30,40));d=ImageDraw.Draw(out)
reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(bold,27);small=ImageFont.truetype(reg,20);sub=ImageFont.truetype(reg,16)
d.rectangle((0,0,W,107),fill=(34,44,54))
d.text((48,15),'ROOSTERWORKS  |  KERBALISM ADDITIONS',font=ImageFont.truetype(bold,37),fill=(239,239,237))
d.text((48,68),'0.5.0 ALPHA5  •  SMOOTHED GIRDERS  •  FULL-HEIGHT INTERNALS',font=sub,fill=(215,167,90))
cam=b.normalize((2.0,1.00,2.80));right=b.normalize(b.cross((0,1,0),cam));up=b.normalize(b.cross(cam,right));light=b.normalize((1.4,2.0,2.0))
palette=[(122,139,151),(221,221,217),(67,84,105),(203,151,79),(162,116,73),(34,45,58),(214,218,216)]

def draw_meshes(meshes,center,scale):
    poly=[]
    for i,m in enumerate(meshes):
        for a,bb,c in m.tris:
            vertices=[m.verts[t] for t in (a,bb,c)]
            n=b.normalize(m.normals[a])
            if i!=5 and sum(n[k]*cam[k] for k in range(3))<=0:continue
            dep=sum(sum(v[k]*cam[k] for k in range(3)) for v in vertices)/3
            pts=[(center[0]+scale*sum(v[k]*right[k] for k in range(3)),center[1]-scale*sum(v[k]*up[k] for k in range(3))) for v in vertices]
            diffuse=max(0,sum(light[k]*n[k] for k in range(3)))
            amt=.66+.28*diffuse
            color=tuple(max(0,min(255,round(ch*amt))) for ch in palette[i])
            poly.append((dep,pts,color))
    for dep,pts,color in sorted(poly,key=lambda x:x[0]):d.polygon(pts,fill=color)

for j,p in enumerate(b.PARTS):
    left=j*510
    for i,(ymin,ymax,variant) in enumerate(((110,570,'OPEN FRAME'),(590,1105,'PANEL-CLAD TRUSS'))):
        d.rectangle((left+8,ymin,left+502,ymax),fill=((26,38,49) if j%2 else (29,42,53)),outline=(56,76,87),width=1)
        d.text((left+26,ymin+12),p['id'].replace('RW_','').replace('Support_',' '),font=font,fill=(235,238,240))
        d.text((left+26,ymin+49),f"{variant}   |   {p['diameter']} m × {p['height']} m",font=small,fill=(202,165,105))
        base,panels=b.build_part(p)
        full=base+[panels] if i else base
        scale=(71 if p['diameter']>2 else 102)
        if p['height']>4:scale=65
        draw_meshes(full,(left+253,ymin+245),scale)
        d.text((left+24,ymax-40),f"EC {p['ec']:,}   •   Mono {p['mono']:,}",font=small,fill=(217,223,224))
# 5th column with adapter
left=2040
d.rectangle((left+8,110,left+502,1105),fill=(25,36,47),outline=(56,76,87),width=1)
d.text((left+28,126),'OCTO → 2.5 m',font=font,fill=(241,241,239))
d.text((left+28,162),'Round stack adapter',font=small,fill=(211,169,106))
adapter=b.build_adapter()
draw_meshes(adapter,(left+255,473),174)
d.text((left+28,670),'2.5 m octagonal base',font=small,fill=(230,231,231))
d.text((left+28,710),'2.5 m circular top',font=small,fill=(230,231,231))
d.text((left+28,761),'2 stack nodes • size2',font=sub,fill=(181,200,213))
d.text((left+28,817),'Structural → Adapters',font=sub,fill=(181,200,213))
d.text((left+28,923),'No resource storage',font=sub,fill=(181,200,213))
d.text((left+28,1074),'Geometry preview only',font=sub,fill=(214,161,92))
# Sixth column with 1.25m hex adapter
left=2550
d.rectangle((left+8,110,left+502,1105),fill=(25,36,47),outline=(56,76,87),width=1)
d.text((left+28,126),'HEX → 1.25 m',font=font,fill=(241,241,239))
d.text((left+28,162),'Round stack adapter',font=small,fill=(211,169,106))
hadapter=b.build_hex_adapter()
draw_meshes(hadapter,(left+255,473),285)
d.text((left+28,670),'1.25 m hexagonal base',font=small,fill=(230,231,231))
d.text((left+28,710),'1.25 m circular top',font=small,fill=(230,231,231))
d.text((left+28,761),'2 stack nodes • size1',font=sub,fill=(181,200,213))
d.text((left+28,817),'Structural → Adapters',font=sub,fill=(181,200,213))
d.text((left+28,923),'No resource storage',font=sub,fill=(181,200,213))
d.text((left+28,1074),'Geometry preview only',font=sub,fill=(214,161,92))
p=OUT/'RoosterWorks-Girders-v0.5.0-Refined-Preview.png'
out.save(p)
print('CREATED',p)
