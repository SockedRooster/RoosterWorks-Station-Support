#!/usr/bin/env python3
"""Static integrity checks for RoosterWorks Station Support v0.8.4."""
from pathlib import Path
import json,struct
ROOT=Path(__file__).resolve().parents[1]
GD=ROOT/'GameData'/'RoosterWorksStationSupport'
expected={'RW_OctoSupport_XL':(9000,1500,True),
          'RW_OctoSupport_Medium':(4500,750,True),
          'RW_HexSupport_Long':(1200,200,True),
          'RW_HexSupport_Medium':(600,100,True),
          'RW_Octo25_Adapter':(None,None,False),
          'RW_Hex125_Adapter':(None,None,False)}
assert len(list((GD/'Parts').glob('*.cfg')))==6
assert len(list((GD/'Models').glob('*.mu')))==6
for name,(ec,mono,variant) in expected.items():
 cfg=(GD/'Parts'/f'{name}.cfg').read_text()
 mu=(GD/'Models'/f'{name}.mu').read_bytes()
 assert mu[:8]==struct.pack('<ii',76543,5)
 assert len(mu)>500000
 assert cfg.count('node_stack_')==2
 assert cfg.count('{')==cfg.count('}')
 assert f'name = {name}' in cfg
 if variant:
  assert 'ArmorPanels = true' in cfg and 'ArmorPanels = false' in cfg
  assert f'maxAmount = {ec}' in cfg and f'maxAmount = {mono}' in cfg
 else: assert 'RESOURCE' not in cfg
 print('PASS',name,round(len(mu)/1000000,2),'MB')
ver=json.loads((GD/'RoosterWorksStationSupport.version').read_text())['VERSION']
assert [ver['MAJOR'],ver['MINOR'],ver['PATCH']]==[0,8,4]
print('PASS six parts, resources, armor configs, adapter nodes and v0.8.4 metadata')
print('NOTE runtime KSP behavior needs in-game verification')
