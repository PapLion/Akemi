from harness import *
from collections import Counter

def evaluate_sets(m,ds,tag):
 evaluation={}
 for split,rows in ds.items():
  met,pred=evaluate(m,rows);evaluation[split]=met;put(tag+'-'+split+'-predictions',pred)
 put(tag+'-evaluation',evaluation);return evaluation

def main():
 assert get('engineering')['passed'] and get('engineering')['sources']==sources()
 ds=data();put('datasets',ds)
 hist=json.loads((BASE/'query-conditioning/results/datasets.json').read_text())['B'];assert ds==hist
 idx=order(ds['train'],17);consumed=[ds['train'][idx[(u*P['batch']+j)%len(idx)]] for u in range(P['updates']) for j in range(P['batch'])]
 put('data-provenance',{'dataset_sha':digest(ds),'split_sha':{s:digest(r) for s,r in ds.items()},'source_dataset_sha':file_sha(BASE/'query-conditioning/results/datasets.json'),'tokenizer_fp':FP,'tokenizer_sha':file_sha(ARTIFACT),'input_ids':{'prefix':ds['train'][0]['prefix'],'query_entity0':ds['train'][0]['query'],'query_entity1':ds['train'][1]['query'],'target0':ds['train'][0]['answer'],'target1':ds['train'][1]['answer']},'query_counts':dict(Counter(r['query_side'] for r in consumed)),'target_counts':dict(Counter(r['gold'] for r in consumed)),'conditioned_counts':{str(k):v for k,v in Counter((r['query_side'],r['gold']) for r in consumed).items()},'sampler_order':idx,'targets_consumed_per_arm':len(consumed),'raw_origin':'controlled EN authored experimental templates, unchanged from Query Conditioning V1','sealed_data_accessed':False})
 params={};initial={}
 for arm in P['primary_arms']:
  m=model(arm);params[arm]=parameter_report(m,arm,ds['train']);initial[arm]=state_sha(m);snapshot(ROOT/'results'/f'{arm}-17-initial.pt',m,optimizer(m),arm,17,0,ds['train'])
 put('parameters',params);put('initial-weights',initial)
 results={}
 for arm in P['primary_arms']:
  m=train(arm,17,ds['train']);results[arm]=evaluate_sets(m,ds,f'{arm}-17')
 put('primary-comparison',results)
 passed=gate(results['B']);put('gate',{'passed':passed,'criteria':P['gates'],'confirmation':'enabled' if passed else 'NOT EXECUTED','Hielo':'NOT TRAINED'})
 if passed:
  confirmation={}
  for arm in P['confirmation']['arms']:
   m=train(arm,P['confirmation']['seed'],ds['train']);confirmation[arm]=evaluate_sets(m,ds,f"{arm}-{P['confirmation']['seed']}")
  put('confirmation-comparison',confirmation)
 else:print('STOP: B did not pass preregistered engineering triage; no extra seed, layer or update.',flush=True)
if __name__=='__main__':main()
