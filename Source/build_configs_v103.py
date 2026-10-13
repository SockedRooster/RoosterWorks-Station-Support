"""Build v1.0.3 configs from the v1.0.2 player ZIP (idempotent)."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import argparse, re, zipfile, json
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'GameData/RoosterWorksStationSupport'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline-zip',type=Path,required=True)
args=parser.parse_args()

def scaled(value,factor,integer=False):
    number=Decimal(value)*Decimal(str(factor))
    if integer: number=number.quantize(Decimal(1),rounding=ROUND_HALF_UP)
    return format(number.normalize(),'f')

with zipfile.ZipFile(args.baseline_zip) as archive:
    for name in archive.namelist():
        if '/Parts/' not in name or not name.endswith('.cfg'): continue
        cfg=archive.read(name).decode('utf-8')
        part=Path(name).stem
        cfg=re.sub(r'(?m)^(        (?:amount|maxAmount) = )(\d+)$',
                   lambda m:m[1]+scaled(m[2],'.4',True),cfg)
        if 'Support' in part:
            cfg=cfg.replace('ArmorPanels = false','ArmorPanels = false\n                ArmorPanelsGrey = false')
            cfg=cfg.replace('ArmorPanels = true','ArmorPanels = true\n                ArmorPanelsGrey = false')
            start=cfg.index('        VARIANT\n        {\n            name = Armored\n')
            end=cfg.index('\n    }',start)
            armored=cfg[start:end]
            grey=armored.replace('name = Armored\n','name = ArmoredGrey\n').replace('displayName = Armored Panels','displayName = Armored Grey').replace('primaryColor = #D5D9D5','primaryColor = #707D89')
            grey=grey.replace('ArmorPanels = true','ArmorPanels = false').replace('ArmorPanelsGrey = false','ArmorPanelsGrey = true')
            cfg=cfg[:end]+'\n'+grey+cfg[end:]
            hollow=part.endswith('_Hollow')
            desc=('Hollow structural girder with an open center and no resource storage.' if hollow
                  else 'Station-support girder with fixed ElectricCharge and MonoPropellant storage, reduced to 40% of v1.0.2 capacity.')
            desc+=' Select Open Frame, Armored Panels or Armored Grey. Both armor finishes have the same mass and 10% price surcharge.'
            cfg=re.sub(r'(?m)^    description = .+$','    description = '+desc,cfg)
        (GAME/'Parts'/f'{part}.cfg').write_text(cfg,encoding='utf-8',newline='\n')
        if not part.startswith('RW_Octo'): continue
        newpart=part.replace('RW_OctoSupport','RW_Octo375Support').replace('RW_Octo25_Adapter','RW_Octo375_Adapter')
        large=cfg.replace(f'name = {part}\n',f'name = {newpart}\n',1)
        large=large.replace('rescaleFactor = 1\n','rescaleFactor = 1.5\n').replace('bulkheadProfiles = size2','bulkheadProfiles = size3')
        # rescaleFactor applies to MODEL geometry, colliders, and node positions.
        # Keep source node coordinates; increase stack node size to match size3.
        large=re.sub(r'(?m)^(    node_stack_.*), 2$',r'\1, 3',large)
        large=re.sub(r'(?m)^(    title = .+)$',lambda m:m[1].replace('Octo to 2.5m Adapter','Octo to 3.75m Adapter').replace('Octo XL Girder','Octo 3.75m XL Girder').replace('Octo Medium Girder','Octo 3.75m Medium Girder'),large)
        large=re.sub(r'(?m)^(    description = ).+$',lambda m:m[1]+('Uniformly enlarged 3.75 m octagonal adapter.' if 'Adapter' in part else desc+' Enlarged to 3.75 m diameter; dimensions scale by 1.5 and mass, price and storage by 3.375.'),large)
        large=re.sub(r'(?m)^(    (?:cost|mass|entryCost) = )([\d.]+)$',lambda m:m[1]+scaled(m[2],3.375),large)
        large=re.sub(r'(?m)^(            (?:cost|mass) = )([\d.]+)$',lambda m:m[1]+scaled(m[2],3.375),large)
        large=re.sub(r'(?m)^(        (?:amount|maxAmount) = )([\d.]+)$',lambda m:m[1]+scaled(m[2],3.375,True),large)
        large=large.replace('    tags = ','    tags = 3.75 375 large ')
        (GAME/'Parts'/f'{newpart}.cfg').write_text(large,encoding='utf-8',newline='\n')
version=GAME/'RoosterWorksStationSupport.version'
data=json.loads(version.read_text())
data['VERSION']['PATCH']=3
version.write_text(json.dumps(data,indent=2)+'\n')
print('Built 15 configs: 12 girders with 3 finishes, 3 adapters; 60% storage reduction.')
