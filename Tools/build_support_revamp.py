"""Support art, selectable tanks and central core. Native output; no game install writes."""
from low_impact import limit_worker
limit_worker(1)
from support_art import *
from native_model import load,walk
from native_derivatives import write
from config_nodes import Node,parse,dump
import json
GD=M.parent;BASE=R/'Source/RevampBaseline/GameData/RoosterWorksStationSupport'
SPECS={'RW_OctoSupport_XL':(8,2.5,4.75,4),'RW_OctoSupport_Medium':(8,2.5,2.65,2),'RW_HexSupport_Long':(6,1.25,3.15,4),'RW_HexSupport_Medium':(6,1.25,1.75,2),'RW_Octo25_Adapter':(8,2.5,.74,1),'RW_Hex125_Adapter':(6,1.25,.56,1)}
SERVICE_LANES=(math.tau/3,2*math.tau/3)
CORE_WIRE_OFFSETS={'blue':.065,'yellow':.18}
OUTER_WIRE_OFFSETS={'blue':.065,'yellow':.092}

def core_wire_point(d,a,key,y):
    return h.point(.28*d/2.5,a+CORE_WIRE_OFFSETS[key],y)

def harness_path(d,length,sign,a,key):
    s=d/2.5;half=length/2;inner=sign*(half-.19*s);seat=sign*(half-.055*s)
    # Shared trunk endpoint; smoothly fan out to the wider external cable lane.
    p0=np.array(core_wire_point(d,a,key,inner));p1=p0+np.array((0,sign*.10*s,0))
    p3=np.array(h.point(1.272*s,a+OUTER_WIRE_OFFSETS[key],seat))
    p2=np.array(h.point(.65*s,a+OUTER_WIRE_OFFSETS[key],seat))
    return [(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3 for t in np.linspace(0,1,17)]

def group(model,name,batch):
    parent=node(name);model.root['children'].append(parent);emit(model,parent,name,batch);return parent

def frame_radius(d,a):
    sides=6 if d<2 else 8;r=.47*d
    face=min([math.pi/2+(j+.5)*math.tau/sides for j in range(sides)],key=lambda t:abs((a-t+math.pi)%math.tau-math.pi))
    return r*math.cos(math.pi/sides)/math.cos(a-face)

def inner_wall(mesh,radius,lo,hi):
    wall=h.Mesh();h.cylinder_surface(wall,radius,lo,hi,segments=48);off=len(mesh.vertices)
    mesh.vertices.extend(wall.vertices);mesh.normals.extend(tuple(-v for v in n) for n in wall.normals);mesh.uvs.extend(wall.uvs);mesh.triangles.extend(tuple(i+off for i in reversed(t)) for t in wall.triangles)

def frame(model,n,d,length,bays,adapter=False):
    b=Batch();s=d/2.5;rr=d*.47;half=length/2;end=half-.055*s;ys=np.linspace(-end,end,bays+1)
    angles=[math.pi/2+j*math.tau/n for j in range(n)]
    for a in angles:
        out=np.array((math.sin(a),0,math.cos(a)));p=lambda y:np.array(h.point(rr,a,y))
        # Wide flanges around a recessed web; actual I-section silhouette.
        beam(b['frame'],p(-end),p(end),.060*s,.10*s,out)
        for radial in (-.045,.045):beam(b['steel'],p(-end)+out*radial*s,p(end)+out*radial*s,.115*s,.018*s,out)
        for yy in ys:
            terminal=abs(abs(yy)-end)<1e-6
            plate(b,p(yy)+out*.065*s,(math.cos(a),0,-math.sin(a)),(0,1,0),.15*s,(.10 if terminal else .17)*s,.022*s,'frame')
            for dy in ((-.028,.028) if terminal else (-.048,.048)):bolt(b,p(yy+dy*s)+out*.078*s,out,.024*s)
    for j,a in enumerate(angles):
        aa=angles[(j+1)%n];mid=(a+math.pi/n);out=np.array((math.sin(mid),0,math.cos(mid)));right=np.array((math.cos(mid),0,-math.sin(mid)))
        for yy in ys:beam(b['steel'],h.point(rr,a,yy),h.point(rr,aa,yy),.09*s,.09*s,(0,1,0))
        if not adapter:
            for lo,hi in zip(ys[:-1],ys[1:]):
                midy=(lo+hi)/2;center=rr*math.cos(math.pi/n)*out+np.array((0,midy,0))
                # Two crossed diagonal straps with thickness and capped endpoints.
                for a0,a1 in ((a,aa),(aa,a)):beam(b['steel'],h.point(rr,a0,lo),h.point(rr,a1,hi),.035*s,.025*s,out)
                plate(b,center+out*.022*s,right,(0,1,0),.14*s,.12*s,.025*s,'frame')
                for dx in (-.04,.04):bolt(b,center+right*dx*s+out*.039*s,out,.019*s)
                # A slim center stringer provides a mounting surface for external equipment.
            beam(b['frame'],rr*math.cos(math.pi/n)*out+np.array((0,-end,0)),rr*math.cos(math.pi/n)*out+np.array((0,end,0)),.034*s,.035*s,out)
        for yy in (-end,end):
            # Real end-ring mounting holes represented by recessed dark wells and bolt seats.
            for f in (.2,.8):
                p=np.array(h.point(rr,a,yy))*(1-f)+np.array(h.point(rr,aa,yy))*f
                bolt(b,p+(0,(.033 if yy>0 else -.033)*s,0),(0,1 if yy>0 else -1,0),.027*s)
    # Shared station interface: same angular lanes, radius and wire offsets.
    for a in (math.tau/3,2*math.tau/3):
        for key,da,rad in (('steel',0,.014),('blue',.065,.007),('yellow',.092,.007)):
            angle=a+da;radius=(1.30 if key=='steel' else 1.272)*s
            tube(b[key],h.point(radius,angle,-half),h.point(radius,angle,half),rad*s,12)
            for yy in ys:
                # Plane of the nearest polygon side, extending from its end/bay ring.
                faceangle=min([q+math.pi/n for q in angles],key=lambda t:abs((angle-t+math.pi)%math.tau-math.pi))
                skin=rr*math.cos(math.pi/n)/math.cos(angle-faceangle)
                tube(b['steel'],h.point(skin,angle,yy),h.point(radius,angle,yy),.012*s,8)
                bolt(b,h.point(skin+.010*s,angle,yy),(math.sin(angle),0,math.cos(angle)),.018*s)
    if adapter:
        # Octagonal/hexagonal ring around an open central passage.
        for yy in (-half+.015*s,half-.015*s):
            h.annulus(b['white'],d*.36,d*.49,yy,normal_sign=1 if yy>0 else -1,segments=64)
            lathe(b['frame'],[(yy-.010*s,d*.36),(yy+.010*s,d*.36)])
            for a in angles:
                seat=yy-(.025*s if yy>0 else -.025*s);beam(b['steel'],h.point(d*.36,a,seat),h.point(rr,a,seat),.07*s,.04*s,(0,1,0))
        h.cylinder_surface(b['white'],d*.49,-half+.015*s,half-.015*s,segments=64)
        inner_wall(b['frame'],d*.36,-half+.015*s,half-.015*s)
    if adapter:
        shell=b.meshes.pop('white')
        for key,parentname in (('white','Body_white_00'),('grey','Body_grey_00')):
            appearance=Batch();appearance.meshes[key]=shell;group(model,parentname,appearance)
    emit(model,model.root,'RWSS_Frame',b)
    if not adapter:
        for key,parentname in (('white','ArmorPanels'),('grey','ArmorPanelsGrey')):
            armor=Batch()
            for a in [q+math.pi/n for q in angles]:
                out=np.array((math.sin(a),0,math.cos(a)));right=(math.cos(a),0,-math.sin(a));width=2*rr*math.sin(math.pi/n)-.14*s
                for lo,hi in zip(ys[:-1],ys[1:]):
                    p=out*(rr*math.cos(math.pi/n)+.035*s)+np.array((0,(lo+hi)/2,0));height=hi-lo-.13*s
                    plate(armor,p,right,(0,1,0),width,height,.027*s,key)
                    # Narrow recessed edging, corner fasteners and service access panels.
                    for sign in (-1,1):beam(armor['frame'],p+np.array(right)*width*.47*sign+(0,-height*.45,0),p+np.array(right)*width*.47*sign+(0,height*.45,0),.016*s,.010*s,out)
                    for xx in (-.43,.43):
                        for yy in (-.43,.43):bolt(armor,p+np.array(right)*width*xx+np.array((0,height*yy,0))+out*.016*s,out,.019*s)
                    plate(armor,p+out*.018*s,right,(0,1,0),min(width*.65,.32*s),min(height*.40,.20*s),.015*s,'frame',3)
            group(model,parentname,armor)

def terminal_interface(b,d,length,core=False):
    """Common service mating collars, radial ties and blue/yellow end harness."""
    s=d/2.5;half=length/2;rad=.25*s
    for sign in (-1,1):
        face=sign*half;inner=sign*(half-.19*s);seat=sign*(half-.055*s)
        if not core:lathe(b['white'],sorted([(inner,rad),(face,rad)]))
        lathe(b['frame'],sorted([(sign*(half-.045*s),.30*s),(face,.30*s)]))
        h.annulus(b['steel'],rad-.025*s,.30*s,face,normal_sign=sign,segments=48)
        for a in (math.pi/2+j*math.tau/(6 if d<2 else 8) for j in range(6 if d<2 else 8)):
            beam(b['steel'],h.point(rad,a,seat),h.point(frame_radius(d,a),a,seat),.065*s,.05*s,(0,1,0))
        for a in SERVICE_LANES:
            for key in CORE_WIRE_OFFSETS:
                pts=harness_path(d,length,sign,a,key)
                for p,q in zip(pts,pts[1:]):tube(b[key],p,q,.007*s,12)

def battery_pack(model,d,length,full=False):
    s=d/2.5;b=Batch();rows=max(2,int((length-.30*s)/(.40*s)));pitch=(length-.40*s)/rows
    for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4):
        out=np.array((math.sin(a),0,math.cos(a)));right=np.array((math.cos(a),0,-math.sin(a)))
        for j in range(rows):
            y=-length/2+.20*s+pitch*(j+.5);p=out*((.75 if d<2 else .80)*s)+np.array((0,y,0))
            plate(b,p,right,(0,1,0),(.72 if d<2 else .86)*s,pitch*.93,.30*s,'frame',0)
            for dx in (-.24,.24):
                beam(b['steel'],p+right*dx*s+out*.155*s+(0,-pitch*.29,0),p+right*dx*s+out*.155*s+(0,pitch*.29,0),.018*s,.023*s,out)
                bolt(b,p+right*dx*s+out*.17*s+(0,pitch*.33,0),out,.016*s)
            for dx in (-.12,.12):tube(b['led'],p+right*dx*s+out*.151*s+(0,-pitch*.28,0),p+right*dx*s+out*.158*s+(0,-pitch*.28,0),.011*s,10)
            beam(b['steel'],out*.55*s+(0,y,0),p,.07*s,.06*s,out)
        # Mount banks to both end diaphragms; no unsupported floating battery faces.
        beam(b['frame'],out*.55*s+np.array((0,-length/2+.055*s,0)),out*.55*s+np.array((0,length/2-.055*s,0)),.07*s,.05*s,out)
        for y in (-length/2+.055*s,length/2-.055*s):beam(b['steel'],out*.55*s+np.array((0,y,0)),out*frame_radius(d,a)+np.array((0,y,0)),.065*s,.05*s,(0,1,0))
    if full:
        beam(b['black'],(0,-length/2+.19*s,0),(0,length/2-.19*s,0),.90*s,.90*s)
        for y in np.linspace(-length/2+.25*s,length/2-.25*s,rows):lathe(b['steel'],[(y-.012*s,.40*s),(y+.012*s,.40*s)])
    else:
        vessel(b,(0,0,0),.50*s,length-.40*s,'tank')
        for a in (0,math.pi):tube(b['bronze'],h.point(.52*s,a,-length/2+.2*s),h.point(.52*s,a,length/2-.2*s),.017*s,10)
    terminal_interface(b,d,length)
    return b

