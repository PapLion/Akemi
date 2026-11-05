"""Save final engineering environment and resource scope (no training)."""
import json,os,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import torch
R=Path(__file__).resolve().parent
repo=R.parent
out={'utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'torch':torch.__version__,'platform':platform.platform(),'cpu':platform.processor(),'device_used':'cpu','threads':1,'parent_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip(),'primary_trajectories':18,'policy_ablations':6,'updates_per_final_trajectory':1000,'response_targets_per_update':8,'tests':{'new':24,'inherited_mechanism':19,'inherited_foundation':22},'sealed_final_opened_for_evaluation':False,'independent_human_review':False,'gpu_used':False,'paid_services_used':False,'original_sources_modified':False}
(R/'results/final-environment.json').write_text(json.dumps(out,indent=2)+'\n')
print('Saved engineering scope')
