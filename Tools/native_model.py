"""Strict reader for the native MU subset emitted by this source kit.

Reads Unity coordinates unchanged. Unsupported record types fail explicitly.
"""
import struct
from pathlib import Path

class Reader:
    def __init__(self,path):
        self.data=Path(path).read_bytes();self.pos=0
        self.materials=[];self.textures=[]
    def take(self,fmt,count=1):
        n=struct.calcsize('<'+fmt)*count
        values=struct.unpack_from('<'+fmt*count,self.data,self.pos);self.pos+=n
        return values[0] if count==1 else values
    def text(self):
        length=0;shift=0
        while True:
            b=self.take('B');length|=(b&127)<<shift
            if b<128:break
            shift+=7
            assert shift<=28
        result=self.data[self.pos:self.pos+length].decode('utf-8');self.pos+=length
        return result
    def mesh(self):
        assert self.take('i')==13
        count,submeshes=self.take('i',2);m={}
        while True:
            tag=self.take('i')
            if tag==22:break
            if tag in (14,15,16,17,18,32):
                key,n={14:('vertices',3),15:('uvs',2),16:('uv2',2),17:('normals',3),18:('tangents',4),32:('colors',4)}[tag]
                m[key]=[self.take('f',n) for _ in range(count)]
            elif tag==19:
                n=self.take('i');assert n%3==0
                m.setdefault('submeshes',[]).append([self.take('i',3) for _ in range(n//3)])
            else:raise ValueError(('Unsupported mesh record',tag,self.pos))
        assert len(m['submeshes'])==submeshes
        return m
    def node(self):
        n={'name':self.text(),'position':self.take('f',3),'rotation':self.take('f',4),'scale':self.take('f',3),'children':[]}
        while self.pos<len(self.data):
            tag=self.take('i')
            if tag==1:break
            if tag==0:n['children'].append(self.node())
            elif tag==24:n['tag']=self.text();n['layer']=self.take('i')
            elif tag==7:n['mesh']=self.mesh()
            elif tag==8:
                n['shadows']=self.take('B',2);count=self.take('i')
                n['materials']=[self.take('i') for _ in range(count)]
            elif tag in (6,28):
                trigger=self.take('B') if tag==28 else 0
                n['collider']={'type':'box','trigger':trigger,'size':self.take('f',3),'center':self.take('f',3)}
            elif tag in (3,25):
                trigger=self.take('B') if tag==25 else 0
                convex=self.take('B')
                n['collider']={'type':'mesh','trigger':trigger,'convex':convex,'mesh':self.mesh()}
            elif tag==10:
                for _ in range(self.take('i')):
                    mat={'name':self.text(),'shader':self.text(),'properties':{}}
                    for _ in range(self.take('i')):
                        name=self.text();kind=self.take('i')
                        if kind in (0,1):value=self.take('f',4)
                        elif kind in (2,3):value=self.take('f')
                        elif kind==4:value={'index':self.take('i'),'scale':self.take('f',2),'offset':self.take('f',2)}
                        else:raise ValueError(('Unknown material property',kind))
                        mat['properties'][name]=value
                    self.materials.append(mat)
            elif tag==12:
                for _ in range(self.take('i')):self.textures.append({'name':self.text(),'type':self.take('i')})
            elif tag==23:
                n['light']={'type':self.take('i'),'intensity':self.take('f'),'range':self.take('f'),'color':self.take('f',4),'cullingMask':self.take('I'),'spotAngle':self.take('f')}
            else:raise ValueError(('Unsupported native record',tag,self.pos))
        return n
    def read(self):
        assert self.take('i',2)==(76543,5)
        self.name=self.text();self.root=self.node()
        assert self.pos==len(self.data)
        return self

def walk(n,path=''):
    path=path+'/'+n['name']
    yield path,n
    for child in n['children']:yield from walk(child,path)

def load(path):return Reader(path).read()
