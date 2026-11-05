"""Isolated CPU FP32 engineering timing. Run AFTER learning, never concurrently."""
import json,time,statistics,resource,platform
from pathlib import Path
import torch
import torch.nn.functional as F
import network,panel,learn
R=Path(__file__).resolve().parent
torch.set_num_threads(1)
def main():
 results=[];rows=panel.load('train')[:8];x,y=learn.batch(rows)
 cases=[(a,16) for a in network.ARMS]+[('transformer',0)]
 for arm,window in cases:
  m=network.build(arm,17,window);opt=network.optimizer(m);times=[]
  for i in range(14):
   t=time.perf_counter();opt.zero_grad(set_to_none=True);logits=m(x);f=time.perf_counter();loss=F.cross_entropy(logits[:,-1],y);loss.backward();b=time.perf_counter();torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True);opt.step();end=time.perf_counter()
   if i>=4:times.append({'forward_ms':1000*(f-t),'backward_ms':1000*(b-f),'clip_adamw_ms':1000*(end-b),'update_ms':1000*(end-t)})
  # Lower bound: dense linear matmuls only, excludes functional tied head,
  # attention, norms, nonlinearities and all backward/AdamW operations.
  linear=[0];handles=[]
  def hook(module,args,out):linear[0]+=2*args[0].numel()*module.out_features
  for mod in m.modules():
   if isinstance(mod,torch.nn.Linear):handles.append(mod.register_forward_hook(hook))
  with torch.no_grad():m(x)
  for h in handles:h.remove()
  means={k:statistics.mean(v[k] for v in times) for k in times[0]}
  results.append({'arm':arm,'window':window,'batch':8,'context_ids':64,'measured_updates':10,'warmup_updates':4,'targets_per_update':8,'input_ids_per_update':512,'targets_per_second':8000/means['update_ms'],'update_ms_sd':statistics.stdev(t['update_ms'] for t in times),'parameters':sum(p.numel() for p in m.parameters()),'active_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'forward_linear_flops_lower_bound':linear[0],'functional_head_flops':2*x.numel()*32*8192,'peak_rss_process_cumulative_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'timings':times,**means})
  print(arm,window,means['update_ms'],flush=True)
 (R/'results/cpu-performance.json').write_text(json.dumps({'torch':torch.__version__,'platform':platform.platform(),'threads':1,'precision':'FP32','results':results},indent=2))
if __name__=='__main__':main()
