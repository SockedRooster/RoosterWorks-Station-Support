#!/usr/bin/env python3
"""Convert all five Blender Station Support FBXs and make a complete KSP test ZIP.

Run after the Blender batch script completes. Needs numpy/scipy/pillow.
The Octo XL changes are limited to its battery orientation and badge offset; Octo Medium badge also moves.
"""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from convert_station_fbx import main as convert_one

NAMES = (
 'RW_OctoSupport_Medium', 'RW_HexSupport_Long', 'RW_HexSupport_Medium',
 'RW_Octo25_Adapter', 'RW_Hex125_Adapter',
)
ROOT=Path(__file__).resolve().parents[2]
DEFAULT=Path.home()/'Documents'/'RoosterWorks_Station_Support'/'BatchExports'

def run(fbx_dir=DEFAULT):
    folder=Path(fbx_dir).expanduser().resolve()
    model_dir=ROOT/'GameData'/'RoosterWorksStationSupport'/'Models'
    missing=[name for name in NAMES if not (folder/(name+'_INTERMEDIATE.fbx')).is_file()]
    if missing:
        raise FileNotFoundError('FBX files missing from '+str(folder)+'\n'+ '\n'.join('  '+name+'_INTERMEDIATE.fbx' for name in missing))
    # Approved Octo XL is rebuilt from its original FBX so only the badge mounting offset changes.
    original_fbx=ROOT/'DeveloperSource/Blender/Approved_OctoXL_INTERMEDIATE.fbx'
    if original_fbx.is_file():convert_one(original_fbx,'RW_OctoSupport_XL',model_dir)
    for name in NAMES:
        fbx=folder/(name+'_INTERMEDIATE.fbx')
        print('\n---',name,'---')
        convert_one(fbx,name,model_dir)
        output=model_dir/(name+'.mu')
        if not output.is_file() or output.stat().st_size<5000:
            raise AssertionError('Missing or implausibly small MU: '+str(output))
    assert (model_dir/'RW_OctoSupport_XL.mu').is_file()
    package=ROOT/'RoosterWorks-Station-Support-v0.8.4-SIX-PART-TEST.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as archive:
        for file in (ROOT/'GameData').rglob('*'):
            if file.is_file():archive.write(file,file.relative_to(ROOT))
    with ZipFile(package) as archive:
        assert archive.testzip() is None
        models=[x for x in archive.namelist() if x.endswith('.mu')]
        assert len(models)==6,models
    print('\nSUCCESS: six-part test ZIP:',package)
    print('Approved Octo XL: batteries and badge adjusted; Octo Medium badge adjusted; four other models unchanged.')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--fbx-dir',type=Path,default=DEFAULT)
    run(p.parse_args().fbx_dir)