def tanks(d,length,xenon=False):
    s=d/2.5;b=Batch();volume=0
    if xenon:
        for a in (0,math.pi/2,math.pi,3*math.pi/2):
            center=h.point(.51*s,a,0);volume+=vessel(b,center,.35*s,length-.40*s,'tank')
            for y in (-length/2+.35*s,length/2-.35*s):beam(b['frame'],np.array(center)+(0,y,0),h.point(frame_radius(d,a),a,y),.055*s,.05*s,(0,1,0))
            for y in (-length/2+.14*s,length/2-.14*s):tube(b['bronze'],np.array(center)+(0,y,0),(0,y,0),.025*s,12)
    else:
        count=2 if length/d>1.7 else 1;cell=(length-.32*s)/count;radius=(.88 if d<2 else .96)*s
        for j in range(count):
            y=(j-(count-1)/2)*cell;volume+=vessel(b,(0,y,0),radius,cell-.08*s,'tank')
            for a in (0,math.pi/2,math.pi,3*math.pi/2):
                out=(math.sin(a),0,math.cos(a));right=(math.cos(a),0,-math.sin(a));p=np.array(h.point(radius+.018*s,a,y))
                plate(b,p,right,(0,1,0),.23*s,.15*s,.014*s,'frame',1)
                # Seat braces on the cylindrical belt, not outside the curved dome.
                belt=(cell-.08*s)/2-min(radius,(cell-.08*s)*.25)
                for dy in (-belt,belt):
                    beam(b['frame'],h.point(radius-.015*s,a,y+dy),h.point(frame_radius(d,a),a,y+dy),.10*s,.10*s,(0,1,0))
                    beam(b['steel'],h.point(frame_radius(d,a),a,y+dy),h.point(frame_radius(d,a),a,(-length/2+.055*s if dy<0 else length/2-.055*s)),.065*s,.065*s,(math.sin(a),0,math.cos(a)))
                    plate(b,h.point(radius+.022*s,a,y+dy),right,(0,1,0),.18*s,.14*s,.045*s,'steel')
            for a in (math.pi/4,5*math.pi/4):
                tube(b['bronze'],h.point(radius+.04*s,a,y-cell*.25),h.point(radius+.04*s,a,y+cell*.25),.014*s,10)
                for dy in (-cell*.25,cell*.25):tube(b['steel'],h.point(radius,a,y+dy),h.point(radius+.04*s,a,y+dy),.018*s,10)
    # Manifold and protected fill/drain valve blocks inside the structural ring.
    y=-length/2+.16*s
    for a in (0,math.pi/2,math.pi,3*math.pi/2):
        tube(b['steel'],(0,y,0),h.point(frame_radius(d,a),a,y),.035*s,12)
        p=h.point(.65*s,a,y);plate(b,p,(math.cos(a),0,-math.sin(a)),(0,1,0),.12*s,.12*s,.08*s,'bronze')
    terminal_interface(b,d,length)
    return b,volume

