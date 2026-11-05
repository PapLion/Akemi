"""Short final CPU measurement, run after corpus scan has completed."""
import f2,json,time,statistics,resource,platform,os
from pathlib import Path
out=f2.ROOT/'results';report={}
for kind in ['F2','Transformer']:
 cases=[]
 for T in f2.P['contexts']:
  m=f2.make(kind);o=f2.opt(m)
  for u in range(2):f2.update(m,o,u,T)
  rows=[f2.update(m,o,u,T) for u in range(2,7)];rate=sum(r['targets'] for r in rows)/(sum(r['update_ms'] for r in rows)/1000)
  t=time.perf_counter();f2.snapshot(out/f'{kind}-isolated-{T}.pt',m,o,7,kind);save=time.perf_counter()-t;t=time.perf_counter();f2.restore(out/f'{kind}-isolated-{T}.pt');restore=time.perf_counter()-t
  cases.append({'context':T,'batch':2,'warmup_updates':2,'measured_updates':5,'targets_per_second':rate,'mean_update_ms':statistics.mean(r['update_ms'] for r in rows),'stdev_update_ms':statistics.stdev(r['update_ms'] for r in rows),'mean_forward_ms':statistics.mean(r['forward_ms'] for r in rows),'mean_backward_ms':statistics.mean(r['backward_ms'] for r in rows),'mean_adamw_clip_ms':statistics.mean(r['adamw_and_clip_ms'] for r in rows),'checkpoint_seconds':save,'restore_seconds':restore,'compute_only_5M_hours':5e6/rate/3600,'planning_5M_hours_with_30pct_allowance':1.3*5e6/rate/3600,'rows':rows})
 report[kind]={'cases':cases,'process_peak_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'parameters':sum(p.numel() for p in m.parameters())}
(out/'f2-benchmark-isolated.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
