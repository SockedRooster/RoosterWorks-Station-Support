"""Add a grey armor group without changing any existing model bytes.

Reads original MU assets from the v1.0.2 player ZIP. No re-export of the existing
geometry is needed. This is the canonical release model build, preserving manual
adjustments in the prior release that the older FBX converter may not reproduce.
"""
from pathlib import Path
import argparse, zipfile, struct
from read_mu import Reader
ROOT=Path(__file__).resolve().parents[1]
MODELS=ROOT/'GameData/RoosterWorksStationSupport/Models'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-zip',type=Path,required=True)
args=p.parse_args()
def string(s):
    b=s.encode(); assert len(b)<128
    return bytes([len(b)])+b
with zipfile.ZipFile(args.baseline_zip) as z:
    for name in z.namelist():
        if not name.endswith('.mu'): continue
        data=z.read(name); model=Reader(data)
        armor=next((n for n in model.nodes if n['name']=='ArmorPanels'),None)
        if armor and 'Adapter' not in name:
            begin,end=armor['start'],armor['end']
            edits=[(0,len(string('ArmorPanels')),string('ArmorPanelsGrey'))]
            for mesh in model.meshes:
                n=mesh['node']
                if n['parent'] is not armor: continue
                edits.append((n['start']-begin,len(string(n['name'])),string(n['name'].replace('Armor_','GreyArmor_',1))))
                if mesh['material']==2:
                    edits.append((mesh['material_offset']-begin,4,struct.pack('<i',0)))
            grey=data[begin:end]
            for offset,length,replacement in sorted(edits,reverse=True):
                grey=grey[:offset]+replacement+grey[offset+length:]
            result=data[:end]+struct.pack('<i',0)+grey+data[end:]
            Reader(result)
        else: result=data
        (MODELS/Path(name).name).write_bytes(result)
        print('Built',Path(name).name)
