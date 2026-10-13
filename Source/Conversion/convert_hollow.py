"""Build the four hollow models from the included, unmodified FBX references."""
from pathlib import Path
from convert_station_fbx import main

ROOT = Path(__file__).resolve().parents[2]
for part in ('RW_OctoSupport_XL', 'RW_OctoSupport_Medium',
             'RW_HexSupport_Long', 'RW_HexSupport_Medium'):
    source = (ROOT/'Source/Blender/Approved_OctoXL_INTERMEDIATE.fbx' if part.endswith('_XL')
              else ROOT/'Source/FiveFBXExports'/f'{part}_INTERMEDIATE.fbx')
    main(source, part, hollow=True)
