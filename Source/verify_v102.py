"""Verify release config, clear hollow bore, and preservation of original assets.

Usage: python Source/verify_v102.py --baseline-zip <v1.0.1 player zip>
These checks do not replace KSP editor, flight and persistence testing.
"""
import argparse, json, math, re, zipfile
from pathlib import Path
from read_mu import Reader

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'GameData/RoosterWorksStationSupport'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline-zip', type=Path, required=True)
args = parser.parse_args()

def number(cfg, key):
    return float(re.search(r'^    '+key+r' = ([\d.]+)$', cfg, re.M)[1])

def variant(cfg, name):
    match = re.search(r'\bVARIANT\s*\{\s*name = '+name+r'\b(.+?)GAMEOBJECTS\s*\{(.+?)\}', cfg, re.S)
    assert match
    return match[1], match[2]

assert len(list((GAME/'Parts').glob('*.cfg'))) == 10
assert len(list((GAME/'Models').glob('*.mu'))) == 10
with zipfile.ZipFile(args.baseline_zip) as base:
    for cfg_path in sorted((GAME/'Parts').glob('*.cfg')):
        part = cfg_path.stem
        hollow = part.endswith('_Hollow')
        original = part.removesuffix('_Hollow')
        cfg = cfg_path.read_text(encoding='utf-8')
        old = base.read(f'GameData/RoosterWorksStationSupport/Parts/{original}.cfg').decode('utf-8')
        assert cfg.count('{') == cfg.count('}')
        assert f'name = {part}\n' in cfg
        assert f'/Models/{part}\n' in cfg
        assert cfg.count('node_stack_') == 2
        for line in old.splitlines():
            if 'node_stack_' in line or 'node_attach =' in line: assert line in cfg
        path = GAME/'Models'/f'{part}.mu'
        mu = Reader(path)
        assert mu.name == part
        for node in mu.nodes:
            assert all(math.isfinite(x) for k in ('pos','rot','scale') for x in node[k])
            if 'size' in node: assert all(x > 0 for x in node['size'])
        for mesh in mu.meshes:
            assert 0 < len(mesh['verts']) < 65535
            assert len(mesh['verts']) == len(mesh['normals']) == len(mesh['uv'])
            assert all(0 <= i < len(mesh['verts']) for tri in mesh['tris'] for i in tri)
            assert all(math.isfinite(v) for vert in mesh['verts'] for v in vert)
            assert 0 <= mesh['material'] < len(mu.materials)
        if not hollow:
            assert path.read_bytes() == base.read(f'GameData/RoosterWorksStationSupport/Models/{part}.mu')
        if 'Adapter' in part:
            assert cfg == old, 'Adapter config changed'
        else:
            for name, active in [('Open','false'), ('Armored','true')]:
                values, objects = variant(cfg, name)
                delta = float(re.search(r'cost = ([\d.]+)', values)[1])
                assert math.isclose(delta, 0 if name == 'Open' else number(cfg, 'cost')*.1)
                assert f'ArmorPanels = {active}' in objects
                oldmass=float(re.search(r'mass = ([\d.]+)', variant(old, name)[0])[1])
                assert float(re.search(r'mass = ([\d.]+)', values)[1]) == oldmass
            if hollow:
                assert 'RESOURCE' not in cfg and 'EquipmentCollider' not in path.read_bytes().decode('latin1')
                assert number(cfg,'mass') == number(old,'mass')*.5
                assert number(cfg,'cost') == number(old,'cost')*.5
                clearance = .46 if 'Hex' in part else 1.0
                # A cylinder of this radius must fit from end to end with no mesh in it.
                # Minimum triangle distance in XZ includes face interiors, not only vertices.
                def dist_segment(a,b):
                    ax,az=a[0],a[2]; dx,dz=b[0]-ax,b[2]-az
                    t=max(0,min(1,-(ax*dx+az*dz)/(dx*dx+dz*dz))) if dx*dx+dz*dz else 0
                    return math.hypot(ax+t*dx,az+t*dz)
                def tri_distance(a,b,c):
                    cross=lambda u,v: u[0]*v[2]-u[2]*v[0]
                    signs=[cross(a,b),cross(b,c),cross(c,a)]
                    area=(b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])
                    if abs(area)>1e-12 and (min(signs)>=0 or max(signs)<=0): return 0
                    return min(dist_segment(a,b),dist_segment(b,c),dist_segment(c,a))
                minradius=min(tri_distance(*(mesh['verts'][i] for i in tri))
                              for mesh in mu.meshes for tri in mesh['tris'])
                assert minradius > clearance, (part,minradius)
                for node in mu.nodes:
                    if 'size' not in node: continue
                    x,y,z=node['pos']; sx,sy,sz=node['size']
                    if node['name'].startswith('RadialFaceCollider_'):
                        assert math.hypot(x,z)-sz/2 > clearance
                    else:
                        assert math.hypot(max(0,abs(x)-sx/2),max(0,abs(z)-sz/2)) > clearance
                # Preserved frame meshes are a strict subset of the original source geometry.
                oldmu=Reader(GAME/'Models'/f'{original}.mu')
                def faces(model, armor):
                    return {(m['material'],tuple(m['verts'][i] for i in tri))
                            for m in model.meshes if model.armored(m)==armor for tri in m['tris']}
                assert faces(mu,True)==faces(oldmu,True), 'Armor geometry changed'
                assert faces(mu,False)<faces(oldmu,False), 'Hollow frame changed or interior not removed'
                print(f'PASS {part}: clear bore diameter > {clearance*2:g} m; frame/armor preserved; no resources')
            else:
                for key in ('mass','cost','entryCost'): assert number(cfg,key)==number(old,key)
                assert re.findall(r'RESOURCE\s*\{[^{}]*\}',cfg)==re.findall(r'RESOURCE\s*\{[^{}]*\}',old)
        print(f'PASS {part}: MU structure, mesh indices, nodes, prices and config')
    for path in (GAME/'Models').glob('*.png'):
        assert path.read_bytes()==base.read(f'GameData/RoosterWorksStationSupport/Models/{path.name}')
version=json.loads((GAME/'RoosterWorksStationSupport.version').read_text())
assert version['VERSION']==dict(MAJOR=1,MINOR=0,PATCH=2,BUILD=0)
# Demonstrate the axis issue for a sideways girder: vessel Y negates longitudinal X;
# parent local Y (world X) retains the longitudinal position under 180-degree rotation.
for position in (-2.0,-.5,0,.5,2.0):
    point=(position,1,0)
    vessel=(-point[0],point[1],-point[2])
    parent=(point[0],-point[1],-point[2])
    assert parent[0] == point[0]
    assert (vessel[0]==point[0]) == (position==0)
print('PASS unchanged original models/textures/resources, version, and symmetry-axis math')
print('NOT RUN: KSP VAB/flight/save-load tests. Use Parent radial symmetry on rotated girders.')
