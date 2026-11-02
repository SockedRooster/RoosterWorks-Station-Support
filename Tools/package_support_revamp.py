from pathlib import Path
import hashlib,json,zipfile,time
from low_impact import limit_worker
limit_worker(1)
R=Path(__file__).resolve().parents[1]
report=json.loads((R/'Reports/SUPPORT_REVAMP_01.json').read_text());assert report['status'].startswith('PASS')
files=sorted(p for p in R.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.build-deps','__pycache__')) and p.suffix not in ('.pyc','.blend1') and p.name!='CHECKSUMS-SHA256.txt')
(R/'CHECKSUMS-SHA256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in files))
for kind in ('Install','Developer-Source'):
    target=R.parent/(f'RoosterWorks-Station-Support-v1.0.8-{kind}.zip' if kind=='Developer-Source' else 'RoosterWorks-Station-Support-v1.0.8.zip')
    selected=files+[R/'CHECKSUMS-SHA256.txt'] if kind=='Developer-Source' else [p for p in files if p.is_relative_to(R/'GameData') or p.name in ('README.md','RELEASE_NOTES.md','LICENSE')]
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p in selected:
            z.write(p,p.relative_to(R).as_posix());time.sleep(.025)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for p in selected:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
    print(target.name,round(target.stat().st_size/1024**2,1),'MiB; all files verified',flush=True)
