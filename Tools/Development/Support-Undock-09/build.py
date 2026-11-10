"""Package the KRnD compatibility fix on the reverted test.7 baseline."""
from pathlib import Path
import json
import re
import zipfile

here = Path(__file__).resolve().parent
project = here.parent
base = project / "Support-Docking-Axis-07/RoosterWorks-Station-Support-v1.0.10-test.7-Install.zip"
destination = here / "RoosterWorks-Station-Support-v1.0.10-test.9-Install.zip"
prefix = "GameData/RoosterWorksStationSupport/"
with zipfile.ZipFile(base) as archive:
    files = {name: archive.read(name) for name in archive.namelist()}

# Use exact part IDs so another manufacturer's B9 tanks can still use their own patches.
ids = []
for path, data in files.items():
    if path.startswith(prefix + "Parts/") and path.endswith(".cfg"):
        if re.search(rb"(?m)^\s*moduleID = (SupportStorage|HubStorage)\s*$", data):
            ids.append(re.search(rb"(?m)^\s*name = (\w+)", data)[1].decode())
assert len(set(ids)) == len(ids) == 9
patch = "// B9 owns these parts' variable capacities. KRnD restores prefab capacity on vessel changes.\n"
for part_id in sorted(ids):
    patch += f"@PART[{part_id}]:NEEDS[KRnD]:AFTER[KRnD]\n{{\n    !MODULE[KRnDModule],* {{}}\n}}\n"
files[prefix + "Compatibility/KRnDStorage.cfg"] = patch.encode()
version_path = prefix + "RoosterWorksStationSupport.version"
version = json.loads(files[version_path])
version["VERSION"]["BUILD"] = 9
files[version_path] = (json.dumps(version, indent=2) + "\n").encode()
notes = prefix + "INSTALL.txt"
files[notes] = files[notes].replace(b"test.7", b"test.9") + (
    b"\nWith KRnD installed, the six storage girders and three storage hubs are excluded "
    b"from KRnD upgrades so their B9-selected batteries retain capacity across vessel changes.\n"
)
tmp = destination.with_suffix(".partial")
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
    for path, data in sorted(files.items()):
        archive.writestr(path, data)
with zipfile.ZipFile(tmp) as archive:
    assert archive.testzip() is None and set(archive.namelist()) == set(files)
    assert all(path.startswith(prefix) and archive.read(path) == data for path, data in files.items())
tmp.replace(destination)
print(destination.name)
