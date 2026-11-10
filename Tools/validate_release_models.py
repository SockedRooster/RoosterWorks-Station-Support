"""Run the current model regression suite with one low-priority worker."""
from pathlib import Path
import sys,json,runpy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'Tools'))
from low_impact import limit_worker
limit_worker(1)
meta=json.loads((R/'RELEASE_METADATA.json').read_text())
script='validate_hub_fix.py' if meta['addon'].endswith('Modules') else 'validate_support_revamp.py'
runpy.run_path(str(R/'Tools'/script),run_name='__main__')
