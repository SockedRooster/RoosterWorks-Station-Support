#!/usr/bin/env python3
"""Rebuild all six Station Support .mu models from the approved FBX sources.

For v1.0.1, unchanged rendered mesh data is preserved while the invisible
radial attachment collider ring is added to each model.
Needs numpy, scipy and pillow; run after installing `requirements.txt`.
"""
import argparse
from pathlib import Path
from convert_station_fbx import main as convert_one

ROOT = Path(__file__).resolve().parents[2]
FIVE = ROOT / 'Source' / 'FiveFBXExports'
XL = ROOT / 'Source' / 'Blender' / 'Approved_OctoXL_INTERMEDIATE.fbx'
NAMES = ('RW_OctoSupport_XL','RW_OctoSupport_Medium','RW_HexSupport_Long',
         'RW_HexSupport_Medium','RW_Octo25_Adapter','RW_Hex125_Adapter')

def run(five_dir=FIVE):
    target = ROOT/'GameData'/'RoosterWorksStationSupport'/'Models'
    for part in NAMES:
        path = XL if part=='RW_OctoSupport_XL' else Path(five_dir)/f'{part}_INTERMEDIATE.fbx'
        if not path.is_file(): raise FileNotFoundError(path)
        print(f'\n--- {part} ---')
        convert_one(path,part,target)
    print('\nSUCCESS: regenerated 6 .mu models with radial face colliders.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fbx-dir',type=Path,default=FIVE,
                        help='folder containing the approved five exported FBX files')
    run(parser.parse_args().fbx_dir)
