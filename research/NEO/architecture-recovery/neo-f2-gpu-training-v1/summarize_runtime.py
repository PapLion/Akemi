"""Summarize observed logs and lifecycle receipts, without interpreting GPU utilization causally."""
from pathlib import Path
import json,statistics,datetime,re
R=Path(__file__).resolve().parent;O=R/'results'
def load(p):return json.loads(p.read_text())
def utc(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
summary={}
for kind in ['F2','Transformer']:
 p=O/(kind+'-curve.jsonl')
 if not p.exists():continue
 a=[json.loads(x) for x in p.read_text().splitlines()];ts=sorted(x['seconds'] for x in a)
 m=[json.loads(x) for x in (O/(kind+'-monitor.jsonl')).read_text().splitlines()]
 telemetry=[re.search(r'(\d+) %, (\d+) MiB',r.get('telemetry','')) for r in m];telemetry=[(int(t[1]),int(t[2])) for t in telemetry if t]
 summary[kind]=dict(sampled_gpu_utilization_mean_pct=statistics.mean(t[0] for t in telemetry),sampled_gpu_memory_max_MiB=max(t[1] for t in telemetry),maximum_logged_allocated_MiB=max(x['gpu_allocated'] for x in a)/2**20,updates=len(a),gradient_norm_median=statistics.median(x['gradient_norm'] for x in a),gradient_norm_max=max(x['gradient_norm'] for x in a),clipping_fraction=sum(x['clipped'] for x in a)/len(a),update_seconds_p50=statistics.median(ts),update_seconds_p95=ts[min(len(ts)-1,int(.95*len(ts)))],first_observed_utc=utc(m[0]['utc']) if 'utc' in m[0] else None,last_observed=m[-1])
(O/'runtime-diagnostics.json').write_text(json.dumps(summary,indent=2)+'\n')
plan=load(O/'rental-plan.json');cleanup=load(O/'cleanup.json')
timeline=dict(created_utc=utc(plan['created_epoch']),destroyed_confirmed_utc=utc(cleanup['utc']),rental_seconds_until_absence=cleanup['utc']-plan['created_epoch'],deadline_utc=utc(plan['deadline_epoch']))
(O/'lifecycle-timing.json').write_text(json.dumps(timeline,indent=2)+'\n')
print(json.dumps(timeline))
