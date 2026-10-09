import zlib,struct
from pathlib import Path
class N:
 def __init__(self,name,props,kids):self.name=name;self.p=props;self.ch=kids
 def all(self,name): return [x for x in self.ch if x.name==name]
 def first(self,name): return next((x for x in self.ch if x.name==name),None)

def fbx_load(path):
 data=Path(path).read_bytes(); assert data[:21]==b'Kaydara FBX Binary  \x00';v=struct.unpack_from('<I',data,23)[0]; assert v<7500,(v,'only 32 bit supported')
 def value(p):
  t=chr(data[p]);p+=1
  if t in 'YCBIFDL':
   fmt={'Y':'h','C':'?','B':'B','I':'i','F':'f','D':'d','L':'q'}[t]
   obj=struct.unpack_from('<'+fmt,data,p)[0];return obj,p+struct.calcsize(fmt)
  if t in 'SR':
   size=struct.unpack_from('<I',data,p)[0];p+=4
   bb=data[p:p+size];return (bb.decode('utf8','replace') if t=='S' else bb),p+size
  if t in 'fdilbc':
   num,enc,size=struct.unpack_from('<III',data,p);p+=12
   bb=data[p:p+size];p+=size
   if enc==1:bb=zlib.decompress(bb)
   fmt={'f':'f','d':'d','i':'i','l':'q','b':'B','c':'B'}[t]
   assert len(bb)==num*struct.calcsize(fmt),(t,num,len(bb))
   # lazy return memoryview to keep no multi-million tuples
   return (t,num,bb),p
  raise ValueError((t,p))
 def node(p):
  end,num,plen,nlen=struct.unpack_from('<IIIB',data,p)
  if end==0:return None,p+13
  p+=13;name=data[p:p+nlen].decode('utf8','replace');p+=nlen
  props=[]
  for i in range(num):
   obj,p=value(p);props.append(obj)
  kids=[]
  while p<end-13:
   child,p=node(p)
   if child:kids.append(child)
   else:break
  return N(name,props,kids),end
 p=27;allnodes=[]
 while p<len(data)-160:
  n,p=node(p)
  if n:allnodes.append(n)
  else:break
 return allnodes

def arr(x):
 ty,n,b=x;f={'f':'f','d':'d','i':'i','l':'q','b':'B','c':'B'}[ty]
 return struct.unpack('<'+f*n,b)
if __name__=='__main__':
 nodes=fbx_load('/mnt/data/RW_OctoSupport_XL_INTERMEDIATE.fbx')
 print('top',[(n.name,len(n.p),len(n.ch)) for n in nodes]);o=next(n for n in nodes if n.name=='Objects')
 from collections import Counter
 print('object types',Counter((n.name,n.p[2] if len(n.p)>2 else '') for n in o.ch))
 print('object samples')
 for n in o.ch[:34]:print(n.name, n.p[:3],len(n.ch))
 cs=next(n for n in nodes if n.name=='Connections')
 print('conn',len(cs.ch),cs.ch[:5] and [x.p for x in cs.ch[:8]])
 g=[n for n in o.ch if n.name=='Geometry']
 print('geometry',len(g));print('geom sample',[(x.name,x.p[:3],[(y.name, y.p[0][1] if y.p and isinstance(y.p[0],tuple) else str(y.p)[:30]) for y in x.ch[:8]]) for x in g[:2]])
 print('geometry names', [x.p[1] for x in g[:45]])
 print('materials',[(x.p[:3]) for x in o.ch if x.name=='Material'])
