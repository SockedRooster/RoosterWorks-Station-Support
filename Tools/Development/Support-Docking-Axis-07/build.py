"""Give stock SAS and the docking module their own, coaxial reference frames."""
from pathlib import Path
import copy
import json
import os
import sys
import zipfile

out = Path(__file__).resolve().parent
workspace = out.parent
sdk = workspace / 'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0] = [str(sdk/'Tools'), str(sdk/'Source'), str(sdk/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
import numpy as np
from native_model import load, walk
from native_derivatives import write
from support_art import node
from config_nodes import parse, dump

def rotate(q, v):
    xyz = np.array(q[:3])
    return v + 2 * np.cross(xyz, np.cross(xyz, v) + q[3] * v)

source = workspace/'Support-Docking-Lights-06/RoosterWorks-Station-Support-v1.0.10-test.6-Install.zip'
with zipfile.ZipFile(source) as z:
    files = {p:z.read(p) for p in z.namelist()}
prefix = 'GameData/RoosterWorksStationSupport/'
work = out/'Build'
work.mkdir(exist_ok=True)
for size in ('125','250','375'):
    name = 'RWG_Docking_'+size
    asset = prefix+'Models/'+name+'.mu'
    cfg = prefix+'Parts/'+name+'.cfg'
    path = work/(name+'.mu')
    path.write_bytes(files[asset])
    model = load(path)
    old_children = copy.deepcopy(model.root['children'])
    face = next(n for n in old_children if n['name']=='DockFace')
    control = node('DockControl')
    control['position'] = face['position']
    model.root['children'].append(control)
    write(model,path)
    files[asset] = path.read_bytes()
    part = parse(files[cfg].decode('utf-8')).children[0]
    docking = next(n for n in part.children if n.get('name')=='ModuleDockingNode')
    assert docking.get('nodeTransformName')==docking.get('controlTransformName')=='DockFace'
    docking.set('controlTransformName','DockControl')
    files[cfg] = dump(part).encode('utf-8')
    exported = load(path)
    assert exported.root['children'][:-1]==old_children
    nodes = {n['name']:n for _,n in walk(exported.root)}
    part = parse(files[cfg].decode()).children[0]
    module = next(n for n in part.children if n.get('name')=='ModuleDockingNode')
    target = nodes[module.get('nodeTransformName')]
    helm = nodes[module.get('controlTransformName')]
    port = np.array([float(x) for x in part.get('node_stack_top').split(',')])
    assert np.allclose(target['position'],port[:3]) and helm['position']==target['position']
    target_axis = rotate(target['rotation'],np.array([0.,0.,1.]))
    control_axis = rotate(helm['rotation'],np.array([0.,1.,0.]))
    assert np.allclose(target_axis,port[3:6],atol=1e-6)
    assert np.allclose(control_axis,target_axis,atol=1e-6)
    print(name,'target and control axes agree at the docking face')

vf = prefix+'RoosterWorksStationSupport.version'
meta = json.loads(files[vf]);meta['VERSION']['BUILD'] = 7
files[vf] = (json.dumps(meta,indent=2)+'\n').encode()
doc = prefix+'INSTALL.txt'
files[doc] = files[doc].replace(b'v1.0.10-test.6',b'v1.0.10-test.7')
files[doc] += b'\nFor SAS docking, select Control From Here on your own coupler, Set as Target on the receiving port, then select SAS Target. Target mode points at the selected port along the line of sight.\n'
result = out/'RoosterWorks-Station-Support-v1.0.10-test.7-Install.zip'
tmp = result.with_suffix('.partial')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for p,v in sorted(files.items()):z.writestr(p,v)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None and all(p.startswith(prefix) and z.read(p)==v for p,v in files.items())
os.replace(tmp,result)
