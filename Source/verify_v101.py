#!/usr/bin/env python3
"""Offline structural and regression checks for RoosterWorks Station Support v1.0.1."""
from pathlib import Path
import json, struct, hashlib, re, zipfile, argparse
ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'GameData'/'RoosterWorksStationSupport'
PARSER=argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--baseline-zip',type=Path,default=ROOT.parent/'RoosterWorks-Station-Support-v1.0.0.zip', help='optional previous-release player ZIP for exact regression checks')
BASE = PARSER.parse_args().baseline_zip
if not BASE.exists():
    print('INFO: No v1.0.0 baseline ZIP found; cross-version binary comparison skipped.')
SPECS={
 'RW_OctoSupport_XL':(3.2,.8,9000,1500,8),
 'RW_OctoSupport_Medium':(1.85,.4625,4500,750,8),
 'RW_HexSupport_Long':(.76,.19,1200,200,6),
 'RW_HexSupport_Medium':(.42,.105,600,100,6),
 'RW_Octo25_Adapter':(.28,None,None,None,8),
 'RW_Hex125_Adapter':(.14,None,None,None,6),
}

def variant_block(cfg, name):
    m=re.search(r'\bVARIANT\s*\{\s*name\s*=\s*'+name+r'\s*(.*?)\n\s*GAMEOBJECTS',cfg,re.S)
    assert m, name
    return m.group(1)

assert len(list((GAME/'Parts').glob('*.cfg')))==6
assert len(list((GAME/'Models').glob('*.mu')))==6
from contextlib import nullcontext
with (zipfile.ZipFile(BASE) if BASE.exists() else nullcontext(None)) as z:
    for part,(dry,extra,ec,mp,n) in SPECS.items():
        cfg=(GAME/'Parts'/f'{part}.cfg').read_text()
        baseline=(z.read(f'GameData/RoosterWorksStationSupport/Parts/{part}.cfg').decode() if z else '')
        mu=(GAME/'Models'/f'{part}.mu').read_bytes()
        orig=(z.read(f'GameData/RoosterWorksStationSupport/Models/{part}.mu') if z else b'')
        assert mu[:8]==struct.pack('<ii',76543,5),part
        assert len(mu)>500_000,part
        assert cfg.count('{')==cfg.count('}'),part
        assert cfg.count('node_stack_')==2 and 'node_attach = ' in cfg,part
        assert 'attachRules = 1,1,1,1,0' in cfg,part
        assert f'mass = {dry}' in cfg,part
        assert mu.count(b'RadialFaceCollider_')==n,(part,mu.count(b'RadialFaceCollider_'))
        # All rendered geometry and original collider entries precede the new
        # radial faces; verify exact binary match through the start of old collider.
        marker=(b'RailCollider_00' if extra is not None else b'AdapterCollider')
        assert marker in mu
        if z:
            assert marker in orig
            assert mu[:mu.index(marker)]==orig[:orig.index(marker)],f'legacy model changed before colliders: {part}'
        assert b'ArmorPanels' in mu or extra is None,part
        if extra is not None:
            assert 'baseMass = 0' in cfg and 'baseCost = 0' in cfg
            assert re.search(r'\bmass\s*=\s*0\b',variant_block(cfg,'Open'))
            assert re.search(r'\bmass\s*=\s*'+str(extra)+r'\b',variant_block(cfg,'Armored'))
            assert f'amount = {ec}' in cfg and f'maxAmount = {ec}' in cfg
            assert f'amount = {mp}' in cfg and f'maxAmount = {mp}' in cfg
            for word in ('ArmorPanels = false','ArmorPanels = true'):
                assert word in cfg,part
            assert 'MODULE\n    {\n        name = ModulePartVariants' in cfg
        # The resource blocks are unchanged.
            
        else:
            assert 'ModulePartVariants' not in cfg and 'RESOURCE' not in cfg
        # Core stack node data retained.
        if z:
            for line in baseline.splitlines():
                if 'node_stack_' in line:
                    assert line in cfg,part
        print(f'PASS {part}: {n} radial colliders, unchanged visible geometry prefix, config')
    # No accidental texture changes.
    for png in (GAME/'Models').glob('*.png'):
        if z:
            baseline=z.read('GameData/RoosterWorksStationSupport/Models/'+png.name)
            assert baseline == png.read_bytes(), f'Texture changed: {png.name}'
version=json.loads((GAME/'RoosterWorksStationSupport.version').read_text())
assert version['VERSION']=={'MAJOR':1,'MINOR':0,'PATCH':1,'BUILD':0}
assert (ROOT/'LICENSE').read_text().startswith('MIT License')
meta=json.loads((ROOT/'CKAN'/'RoosterWorksStationSupport.netkan').read_text())
assert meta['identifier']=='RoosterWorksStationSupport'
assert 'asset_match/' in meta['$kref']
print('PASS v1.0.1 version, stable part IDs, source metadata' + (', unchanged textures' if BASE.exists() else ''))
print('NOTE: Invisible collider raycasts and live variant mass behavior require KSP VAB/flight testing.')