def service_core(model,d,length):
    s=d/2.5;b=Batch();rad=.25*s;half=length/2
    lathe(b['white'],[(-half,rad),(half,rad)])
    inner_wall(b['frame'],rad-.025*s,-half,half)
    for yy in (-half,half):h.annulus(b['steel'],rad-.025*s,rad,yy,normal_sign=1 if yy>0 else -1,segments=48)
    collars=np.linspace(-half+.07*s,half-.07*s,max(3,int(length/(.6*s))))
    for lo,hi in zip(collars[:-1],collars[1:]):
        for a in (0,math.pi/2,math.pi,3*math.pi/2):h.cylinder_surface(b['insulation'],rad+.004*s,lo+.045*s,hi-.045*s,segments=12,theta0=a+.24,theta1=a+math.pi/2-.24)
    for y in collars:
        lathe(b['frame'],[(y-.04*s,rad+.009*s),(y+.04*s,rad+.009*s)])
        for a in (0,math.pi/2,math.pi,3*math.pi/2):bolt(b,h.point(rad+.015*s,a,y),(math.sin(a),0,math.cos(a)),.020*s)
    for a in SERVICE_LANES:
        for key,delta in CORE_WIRE_OFFSETS.items():
            tube(b[key],core_wire_point(d,a,key,-half),core_wire_point(d,a,key,half),.010*s,12)
            for y in np.linspace(-half+.1*s,half-.1*s,max(3,int(length/(.5*s)))):tube(b['steel'],h.point(rad,a+delta,y),core_wire_point(d,a,key,y),.013*s,8)
    for y in (-half+.09*s,half-.09*s):
        h.annulus(b['steel'],rad-.025*s,rad+.055*s,y,normal_sign=1 if y>0 else -1,segments=32)
        for a in (0,math.pi/2,math.pi,3*math.pi/2):beam(b['steel'],h.point(rad,a,y),h.point(frame_radius(d,a),a,y),.06*s,.05*s,(0,1,0))
    for a in (0,math.pi):plate(b,h.point(rad+.018*s,a,0),(math.cos(a),0,-math.sin(a)),(0,1,0),.26*s,.19*s,.025*s,'frame',2)
    terminal_interface(b,d,length,core=True)
    parent=group(model,'RWSS_ServiceCore',b)
    co=node('RWSS_CoreCollider');co.update(collider=dict(type='box',trigger=0,size=(rad*1.4,length,rad*1.4),center=(0,0,0)));parent['children'].append(co)

