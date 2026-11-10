"""Equip the three released couplers with a stock switchable docking light and EC."""
from pathlib import Path
import copy, io, json, math, os, sys, zipfile

out=Path(__file__).resolve().parent
workspace=out.parent
sdk=workspace/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path[:0]=[str(sdk/'Tools'),str(sdk/'Source'),str(sdk/'.build-deps')]
from low_impact import limit_worker
limit_worker(1)
from PIL import Image
from support_art import Batch,node,emit,lathe,np
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump

source=workspace/'Support-Docking-04/RoosterWorks-Station-Support-v1.0.10-test.4-Install.zip'
with zipfile.ZipFile(source) as archive:files={p:archive.read(p) for p in archive.namelist()}
prefix='GameData/RoosterWorksStationSupport/'
work=out/'Build';work.mkdir(exist_ok=True)
mask=io.BytesIO();Image.new('RGBA',(4,4),'white').save(mask,format='PNG')
files[prefix+'Models/rwss_docking_emission.png']=mask.getvalue()

for ident,diameter,capacity,draw,reach in [('125',1.25,25,.01,8),('250',2.5,50,.02,12),('375',3.75,100,.04,16)]:
    name='RWG_Docking_'+ident
    path=work/(name+'.mu');model_path=prefix+'Models/'+path.name
    path.write_bytes(files[model_path]);model=load(path);original=copy.deepcopy(model.root)
    scale=diameter/2.5
    paint=next(m for m in model.materials if m['name']=='RWSS_white')['properties']['_MainTex']
    emissive=copy.deepcopy(paint);emissive['index']=len(model.textures)
    model.textures.append(dict(name='rwss_docking_emission',type=0))
    model.materials.append(dict(name='RWSS_dockLens',shader='KSP/Emissive/Diffuse',properties={
        '_MainTex':paint,'_Color':(.70,.74,.76,1.),'_Emissive':emissive,'_EmissiveColor':(0.,0.,0.,1.)}))
    batch=Batch()
    # A recessed diffuser has a forward face and a chamfer visible from the side.
    for key,profile in [('frame',[(.176,.770),(.176,.718),(.148,.706),(.117,.706),(.117,.770)]),
                        ('dockLens',[(.181,.757),(.181,.718),(.148,.703),(.132,.703)])]:
        lathe(batch[key],[(y*scale,r*scale) for y,r in profile],segments=96)
    emit(model,model.root,'DockLighting',batch)
    lens=next(n for n in model.root['children'] if n['name']=='DockLighting_dockLens_0')
    lens['name']='RW_DockingDiffuser'
    face=next(n for n in original['children'] if n['name']=='DockFace')
    lamp=node('RW_DockingApproachLight')
    lamp['position']=(0,.165*scale,0);lamp['rotation']=face['rotation']
    lamp['light']=dict(type=0,intensity=1.35,range=reach,color=(1.,.96,.87,1.),cullingMask=-1,spotAngle=68.)
    model.root['children'].append(lamp)
    write(model,path);export=load(path);files[model_path]=path.read_bytes()
    cfgpath=prefix+'Parts/'+name+'.cfg'
    part=parse(files[cfgpath].decode()).children[0]
    part.set('description',part.get('description')+f' The inner docking light has steady and blinking modes and a {capacity} EC battery.')
    part.set('mass',round(float(part.get('mass'))+capacity*.00005,6))
    part.set('cost',float(part.get('cost'))+round(capacity*.8))
    light=Node('MODULE',list(dict(name='ModuleLight',lightName=lamp['name'],lightMeshRendererName=lens['name'],
        castLight='true',useAnimationDim='false',useAutoDim='true',lightBrightenSpeed='3',lightDimSpeed='3',useResources='true',resourceAmount=str(draw),
        isOn='false',isBlinking='false',canBlink='true',blinkMin='0.2',blinkMax='2',blinkRate='1',
        lightR='1',lightG='.96',lightB='.87',disableColorPicker='true').items()))
    part.children.append(light)
    part.children.append(Node('RESOURCE',[('name','ElectricCharge'),('amount',str(capacity)),('maxAmount',str(capacity))]))
    files[cfgpath]=dump(part).encode()
    cfg=parse(files[cfgpath].decode()).children[0]
    switch=next(n for n in cfg.children if n.get('name')=='ModuleLight')
    nodes={n['name']:n for _,n in walk(export.root)}
    assert export.root['children'][:len(original['children'])]==original['children']
    target=nodes[switch.get('lightName')];glow=nodes[switch.get('lightMeshRendererName')]
    assert target['rotation']==nodes['DockFace']['rotation'] and target['light']['type']==0 and target['light']['range']==reach
    assert export.materials[glow['materials'][0]]['shader']=='KSP/Emissive/Diffuse'
    vs=np.array(glow['mesh']['vertices']);assert vs[:,1].max()<nodes['DockFace']['position'][1]
    angles=np.unique(np.round(np.arctan2(vs[:,0],vs[:,2])%(2*math.pi),5))
    assert np.diff(np.r_[angles,angles[0]+2*math.pi]).max()<.066
    assert switch.get('useAutoDim')=='true'
    # The full front annulus must face the approaching vessel and sit above its carrier.
    tris=np.asarray(glow['mesh']['submeshes'][0]);front=vs[tris]
    front=front[np.all(abs(front[:,:,1]-.181*scale)<1e-6,axis=1)]
    assert len(front)==192 and (np.cross(front[:,1]-front[:,0],front[:,2]-front[:,0])[:,1]>0).all()
    norms=np.asarray(glow['mesh']['normals']);assert (norms[abs(vs[:,1]-.181*scale)<1e-6,1]>0).all()
    carrier=nodes['DockLighting_frame_0']['mesh']['vertices'];assert max(v[1] for v in carrier)<.181*scale
    assert switch.get('canBlink')=='true' and switch.get('useResources')=='true'
    resources=[r for r in cfg.children if r.header=='RESOURCE']
    assert len(resources)==1 and resources[0].get('name')=='ElectricCharge' and int(resources[0].get('amount'))==int(resources[0].get('maxAmount'))==capacity
    print(name,capacity,'EC;',draw,'EC/s;',reach,'m; exported lens, light and docking transform verified.')
vf=prefix+'RoosterWorksStationSupport.version';meta=json.loads(files[vf]);meta['VERSION']['BUILD']=6
files[vf]=(json.dumps(meta,indent=2)+'\n').encode()
files[prefix+'INSTALL.txt']=files[prefix+'INSTALL.txt'].replace(b'v1.0.10-test.4',b'v1.0.10-test.6')+b'\nDocking couplers include a warm-white approach light and battery. Turn the light on in the part menu or Lights action group, then enable Blink and adjust the rate in the part menu.\n'
result=out/'RoosterWorks-Station-Support-v1.0.10-test.6-Install.zip'
tmp=result.with_suffix('.partial')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for p,v in sorted(files.items()):archive.writestr(p,v)
with zipfile.ZipFile(tmp) as archive:
    assert archive.testzip() is None and all(p.startswith(prefix) and archive.read(p)==v for p,v in files.items())
os.replace(tmp,result)
