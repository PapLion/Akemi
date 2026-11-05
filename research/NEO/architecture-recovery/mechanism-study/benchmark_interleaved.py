"""Primary CPU cost: clipped AdamW, randomized interleaving to reduce order drift."""
import json,time,random,statistics,resource,torch
from pathlib import Path
from variants import build
from hybrid import build_hybrid
from capacity_control import build_control
from experiment import optimizer
R=Path(__file__).resolve().parent;torch.set_num_threads(1)
def main():
 output=[];orderlog=[]
 for context,b in [(64,8),(128,1),(256,1)]:
  cases={a:(build_hybrid(a,17) if a.endswith('_fast') else (build_control(17) if a=='capacity_transformer' else build(a,17))) for a in ['intact','capacity_transformer','event_fast','delta_fast']};opts={a:optimizer(m) for a,m in cases.items()};g=torch.Generator().manual_seed(101);x=torch.randint(1,120,(b,context),generator=g);y=torch.full((b,),48);records={a:[] for a in cases}
  def step(arm):
   m,o=cases[arm],opts[arm];t=time.perf_counter();o.zero_grad(set_to_none=True);z=m(x)[:,-1];loss=torch.nn.functional.cross_entropy(z,y);f=time.perf_counter();loss.backward();back=time.perf_counter();torch.nn.utils.clip_grad_norm_(m.parameters(),1,error_if_nonfinite=True);cl=time.perf_counter();o.step();end=time.perf_counter()
   return {'forward_ms':(f-t)*1000,'backward_ms':(back-f)*1000,'clip_ms':(cl-back)*1000,'adamw_ms':(end-cl)*1000,'update_ms':(end-t)*1000}
  for arm in cases:
   for _ in range(2):step(arm)
  rng=random.Random(20261031)
  for round in range(10):
   order=list(cases);rng.shuffle(order);orderlog.append({'context':context,'batch':b,'round':round,'order':order})
   for arm in order:records[arm].append(step(arm))
  for arm,samples in records.items():
   med=statistics.median(s['update_ms'] for s in samples);output.append({'arm':arm,'context':context,'batch':b,'seed':17,'dtype':'FP32','samples':samples,'median_update_ms':med,'median_forward_ms':statistics.median(s['forward_ms'] for s in samples),'median_backward_ms':statistics.median(s['backward_ms'] for s in samples),'median_clip_ms':statistics.median(s['clip_ms'] for s in samples),'median_adamw_ms':statistics.median(s['adamw_ms'] for s in samples),'targets_per_s':b*1000/med,'input_ids_per_s':b*context*1000/med,'coefficient_of_variation':statistics.stdev(s['update_ms'] for s in samples)/statistics.mean(s['update_ms'] for s in samples),'rss_peak_cumulative':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024})
 (R/'results/benchmark-interleaved.json').write_text(json.dumps({'torch':torch.__version__,'threads':1,'warmup_updates_per_model':2,'measured_updates':10,'clip':1,'optimizer':'AdamW original recipe','order_seed':20261031,'order':orderlog,'results':output,'scope':'CPU FP32 synthetic answer-only. No concurrent training jobs of this study. System processes not isolated. Does not certify dense LM or GPU throughput.'},indent=2))
if __name__=='__main__':main()
