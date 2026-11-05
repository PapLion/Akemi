from evaluation import *
import subprocess,datetime

def main():
 torch.set_num_threads(1);m=load('ice');t=tokenizer();s=m.initial('example');prompt='Una viajera guardó una carta. Después regresó a la estación.'
 with torch.no_grad():
  for token in [257]+t.encode(prompt):logits,s=m.step(token,s,'example')
 path=ROOT/'results/session-example.pt'
 if not path.exists():torch.save({'model_checkpoint':'ice-final.pt','tokenizer':FP,'memory':s.memory,'pending':s.pending,'session_id':s.session_id,'completed':s.completed,'prompt_sha':sha(prompt.encode())},path)
 c=torch.load(path,weights_only=True);r=Session(c['memory'],c['pending'],c['session_id'],c['completed'])
 with torch.no_grad():
  a,s=m.step(32,s,'example');b,r=m.step(32,r,'example');assert torch.equal(a,b) and torch.equal(s.memory,r.memory)
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=CODE_ROOT.parent,text=True).strip(),'base':'1841b99','torch_threads':torch.get_num_threads(),'tokenizer_unchanged':sha(ARTIFACT.read_bytes())==json.loads((ROOT/'results/data-manifest.json').read_text())['artifact_sha'],'session_roundtrip_exact':True,'training_exposure':{},'code_identity':{p.name:sha(p.read_bytes()) for p in sorted(CODE_ROOT.glob('*.py'))}}
 assert result['tokenizer_unchanged']
 for kind in ['no_ice','ice','transformer']:
  m,o,cursor=restore(ROOT/'results'/f'{kind}-final.pt');assert cursor==64;assert len(o.state)==len([p for p in m.parameters() if p.requires_grad]);result['training_exposure'][kind]={'cursor_updates':cursor,'cursor_samples':cursor*2,'sampler_order_hash':digest(order()),'optimizer_states':len(o.state),'exposure':{}}
  exposure=result['training_exposure'][kind]['exposure'];w=windows('train');idx=order()
  for step in range(cursor):
   for j in range(2):
    row=w[idx[(step*2+j)%len(idx)]];k=f"{row['lang']}/{row['domain']}";a=exposure.setdefault(k,{'samples':0,'targets':0,'text_bytes_with_repeated_exposure':0});a['samples']+=1;a['targets']+=len(row['ids'])-1;a['text_bytes_with_repeated_exposure']+=sum(len(t.token_bytes(i)) for i in row['ids'] if i<256 or i>=512)
 memory=json.loads((ROOT/'results/memory-evaluation.json').read_text())['ice']['predictions'];pairs={}
 for r in memory:pairs.setdefault(r['id'],{})[r['mode']]=r
 result['memory_intervention_score_delta_max']={mode:max(abs(a-b) for pair in pairs.values() for a,b in zip(pair['normal']['scores'],pair[mode]['scores'])) for mode in ['reset','swap']}
 dump('final-checks',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