def configs(volume_by_model):
    table=[]
    for path in sorted((BASE/'Parts').glob('*.cfg')):
        root=parse(path.read_text(encoding='utf-8-sig'));part=root.children[0];name=part.get('name');is_hollow=name.endswith('_Hollow');is_adapter='Adapter' in name
        part.set('entryCost',str(int(float(part.get('entryCost'))+.5)))
        if is_adapter:
            part.set('description','Reinforced transition ring with machined flanges, recessed fasteners and continuous blue/yellow service lines.');(GD/'Parts'/path.name).write_text(dump(root));continue
        model=next(n.get('model').split('/')[-1] for n in part.children if n.header=='MODEL');scale=float(part.get('rescaleFactor','1'));d=SPECS[model.replace('_Hollow','')][1]*scale;length=SPECS[model.replace('_Hollow','')][2]*scale
        if is_hollow:
            part.set('category','none');part.set('TechHidden','True')
            part.set('description','Detailed open structural truss. Select Empty Frame or Central Service Core with continuous blue/yellow wiring; armor finish remains independent. No stored resources.')
            sw=Node('MODULE',[('name','ModuleB9PartSwitch'),('moduleID','SupportInterior'),('switcherDescription','Interior'),('switchInFlight','false')])
            sw.children=[Node('SUBTYPE',[('name','Empty'),('title','Empty Frame'),('defaultSubtypePriority','1')]),Node('SUBTYPE',[('name','ServiceCore'),('title','Central Service Core'),('transform','RWSS_ServiceCore'),('addedMass',str(round(.04*length*d/2.5,4))),('addedCost',str(round(250*length*d/2.5)))])];part.children.append(sw)
        else:
            sw=next(n for n in part.children if n.header=='MODULE' and n.get('name')=='ModuleB9PartSwitch');sw.set('baseVolume',1);sw.set('switchInFlight','false');sw.set('affectDragCubes','true')
            for subtype in sw.children:
                if subtype.header=='SUBTYPE':subtype.set('transform','RWSS_'+subtype.get('name'))
            defs=parse((BASE/'Compatibility'/f'BatterySwitch_{name}.cfg').read_text());basekey=defs.children[0].get('name').removesuffix('_Standard')
            vol=volume_by_model[model]['tank']*scale**3;units=max(20,int(vol*200*.85/20)*20);xenon=max(100,int(volume_by_model[model]['xenon']*scale**3*200*10/100)*100)
            hollow=parse((BASE/'Parts'/(name+'_Hollow.cfg')).read_text()).children[0];structure=float(hollow.get('mass'));base_mass=float(part.get('mass'));base_cost=float(part.get('cost'))
            for key,title,extra_mass,extra_cost in [('Empty','Empty Frame',0,0),('ServiceCore','Central Service Core',.04*length*d/2.5,250*length*d/2.5)]:
                sub=Node('SUBTYPE',[('name',key),('title',title),('addedMass',str(round(structure+extra_mass-base_mass,5))),('addedCost',str(round(float(hollow.get('cost'))+extra_cost-base_cost,2)))])
                if key=='ServiceCore':sub.set('transform','RWSS_ServiceCore')
                sw.children.append(sub)
            for key,title,resources in [('LFO','Liquid Fuel / Oxidizer',{'LiquidFuel':units*.45,'Oxidizer':units*.55}),('LF','Liquid Fuel',{'LiquidFuel':units}),('Ox','Oxidizer',{'Oxidizer':units}),('Mono','Monopropellant',{'MonoPropellant':units}),('Xenon','Xenon Gas',{'XenonGas':xenon})]:
                tank=Node('B9_TANK_TYPE',[('name',basekey+'_'+key),('tankMass','0'),('tankCost','0')]);tank.children=[Node('RESOURCE',[('name',resource),('unitsPerVolume',str(round(amount,3)))]) for resource,amount in resources.items()];defs.children.append(tank)
                dry=structure+units*.000625*(1.3 if key=='Xenon' else 1)
                sub=Node('SUBTYPE',[('name',key),('title',title),('tankType',basekey+'_'+key),('transform','RWSS_XenonPack' if key=='Xenon' else 'RWSS_TankPack'),('addedMass',str(round(dry-base_mass,5))),('addedCost',str(round(float(hollow.get('cost'))+units*1.5-base_cost,2)))])
                sw.children.append(sub);table.append(dict(part=name,option=key,resources=resources,dry_mass_t=round(dry,5),tank_volume_m3=round(vol,4)))
            part.set('description','Station truss with Empty Frame, Central Service Core, EC + MonoPropellant, battery-only, LF/Ox, LF, oxidizer, monopropellant and xenon interiors in one Storage selector. Enlarged vessels and battery drawers mount to the frame. Common end collars and blue/yellow harnesses join stacked interiors. Armor finish is independent.')
            (GD/'Compatibility'/f'BatterySwitch_{name}.cfg').write_text(dump(defs))
        (GD/'Parts'/path.name).write_text(dump(root))
    return table

