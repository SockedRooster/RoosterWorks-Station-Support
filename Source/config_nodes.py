"""Small ordered ConfigNode reader/writer for this source kit, not an MM engine."""
from dataclasses import dataclass,field
import re
@dataclass
class Node:
    header:str
    values:list=field(default_factory=list)
    children:list=field(default_factory=list)
    def get(self,key,default=None):return next((v for k,v in self.values if k==key),default)
    def set(self,key,value):
        for i,(k,v) in enumerate(self.values):
            if k==key:self.values[i]=(k,str(value));return
        self.values.append((key,str(value)))
def parse(text):
    root=Node('ROOT');stack=[root];pending=None
    text=re.sub(r'//[^\n]*','',text).replace('{','\n{\n').replace('}','\n}\n')
    for raw in text.splitlines():
        line=raw.strip()
        if not line:continue
        if line=='{':
            assert pending is not None
            node=Node(pending);stack[-1].children.append(node);stack.append(node);pending=None
        elif line=='}':
            assert len(stack)>1 and pending is None;stack.pop()
        elif '=' in line:
            key,value=line.split('=',1);stack[-1].values.append((key.strip(),value.strip()))
        else:
            assert pending is None,pending;pending=line
    assert len(stack)==1 and pending is None
    return root
def dump(node,depth=0):
    indent='    '*depth
    if node.header=='ROOT':return '\n'.join(dump(n,depth) for n in node.children)
    return indent+node.header+'\n'+indent+'{\n'+''.join(indent+'    '+k+' = '+v+'\n' for k,v in node.values)+''.join(dump(c,depth+1) for c in node.children)+indent+'}\n'
