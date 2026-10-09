#!/usr/bin/env python3
"""Offline validation for RoosterWorks Station Support 1.0 release inputs."""
from pathlib import Path
from zipfile import ZipFile
import json, hashlib, struct, re
root=Path(__file__).resolve().parents[1]
gd=root/'GameData'/'RoosterWorksStationSupport'
expected={'RW_OctoSupport_XL':(9000,1500,'2'),
          'RW_OctoSupport_Medium':(4500,750,'2'),
          'RW_HexSupport_Long':(1200,200,'1'),
          'RW_HexSupport_Medium':(600,100,'1'),
          'RW_Octo25_Adapter':(None,None,'2'),
          'RW_Hex125_Adapter':(None,None,'1')}
assert len(list((gd/'Parts').glob('*.cfg')))==6
assert len(list((gd/'Models').glob('*.mu')))==6
for name,(ec,mono,node) in expected.items():
  cfg=(gd/'Parts'/f'{name}.cfg').read_text()
  mu=(gd/'Models'/f'{name}.mu').read_bytes()
  assert mu[:8]==struct.pack('<ii',76543,5)
  assert len(mu)>500000
  assert cfg.count('{')==cfg.count('}')
  assert f'name = {name}' in cfg
  assert f'RoosterWorksStationSupport/Models/{name}' in cfg
  assert cfg.count('node_stack_')==2
  assert f', {node}\n' in cfg
  if ec is not None:
    assert 'name = ModulePartVariants' in cfg
    assert 'ArmorPanels = false' in cfg and 'ArmorPanels = true' in cfg
    assert f'maxAmount = {ec}' in cfg and f'maxAmount = {mono}' in cfg
    assert 'name = ElectricCharge' in cfg and 'name = MonoPropellant' in cfg
  else:
    assert 'RESOURCE' not in cfg
  print('PASS',name,len(mu),'bytes')
ver=json.loads((gd/'RoosterWorksStationSupport.version').read_text())
assert ver['VERSION']=={'MAJOR':1,'MINOR':0,'PATCH':0,'BUILD':0}
assert (root/'LICENSE').read_text().startswith('MIT License')
meta=json.loads((root/'CKAN'/'RoosterWorksStationSupport.netkan').read_text())
assert meta['identifier']=='RoosterWorksStationSupport'
assert meta['install']==[{'find':'RoosterWorksStationSupport','install_to':'GameData'}]
assert 'asset_match/' in meta['$kref']
print('PASS release 1.0.0 version, license, CKAN draft, configs and six native models')
print('NOTE static tests do not substitute for KSP runtime tests')
