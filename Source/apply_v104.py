"""Apply v1.0.4 changes after the v1.0.3 config/model builders.

Optional --baseline-zip verifies the complete game-data delta against v1.0.3.
Only two storage configs, the version file, and one compatibility patch change.
"""
from pathlib import Path
import argparse, re, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'GameData/RoosterWorksStationSupport'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-zip',type=Path)
args=p.parse_args()
specs={'RW_Octo375Support_Medium':{'ElectricCharge':3949,'MonoPropellant':658},
       'RW_Octo375Support_XL':{'ElectricCharge':7898,'MonoPropellant':1316}}
for part,resources in specs.items():
    path=GAME/'Parts'/f'{part}.cfg'
    cfg=path.read_text(encoding='utf-8')
    for resource,capacity in resources.items():
        pattern=r'(name = '+resource+r'\s+amount = )\d+(\s+maxAmount = )\d+'
        cfg,count=re.subn(pattern,lambda m:m[1]+str(capacity)+m[2]+str(capacity),cfg)
        assert count==1
    desc='3.75 m station-support girder with fixed ElectricCharge and MonoPropellant storage. Capacity is reduced a further 35% from v1.0.3, rounded to whole units. Select Open Frame, Armored Panels or Armored Grey. Both armored finishes have the same mass and 10% price surcharge.'
    cfg=re.sub(r'(?m)^    description = .+$','    description = '+desc,cfg)
    path.write_text(cfg,encoding='utf-8',newline='\n')
parts=sorted(path.stem for path in (GAME/'Parts').glob('*.cfg'))
assert len(parts)==15
compat=GAME/'Compatibility'
compat.mkdir(exist_ok=True)
patch='''// Station Modules adds ModuleRWStationFinish to RW_* during its FOR pass.
// Station Support already has Open / Armored / ArmoredGrey stock variants.
// Remove only that extra finish module from these exact Station Support IDs.
// Requires ModuleManager only when the Station Modules compatibility is used.
'''
for part in parts:
    patch+=f'\n@PART[{part}]:AFTER[RoosterWorksStationModules]\n{{\n    !MODULE[ModuleRWStationFinish],* {{ }}\n}}\n'
(compat/'RemoveExtraExteriorFinish.cfg').write_text(patch,encoding='utf-8',newline='\n')
version=GAME/'RoosterWorksStationSupport.version'
data=json.loads(version.read_text()); data['VERSION']['PATCH']=4
version.write_text(json.dumps(data,indent=2)+'\n')
report=['v1.0.4 configuration verification',
        '3.75 m Medium: EC 3949, MonoPropellant 658 (initial fill and capacity).',
        '3.75 m XL: EC 7898, MonoPropellant 1316 (initial fill and capacity).',
        'These values are 65% of v1.0.3 amounts, rounded to nearest whole unit.',
        'Compatibility patch targets exactly 15 Station Support part IDs after the Station Modules FOR pass.',
        'Patch deletes only ModuleRWStationFinish; ModulePartVariants remains intact.']
if args.baseline_zip:
    allowed={f'Parts/{part}.cfg' for part in specs}|{'RoosterWorksStationSupport.version'}
    changed=set()
    with zipfile.ZipFile(args.baseline_zip) as z:
        for name in z.namelist():
            prefix='GameData/RoosterWorksStationSupport/'
            if not name.startswith(prefix): continue
            relative=name.removeprefix(prefix)
            now=(GAME/relative).read_bytes(); old=z.read(name)
            if now!=old:
                changed.add(relative)
                assert relative in allowed, f'Unexpected change: {relative}'
            if relative in {f'Parts/{part}.cfg' for part in specs}:
                strip=lambda s:re.sub(r'(?m)^    description = .+\n|^        (?:amount|maxAmount) = .+\n','',s)
                assert strip(now.decode())==strip(old.decode()), 'Non-resource config changed'
                for resource in specs[Path(relative).stem]:
                    values=re.search(r'name = '+resource+r'\s+amount = (\d+)\s+maxAmount = (\d+)',now.decode())
                    assert values[1]==values[2]==str(specs[Path(relative).stem][resource])
        assert changed==allowed
        previous={n.removeprefix('GameData/RoosterWorksStationSupport/') for n in z.namelist() if n.startswith('GameData/RoosterWorksStationSupport/')}
        current={p.relative_to(GAME).as_posix() for p in GAME.rglob('*') if p.is_file()}
        assert current-previous=={'Compatibility/RemoveExtraExteriorFinish.cfg'}
        assert not previous-current
    report+=['PASS: exactly the intended three existing files changed; one compatibility patch added.',
             'PASS: all models, textures, armor variants, costs/masses, and other 13 part configs match v1.0.3 exactly.']
report+=['NOT RUN: live ModuleManager/KSP reload, VAB or flight verification. Existing saved resource values may need part replacement.']
(ROOT/'VALIDATION_v104.txt').write_text('\n'.join(report)+'\n',encoding='utf-8')
print('\n'.join(report))
