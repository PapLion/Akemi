"""CPU measurements independent of learning metrics; never rents or invokes CUDA."""
from contextlib import contextmanager
from pathlib import Path
import argparse,json,time,statistics,resource,os
import torch
from torch.profiler import profile,ProfilerActivity,record_function
from experiment import make_model,optimizer
from models import CryoNext,causal_loss
R=Path(__file__).resolve().parent
torch.set_num_threads(1)
@contextmanager
def region_instrumentation(m):
 timings={};originals=[]
 def wrap(obj,name,label):
  original=getattr(obj,name)
  def traced(*a,**k):
   start=time.perf_counter()
   with record_function(label):ret=original(*a,**k)
   timings.setdefault(label,[]).append(time.perf_counter()-start);return ret
  originals.append((obj,name,original));setattr(obj,name,traced)
 try:
  if isinstance(m,CryoNext):
   for name,label in [('_active','active/local'),('_summarize','trapos/summary'),('_read','hielo/read')]:wrap(m,name,label)
   for name in ['candidate','signals','key','value','control']:
    if hasattr(m,name):wrap(getattr(m,name),'forward','trapos/'+name)
  else:wrap(m,'hidden','historical/backbone')
  yield timings
 finally:
  for obj,name,original in originals:setattr(obj,name,original)

def step(m,op,x,parallel=False):
 op.zero_grad(set_to_none=True)
 with record_function('update/forward'):
  out=m(x,parallel=parallel) if isinstance(m,CryoNext) else m(x);logits=out.logits if hasattr(out,'logits') else out;loss=causal_loss(logits,x)
 with record_function('update/backward'):loss.backward()
 with record_function('update/adamw'):torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True);op.step()
 return out

def benchmark():
 records=[]
 for t in [64,128,256]:
  for b in [1,4]:
   torch.manual_seed(20261101);x=torch.randint(32,127,(b,t))
   for arm in ['b0_local','b0_full','cryo_history','event','delta','delta_scan']:
    m=make_model('delta' if arm=='delta_scan' else arm,chunk=32);op=optimizer(m)
    for _ in range(2):step(m,op,x,parallel=arm=='delta_scan')
    times=[]
    for _ in range(5):
     st=time.perf_counter();out=step(m,op,x,parallel=arm=='delta_scan');times.append(time.perf_counter()-st)
    records.append({'arm':arm,'length':t,'batch':b,'chunk':32,'parameters':sum(p.numel() for p in m.parameters()),'targets_per_update':b*(t-1),'seconds':times,'median_update_s':statistics.median(times),'targets_s':b*(t-1)/statistics.median(times),'rss_peak_process_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'stats':out.stats if hasattr(out,'stats') else {},'scope':'full-sequence LM engineering fixture; not answer-only learning throughput; cumulative RSS; same one-thread CPU, no GPU'})
    print(arm,t,b,round(records[-1]['targets_s'],1),flush=True)
    (R/'results/performance.json').write_text(json.dumps(records,indent=2))

def profiles():
 dest=R/'results/profiles';dest.mkdir(exist_ok=True)
 torch.manual_seed(20261101);x=torch.randint(32,127,(1,128));allrows=[]
 for arm in ['event','delta','cryo_history']:
  m=make_model(arm,chunk=32);op=optimizer(m);step(m,op,x)
  with region_instrumentation(m) as timings:
   with profile(activities=[ProfilerActivity.CPU],record_shapes=True,profile_memory=True) as p:step(m,op,x)
  p.export_chrome_trace(str(dest/(arm+'.json')))
  allrows.append({'arm':arm,'regions_cpu_s':{k:sum(v) for k,v in timings.items()},'region_calls':{k:len(v) for k,v in timings.items()},'operators':[{'key':e.key,'count':e.count,'self_cpu_us':e.self_cpu_time_total,'total_cpu_us':e.cpu_time_total,'self_memory_bytes':e.self_cpu_memory_usage} for e in p.key_averages()],'warning':'Nested regions overlap; instrumented times not pure throughput or additive attribution.'})
 (R/'results/profiling.json').write_text(json.dumps(allrows,indent=2))
 # Actual candidate skipping; untrained initialization, same fixed threshold from protocol.
 skip=[];m=make_model('event',chunk=32);m.eval()
 with torch.no_grad():
  for hard,threshold in [(False,.5),(True,.5),(True,1.)]:
   m.cfg.hard_threshold=threshold;times=[]
   for i in range(12):
    st=time.perf_counter();o=m(x,hard=hard)
    if i>=2:times.append(time.perf_counter()-st)
   skip.append({'hard':hard,'threshold':threshold,'median_forward_s':statistics.median(times),'stats':o.stats,'scope':'untrained engineering control; hard inference changes outputs and is not certified semantically equivalent to soft'})
 (R/'results/hard-skip.json').write_text(json.dumps(skip,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['bench','profile']);a=parser.parse_args();benchmark() if a.mode=='bench' else profiles()
