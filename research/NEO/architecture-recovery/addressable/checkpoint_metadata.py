"""Add accurate experiment metadata as new files; preserve original run checkpoints."""
from pathlib import Path
import hashlib,torch,json
from run_addressable import O
for p in [O/'resume-check.pt',O/'microfit.pt',O/'main.pt']:
 s=torch.load(p,weights_only=True,map_location='cpu');old=dict(s['config']);s['inherited_recipe_config']=old
 s['config']=dict(old,updates=300,variant='addressable-v1',address_init_seed=707,state_shape=[8,32],write_policy='observed =/! records; deterministic unit delta',key_path='shared input embedding projection',reader='query-key delta read + address_out + historical read/fast/head')
 s['source_checkpoint_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();torch.save(s,p.with_suffix('.certified.pt'))
print('3 new certified metadata copies; original files retained. Model/optimizer/RNG unchanged.')
