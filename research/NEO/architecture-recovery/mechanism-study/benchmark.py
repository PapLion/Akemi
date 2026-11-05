"""Run after the learning matrix: full-vocabulary forward/backward CPU comparison."""
import sys,json,time,statistics,resource,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch
from variants import build,VARIANTS
from capacity_control import build_control
from hybrid import build_hybrid
from experiment import optimizer
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
def run():
 results=[]
 for arm in VARIANTS+['capacity_transformer','event_fast','delta_fast']:
  for context,batch in [(64,8),(128,1),(256,1)]:
   m=build_control(17) if arm=='capacity_transformer' else (build_hybrid(arm,17) if arm.endswith('_fast') else build(arm,17));op=optimizer(m);g=torch.Generator().manual_seed(101);x=torch.randint(1,120,(batch,context),generator=g);y=torch.full((batch,),48)
   def step():
    op.zero_grad();torch.nn.functional.cross_entropy(m(x)[:,-1],y).backward();op.step()
   for _ in range(2):step()
   times=[]
   for _ in range(5):
    t=time.perf_counter();step();times.append(time.perf_counter()-t)
   counts={'linear_flops':0,'linear_calls':0};handles=[]
   def hook(module,args,out):
    counts['linear_flops']+=2*args[0].numel()*module.out_features;counts['linear_calls']+=1
   for module in m.modules():
    if isinstance(module,torch.nn.Linear):handles.append(module.register_forward_hook(hook))
   with torch.no_grad():m(x)
   for h in handles:h.remove()
   # F.linear tied output head is not a module; all positions are computed in this reference API.
   head=2*batch*context*32*8192;attention=4*batch*context*context*32*len(m.blocks)
   results.append({'arm':arm,'context':context,'batch':batch,'precision':'FP32','threads':1,'seconds':times,'median_update_ms':statistics.median(times)*1000,'answer_targets_per_s':batch/statistics.median(times),'input_ids_per_s':batch*context/statistics.median(times),'parameters':sum(p.numel() for p in m.parameters()),'trainable':sum(p.numel() for p in m.parameters() if p.requires_grad),'linear_calls':counts['linear_calls'],'forward_linear_flops':counts['linear_flops'],'tied_head_flops':head,'attention_matmul_flops_estimate':attention,'accounted_forward_flops':counts['linear_flops']+head+attention,'slow_writes_per_doc':0 if arm in ['transformer','no_ice','capacity_transformer'] else (context//2 if arm=='chunk2' else ((context+7)//8 if arm in ['event','delta','event_fast','delta_fast'] else context)),'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024})
   print(arm,context,round(results[-1]['median_update_ms'],2),flush=True)
 (R/'results/benchmark.json').write_text(json.dumps({'hardware':platform.uname()._asdict(),'torch':torch.__version__,'results':results,'notes':'CPU only; no concurrent learning. Answer targets/s != dense LM tokens/s. FLOPs exclude nonlinearities, normalization, optimizer and backward; backward ~2x forward is only a planning approximation. Peak RSS process cumulative.'},indent=2))
if __name__=='__main__':run()