def main():
    volumes={};audit=[]
    for path in sorted((BASE/'Models').glob('*.mu')):
        model=load(path);key=path.stem.replace('_Hollow','');n,d,length,bays=SPECS[key];adapter='Adapter' in key;hollow=path.stem.endswith('_Hollow')
        if adapter:continue # Accepted adapter assets remain byte-for-byte unchanged.
        # Preserve all original external collision transforms. Equipment collision
        # moves with the resource interior rather than blocking an empty variant.
        colliders=[copy.deepcopy(n) for _,n in walk(model.root) if 'collider' in n];equipment=[n for n in colliders if n['name']=='EquipmentCollider'];model.root['children']=[n for n in colliders if n['name']!='EquipmentCollider'];materials(model)
        frame(model,n,d,length,bays,adapter)
        if not adapter:
            if not hollow:service_core(model,d,length)
            if hollow:service_core(model,d,length)
            else:
                for full in (False,True):
                    parent=group(model,'RWSS_Battery' if full else 'RWSS_Standard',battery_pack(model,d,length,full));parent['children'].extend(copy.deepcopy(equipment))
                    for c in parent['children']:
                        if c['name']=='EquipmentCollider':c['collider']=dict(type='box',trigger=0,size=(1.75*d/2.5,length-.30*d/2.5,1.75*d/2.5),center=(0,0,0))
                normal,vol=tanks(d,length);xenon,xvol=tanks(d,length,True);volumes[key]=dict(tank=vol,xenon=xvol)
                for name,batch in (('RWSS_TankPack',normal),('RWSS_XenonPack',xenon)):
                    parent=group(model,name,batch);co=node('RWSS_PressureCollider');co.update(collider=dict(type='box',trigger=0,size=(1.75*d/2.5,length-.30*d/2.5,1.75*d/2.5),center=(0,0,0)));parent['children'].append(co)
        write(model,M/path.name);audit.append(dict(model=path.name,meshes=sum('mesh' in n for _,n in walk(model.root)),triangles=sum(len(t) for _,n in walk(model.root) if 'mesh' in n for t in n['mesh']['submeshes'])))
        print(path.name,'complete',flush=True)
    table=configs(volumes)
    version=GD/'RoosterWorksStationSupport.version';data=json.loads(version.read_text());data['VERSION']=json.loads((R/'RELEASE_METADATA.json').read_text())['version_tuple'] if (R/'RELEASE_METADATA.json').exists() else dict(MAJOR=1,MINOR=0,PATCH=8,BUILD=4);version.write_text(json.dumps(data,indent=2)+'\n')
    meta=R/'CKAN/RoosterWorksStationSupport.netkan';data=json.loads(meta.read_text());data['depends']=[dict(name='ModuleManager'),dict(name='B9PartSwitch')];meta.write_text(json.dumps(data,indent=2)+'\n')
    (R/'Reports/SUPPORT_REVAMP_01.json').write_text(json.dumps(dict(status='Built; validation pending',models=audit,capacities=table,physical_volume=volumes),indent=2))

if __name__=='__main__':main()
