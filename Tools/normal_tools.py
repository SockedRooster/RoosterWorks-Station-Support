import numpy as np
from PIL import Image
import io,struct

def save_normal_dds(rgb,path):
    # Full normalized mip chain avoids sparkling textile detail at VAB distances.
    # DDS uses the vertically inverted storage convention relative to KSP PNGs.
    image=Image.fromarray(rgb[::-1].copy());blocks=[];header=None
    while True:
        xyz=np.asarray(image,dtype=float)/127.5-1
        xyz/=np.maximum(np.linalg.norm(xyz,axis=-1,keepdims=True),1e-9)
        packed=np.full((*xyz.shape[:2],4),255,dtype=np.uint8)
        packed[:,:,1]=np.uint8(np.clip(xyz[:,:,1]*.5+.5,0,1)*255)
        packed[:,:,3]=np.uint8(np.clip(xyz[:,:,0]*.5+.5,0,1)*255)
        buf=io.BytesIO();Image.fromarray(packed).save(buf,format='DDS',pixel_format='DXT5');data=buf.getvalue()
        if header is None:header=bytearray(data[:128])
        blocks.append(data[128:])
        if image.width==1:break
        image=image.resize((max(1,image.width//2),max(1,image.height//2)),Image.Resampling.BOX)
    struct.pack_into('<I',header,8,struct.unpack_from('<I',header,8)[0]|0x20000)
    struct.pack_into('<I',header,28,len(blocks));struct.pack_into('<I',header,108,0x401008)
    path.write_bytes(header+b''.join(blocks))

def tangents(m):
    p=np.asarray(m['vertices']);uv=np.asarray(m['uvs']);n=np.asarray(m['normals']);t=np.array([t for s in m['submeshes'] for t in s])
    e1=p[t[:,1]]-p[t[:,0]];e2=p[t[:,2]]-p[t[:,0]];d1=uv[t[:,1]]-uv[t[:,0]];d2=uv[t[:,2]]-uv[t[:,0]]
    det=d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0];inv=np.zeros_like(det);mask=abs(det)>1e-12;inv[mask]=1/det[mask]
    tx=(e1*d2[:,1,None]-e2*d1[:,1,None])*inv[:,None]
    ty=(e2*d1[:,0,None]-e1*d2[:,0,None])*inv[:,None]
    sx=np.zeros_like(p);sy=np.zeros_like(p)
    for j in range(3):np.add.at(sx,t[:,j],tx);np.add.at(sy,t[:,j],ty)
    sx-=n*np.sum(n*sx,axis=1)[:,None];length=np.linalg.norm(sx,axis=1);bad=length<1e-8
    fallback=np.cross(n[bad],np.where((abs(n[bad,0])<.9)[:,None],(1,0,0),(0,1,0)))
    sx[bad]=fallback;length=np.linalg.norm(sx,axis=1);sx/=np.maximum(length[:,None],1e-9)
    hand=np.where(np.sum(np.cross(n,sx)*sy,axis=1)<0,-1.,1.)
    m['tangents']=np.column_stack((sx,hand)).tolist()