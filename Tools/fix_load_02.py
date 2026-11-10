"""Repair dev.1 loader tables without rebuilding or rendering geometry."""
from pathlib import Path
import sys,json,re
from low_impact import limit_worker
limit_worker(1)
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'Tools'),str(R/'Source'),str(R/'.build-deps')]
from native_model import load
from native_derivatives import write
GD=R/'GameData/RoosterWorksStationSupport'
audit=[]
for f in sorted((GD/'Models').glob('*.mu')):
    old=load(f)
    write(old,f)
    new=load(f)
    assert old.root==new.root and old.materials==new.materials and old.name==new.name
    assert old.textures[:len(new.textures)]==new.textures
    audit.append(dict(model=f.name,before=len(old.textures),after=len(new.textures),geometry_unchanged=True))
    print(f.name,len(old.textures),'->',len(new.textures),flush=True)
changes=[]
for f in sorted((GD/'Parts').glob('*.cfg')):
    content=f.read_text()
    def integer(m):
        value=str(int(float(m[2])+.5))
        if value!=m[2]:changes.append(dict(part=f.stem,old=m[2],new=value))
        return m[1]+value
    content=re.sub(r'(?m)^(\s*entryCost\s*=\s*)([\d.]+)',integer,content)
    f.write_text(content)
version=GD/'RoosterWorksStationSupport.version'
data=json.loads(version.read_text());data['VERSION']['BUILD']=2
version.write_text(json.dumps(data,indent=2)+'\n')
(R/'Reports/LOAD_FIX_02.json').write_text(json.dumps(dict(models=audit,integer_corrections=changes,runtime_verified=False),indent=2)+'\n')
for name in ('README.md','RELEASE_NOTES.md','SUPPORT_REVAMP_01.md'):
    f=R/name
    if f.exists():f.write_text(f.read_text().replace('v1.0.8-dev.1','v1.0.8-dev.2'))
