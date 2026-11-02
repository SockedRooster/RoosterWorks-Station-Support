from pathlib import Path
import hashlib, re, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
GD=ROOT/'GameData/RoosterWorksStationSupport'
parts=GD/'Parts';models=GD/'Models'
expected={
 'RW_OctoSupport_XL':('9000','1500',True),
 'RW_OctoSupport_Medium':('4500','750',True),
 'RW_HexSupport_Long':('1200','200',True),
 'RW_HexSupport_Medium':('600','100',True),
 'RW_Octo25_Adapter':(None,None,False),
 'RW_Hex125_Adapter':(None,None,False),
}
assert len(list(parts.glob('*.cfg')))==6
assert len(list(models.glob('*.mu')))==6
for name,(ec,mono,panels) in expected.items():
 p=parts/(name+'.cfg');m=models/(name+'.mu')
 txt=p.read_text();b=m.read_bytes()
 assert txt.count('{')==txt.count('}')
 assert re.search(r'(?m)^\s*name = '+name+r'\s*$',txt)
 assert 'RoosterWorksStationSupport/Models/'+name in txt
 assert txt.count('node_stack_')==2
 assert b[:8]==(76543).to_bytes(4,'little')+(5).to_bytes(4,'little')
 assert len(b)>500000
 if panels:
  assert 'ArmorPanels = false' in txt and 'ArmorPanels = true' in txt
  assert ('maxAmount = '+ec) in txt and ('maxAmount = '+mono) in txt
 else:
  assert 'RESOURCE' not in txt and 'ModulePartVariants' not in txt
 print('PASS',name,round(len(b)/1e6,2),'MB')
assert (GD/'RoosterWorksStationSupport.version').exists()
print('PASS all six parts and assets; KSP in-game checks still required')
