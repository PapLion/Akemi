from engine import *
import platform,subprocess,importlib.metadata,statistics,csv

def measure():
 data=records();manifest=json.loads((ROOT/'results/data-manifest.json').read_text());assert manifest['artifact_sha']==sha(ARTIFACT.read_bytes())
 totals={}
 for r in data:
  key=f"{r['split']}/{'synthetic' if r['synthetic'] else 'real'}/{r['lang']}/{r['domain']}";a=totals.setdefault(key,{'documents':0,'utf8_bytes':0,'ids':0,'targets':0});a['documents']+=1;a['utf8_bytes']+=len(r['text'].encode());a['ids']+=len(r['ids']);a['targets']+=len(r['ids'])-1
 t=tokenizer();text='El tren volvió a la estación. The traveller returned. 👩🏽‍💻\n'*30;loops=100;start=time.perf_counter()
 for _ in range(loops):ids=t.encode(text)
 encode=time.perf_counter()-start;start=time.perf_counter()
 for _ in range(loops):assert t.decode(ids)==text
 decode=time.perf_counter()-start
 performance={};nll={}
 for kind in ['no_ice','ice','transformer']:
  r=json.loads((ROOT/'results'/f'smoke-{kind}.json').read_text());times=[a['seconds'] for a in r['curves']];nll[kind]={}
  for stage in ['initial','final']:
   nll[kind][stage]={}
   for split in ['train','dev']:
    g={k:v for k,v in r[stage][split].items() if k.startswith('real/')};n=sum(v['targets'] for v in g.values());value=sum(v['nll']*v['targets'] for v in g.values())/n;nll[kind][stage][split]={'nll':value,'ppl':math.exp(value),'targets':n}
  performance[kind]={k:r[k] for k in ['allocated_parameters','trainable_parameters','seconds','targets_per_second','peak_rss_mib']};performance[kind].update({'update_mean_ms':statistics.mean(times)*1000,'update_stdev_ms':statistics.stdev(times)*1000,'exposure_targets':sum(x['targets'] for x in r['curves']),'estimated_100k_target_seconds':100000/r['targets_per_second'],'estimator_limits':'CPU single-thread tiny batch smoke only; no GPU or 50M extrapolation; FLOPs not profiled'})
 dump('summary',{'data':totals,'nll_real_weighted':nll,'performance':performance,'tokenizer':{'fingerprint':FP,'artifact_bytes':ARTIFACT.stat().st_size,'encode_utf8_bytes_s':len(text.encode())*loops/encode,'decode_utf8_bytes_s':len(text.encode())*loops/decode,'measured_utf8_bytes':len(text.encode())*loops},'environment':{'python':platform.python_version(),'torch':torch.__version__,'tokenizers':importlib.metadata.version('tokenizers'),'regex':importlib.metadata.version('regex'),'cpu':subprocess.check_output(['lscpu'],text=True),'threads':torch.get_num_threads(),'precision':'FP32','cuda_used':False},'limits':'Single seed; distinct real dev documents but source collections shared; no independent human review; closed-choice memory fixture is synthetic; source rights conditional.'})
 with (ROOT/'results/curves.csv').open('w') as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(['arm','update','nll','targets','seconds'])
  for kind in performance:
   for r in json.loads((ROOT/'results'/f'smoke-{kind}.json').read_text())['curves']:w.writerow([kind,r['update'],r['ce'],r['targets'],r['seconds']])
 return performance
if __name__=='__main__':torch.set_num_threads(1);print(json.dumps(measure(),indent=2))
