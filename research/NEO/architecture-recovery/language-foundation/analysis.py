import runpy
from pathlib import Path
globals().update({k:v for k,v in runpy.run_path(str(Path(__file__).with_name('pilot.py')),run_name='foundation_module').items() if not k.startswith('__')})
docs=json.loads((OUT/'data.json').read_text());ww=windows(docs,'train');dv=windows(docs,'dev');cnt=collections.Counter(i for r in ww for i in r['ids'][1:]);total=sum(cnt.values());uni={}
for split,w in [('train',ww),('dev',dv)]:
 targets=[i for r in w for i in r['ids'][1:]];nll=-sum(math.log((cnt[i]+.1)/(total+.1*8192)) for i in targets)/len(targets);uni[split]={'nll':nll,'ppl':math.exp(nll),'alpha':.1,'targets':len(targets)}
put('unigram',uni)
checks={}
for kind in P['arms']:
 m,o,c=load(OUT/f'{kind}-128.pt',docs);r=json.loads((OUT/f'{kind}.json').read_text());a=evaluate(m,kind,dv);assert a==r['metrics']['128']['dev'];checks[kind]={'reload_final_dev_exact':True,'adam_steps':sorted(set(int(v['step']) for v in o.state.values()))};assert checks[kind]['adam_steps']==[128]
 # Record full vocabulary logits on a fixed, public dev window (not an evaluation seal).
 x,v=batch(dv[:1])
 with torch.no_grad():y=logits(m,kind,x)
 torch.save({'input_ids':x,'valid':v,'logits':y,'source':dv[0]['id'],'offset':dv[0]['offset']},OUT/f'{kind}-dev-logits.pt')
put('reload-checks',checks)
edge=['','Español: acción, pingüino. English text.','e\u0301 é 🧊🙂 中文 Ελληνικά','x = 2\n    print(x)\n','$\\alpha + \\beta = 1$','\x00\t\r\n']
assert all(h.TOK.decode(h.TOK.encode(s))==s for s in edge)
text=''.join(Path(r['source_path']).read_text() for r in docs);start=time.perf_counter();ids=h.TOK.encode(text);enc=time.perf_counter()-start;start=time.perf_counter();decoded=h.TOK.decode(ids);dec=time.perf_counter()-start;assert decoded==text
put('tokenizer-analysis',{'edge_roundtrips':len(edge),'bytes':len(text.encode()),'ids':len(ids),'encode_seconds':enc,'decode_seconds':dec,'encode_bytes_s':len(text.encode())/enc,'decode_ids_s':len(ids)/dec,'artifact_bytes':h.ARTIFACT.stat().st_size,'artifact_sha':sha(h.ARTIFACT),'train_unique_id_types':len({i for r in ww for i in r['ids']}),'special_ids':{'PAD':256,'BOS':257,'EOS':258},'multiscale_used':False})
# Measured history, without repeating experiments or treating processed positions as new data.
history={}
for family,paths in [('factorial',[BASE/f'distribution-scaling/results/{a}-result.json' for a in 'AC']),('curriculum',[BASE/f'order-curriculum/results/{a}.json' for a in ['direct','curriculum']])]:
 for p in paths:
  z=json.loads(p.read_text());cc=z['curves'];history[str(p.relative_to(BASE))]={'updates':len(cc),'processed_input_ids':sum(r['input_ids'] for r in cc),'answer_targets':sum(r['responses'] for r in cc),'supervision':'answer only','density_answer_per_processed_id':sum(r['responses'] for r in cc)/sum(r['input_ids'] for r in cc)}
for kind in ['no_ice','ice','transformer']:
 z=json.loads((BASE/f'language-bridge/results/smoke-{kind}.json').read_text());history[f'language-bridge/{kind}']={'updates':z['steps'],'lm_targets':sum(r['targets'] for r in z['curves']),'supervision':'full causal LM real+synthetic; one layer, chunk16 except transformer full-window'}
put('history-exposure',history)
print('analysis and reload checks PASS',uni)
