"""Combine the verified Support and expansion player packages into one addon folder."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import zipfile

root = Path(__file__).resolve().parent
workspace = root.parent
base = workspace / 'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9.zip'
expansion = root / 'RoosterWorks-Girder-Expansion-v0.1.0-test.1-Install.zip'
addon = 'RoosterWorksStationSupport'
prefix = 'GameData/' + addon + '/'
old_names = ('RoosterWorksGirderExpansion', 'RoosterWorksKerbalismSupport')
target = root / 'RoosterWorks-Station-Support-v1.0.10-test.1-Install.zip'
payload = {}

def add(path, data):
    if path in payload and payload[path] != data:
        raise ValueError('Conflicting assets at ' + path)
    payload[path] = data

with zipfile.ZipFile(base) as z:
    for path in z.namelist():
        if path.startswith(prefix) and not path.endswith('/'):
            add(path, z.read(path))
    add(prefix+'LICENSE', z.read('LICENSE'))

with zipfile.ZipFile(expansion) as z:
    for path in z.namelist():
        if not path.startswith('GameData/') or path.endswith('/'):
            continue
        _, old_folder, relative = path.split('/', 2)
        assert old_folder in old_names, path
        data = z.read(path)
        if relative == 'LifeSupport.cfg':
            relative = 'Compatibility/KerbalismLifeSupport.cfg'
        if relative.endswith('.cfg'):
            for folder in old_names:
                data = data.replace((folder+'/Models/').encode(), (addon+'/Models/').encode())
        add(prefix+relative, data)

version_path = prefix + addon + '.version'
version = json.loads(payload[version_path])
version['VERSION'] = dict(MAJOR=1, MINOR=0, PATCH=10, BUILD=1)
payload[version_path] = (json.dumps(version, indent=2)+'\n').encode()
parts = [data for path,data in payload.items() if path.startswith(prefix+'Parts/') and path.endswith('.cfg')]
ids = [re.search(rb'^\s*name\s*=\s*([^\s]+)', data, re.M)[1] for data in parts]
assert len(set(ids)) == len(ids) == 21
life = payload[prefix+'Compatibility/KerbalismLifeSupport.cfg']
assert life.count(b'@PART[') == life.count(b'B9_TANK_TYPE:NEEDS[') == 6
for path,data in payload.items():
    assert path.startswith(prefix)
    if path.endswith('.cfg'):
        assert all(folder.encode() not in data for folder in old_names)
        for model in re.findall(rb'^\s*model\s*=\s*([^\s]+)', data, re.M):
            assert 'GameData/'+model.decode()+'.mu' in payload, (path, model)

instructions = """RoosterWorks Station Support v1.0.10-test.1 (KSP 1.12.5)

Close KSP. Install the single GameData/RoosterWorksStationSupport folder into your game's GameData directory. This full install includes the base support parts, three girder adapters, three six-way hubs, and the Kerbalism life-support interiors for six straight girders.

If you installed an earlier test, move RoosterWorksGirderExpansion and RoosterWorksKerbalismSupport out of GameData before restarting. Replace the previous RoosterWorksStationSupport folder. These steps prevent duplicate parts and storage entries. Existing expansion part IDs and subtype names carry over.

Keep ModuleManager and B9PartSwitch installed. The life-support choices also require Kerbalism Default and Community Resource Pack. Select Storage on a main girder in the editor.
"""
add(prefix+'INSTALL.txt',instructions.encode())
temp = target.with_suffix('.partial')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for path,data in sorted(payload.items()):
        z.writestr(path,data)
with zipfile.ZipFile(temp) as z:
    assert {PurePosixPath(p).parts[:2] for p in z.namelist()} == {('GameData',addon)}
    assert z.testzip() is None
    for path,data in payload.items():
        assert z.read(path) == data
os.replace(temp,target)
print(target.name, 'verified:',len(payload),'files,',len(parts),'parts, 6 Kerbalism patches, one GameData addon folder.')
