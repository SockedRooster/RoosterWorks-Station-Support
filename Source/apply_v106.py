"""Fix both Hex battery assemblies using source-verified vertex maps.

Run after apply_v105.py, or supply --baseline-zip <v1.0.5-player.zip>.
Reduces radial battery depth about the existing inner plane, preserving tank space.
"""
from pathlib import Path
import argparse,hashlib,json,math,struct,zipfile
from read_mu import Reader
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'GameData/RoosterWorksStationSupport'
MAP=ROOT/'Source/BatteryMaps'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-zip',type=Path)
args=p.parse_args()
baseline=zipfile.ZipFile(args.baseline_zip) if args.baseline_zip else None
hashes=json.loads((MAP/'baseline-sha256.json').read_text())
report=['v1.0.6 Hex battery clearance verification','Clearance target: 5 mm inside both white and grey armor.']
changed={'RoosterWorksStationSupport.version'}
for part in ('RW_HexSupport_Medium','RW_HexSupport_Long'):
    relative=f'Models/{part}.mu'
    olddata=baseline.read('GameData/RoosterWorksStationSupport/'+relative) if baseline else (GAME/relative).read_bytes()
    assert hashlib.sha256(olddata).hexdigest()==hashes[part], 'Vertex map requires original v1.0.5 model. Supply its player ZIP.'
    old=Reader(olddata); meshes={m['node']['name']:m for m in old.meshes}
    mapping=json.loads((MAP/f'{part}.json').read_text())
    armor=meshes['Armor_white_00']['verts']
    assert armor==meshes['GreyArmor_white_00']['verts']
    data=bytearray(olddata); selected={}; limits={}
    for face in range(6):
        theta=(face+.5)*math.tau/6; nx,nz=math.cos(theta),math.sin(theta)
        indices=[(name,i) for name,faces in mapping.items() for i in faces.get(f'{face+1:02}',[])]
        assert indices
        radii=[meshes[name]['verts'][i][0]*nx+meshes[name]['verts'][i][2]*nz for name,i in indices]
        plate=[x*nx+z*nz for x,y,z in armor if int((math.atan2(z,x)%math.tau)/(math.tau/6))==face]
        inner=min(plate); anchor=min(radii); outer=max(radii); target=inner-.005
        factor=(target-anchor)/(outer-anchor)
        assert 0<factor<1 and target>anchor
        limits[face]=(nx,nz,inner,anchor,target,indices)
        for name,i in indices:
            m=meshes[name]; selected.setdefault(name,set()).add(i)
            x,y,z=m['verts'][i]; r=x*nx+z*nz
            delta=anchor+(r-anchor)*factor-r
            struct.pack_into('<3f',data,m['verts_offset']+i*12,x+delta*nx,y,z+delta*nz)
            # Inverse-transpose normal transform for depth-only compression.
            ax,ay,az=m['normals'][i]; nr=ax*nx+az*nz
            correction=(1/factor-1)*nr
            ax+=correction*nx; az+=correction*nz
            length=math.sqrt(ax*ax+ay*ay+az*az)
            struct.pack_into('<3f',data,m['normals_offset']+i*12,ax/length,ay/length,az/length)
        report.append(f'{part} face {face+1}: original battery depth {1000*(outer-anchor):.2f} mm -> {1000*(target-anchor):.2f} mm; inner plane unchanged; 5.00 mm armor clearance.')
    new=Reader(bytes(data)); nm={m['node']['name']:m for m in new.meshes}
    for name,m in meshes.items():
        for key in ('tris','uv','material'): assert m[key]==nm[name][key]
        for i,(a,b) in enumerate(zip(m['verts'],nm[name]['verts'])):
            assert a[1]==b[1]
            if i not in selected.get(name,set()):
                assert a==b and m['normals'][i]==nm[name]['normals'][i]
    for face,(nx,nz,inner,anchor,target,indices) in limits.items():
        radii=[]
        for name,i in indices:
            a=meshes[name]['verts'][i]; b=nm[name]['verts'][i]
            radii.append(b[0]*nx+b[2]*nz)
            assert abs((-a[0]*nz+a[2]*nx)-(-b[0]*nz+b[2]*nx))<1e-7
            n=nm[name]['normals'][i]; assert abs(sum(x*x for x in n)-1)<1e-6
        assert abs(min(radii)-anchor)<1e-7
        assert min(radii)>=anchor-1e-7 and max(radii)<=target+1e-7
        assert inner-max(radii)>.0049999
        # The whole triangle is behind the same plane when all its vertices are.
    # Byte mask proves no unrelated model records (including colliders) changed.
    restored=bytearray(data)
    for name,ids in selected.items():
        for i in ids:
            for key in ('verts_offset','normals_offset'):
                at=meshes[name][key]+i*12
                restored[at:at+12]=olddata[at:at+12]
    assert bytes(restored)==olddata
    (GAME/relative).write_bytes(data); changed.add(relative)
    report.append(f'PASS {part}: only mapped battery vertices/normals changed; frame, tanks, armor, UVs, triangles and colliders preserved.')
version=GAME/'RoosterWorksStationSupport.version'
v=json.loads(version.read_text()); v['VERSION']['PATCH']=6
version.write_text(json.dumps(v,indent=2)+'\n')
if baseline:
    actual=set()
    for name in baseline.namelist():
        prefix='GameData/RoosterWorksStationSupport/'
        if not name.startswith(prefix): continue
        rel=name.removeprefix(prefix)
        if (GAME/rel).read_bytes()!=baseline.read(name): actual.add(rel)
    assert actual==changed,(actual,changed)
    baseline.close()
    report.append('PASS full release delta: exactly two Hex storage models and version metadata changed. All configurations, capacities, hollow/Octo/adapter models, finishes, textures and patches unchanged.')
report.append('NOT RUN: KSP rendering/flight. Clearance verified against shipped white and grey armor geometry.')
(ROOT/'VALIDATION_v106.txt').write_text('\n'.join(report)+'\n',encoding='utf-8')
print('\n'.join(report))
