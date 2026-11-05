import runpy,csv
from pathlib import Path
globals().update({k:v for k,v in runpy.run_path(str(Path(__file__).with_name('pilot.py')),run_name='foundation_module').items() if not k.startswith('__')})
docs=json.loads((OUT/'data.json').read_text());ww=windows(docs,'train');dv=windows(docs,'dev');cnt=collections.Counter(i for r in ww for i in r['ids'][1:]);N=sum(cnt.values());allout={}
for kind in P['arms']:
 result=json.loads((OUT/f'{kind}.json').read_text());m,o,c=load(OUT/f'{kind}-128.pt',docs);tot=[0.,0.,0]
 with torch.no_grad():
  for r in dv:
   x,v=batch([r]);y=logits(m,kind,x)[0,:-1];labels=x[0,1:];cost=F.cross_entropy(y,labels,reduction='none')
   for i,g in enumerate(labels.tolist()):
    if g not in [256,257,258] and not h.TOK.decode([g]).isspace():tot[0]+=float(cost[i]);tot[1]+=-math.log((cnt[g]+.1)/(N+.1*8192));tot[2]+=1
 allout[kind]={'nonwhitespace_dev_targets':tot[2],'model_nll':tot[0]/tot[2],'unigram_nll':tot[1]/tot[2],'definition':'exclude special IDs and tokens whose isolated decode is whitespace; diagnostic only, not a gate'}
 with (OUT/f'{kind}-curves.csv').open('w') as fp:
  w=csv.DictWriter(fp,fieldnames=['update','targets_seen','ce','preclip_norm','seconds']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in result['curves'])
put('nonwhitespace',allout)
with (OUT/'evaluation-curves.csv').open('w') as fp:
 w=csv.writer(fp);w.writerow(['arm','update','split','category','targets_seen','nll','ppl','eval_targets'])
 for kind in P['arms']:
  r=json.loads((OUT/f'{kind}.json').read_text())
  for u,record in r['metrics'].items():
   for split in ['train','dev']:
    for category,v in record[split].items():w.writerow([kind,u,split,category,record.get('targets_seen',0),v['nll'],v['ppl'],v['targets']])
# Additional historical token exposure, computed from recorded batches only.
extra={}
for p in (BASE/'foreground-binding/results').glob('*-17-training.json'):
 z=json.loads(p.read_text());extra[str(p.relative_to(BASE))]={'updates':len(z['curves']),'input_ids':sum(r['input_ids'] for r in z['curves']),'response_targets':sum(r['responses'] for r in z['curves'])}
put('additional-history',extra)
print(allout)
