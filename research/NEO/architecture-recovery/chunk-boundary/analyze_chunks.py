from chunk_study import *
def swap_values(r):
 s=copy.deepcopy(r);values=[op[2] for op in s['ops'] if op[0]=='='][::-1];i=0
 for op in s['ops']:
  if op[0]=='=':op[2]=values[i];i+=1
 z=P.make_record(s['ops'],s['q'],'value_swap','diagnostic');s.update(ids=z['ids'],label=z['label'],initial_values=r['initial_values'][::-1]);return s

def main():
 out=R/'results';allresults={};curves={c:json.loads((out/f'{c}-curves.json').read_text()) for c in ['same','separate']}
 assert [r['indices'] for r in curves['same']]==[r['indices'] for r in curves['separate']]
 initial={c:torch.load(out/f'{c}-initial.pt',weights_only=True) for c in ['same','separate']}
 for k in ['model','decoder','optimizer','rng','torch_rng']:assert I.equal(initial['same'][k],initial['separate'][k])
 for c in ['same','separate']:
  rr=data(c);m,d,o,rng,step=T.restore(out/f'{c}-150.pt',rr,'A');sw=[swap_values(r) for r in rr];ev,_=evaluate(m,d,sw);base=json.loads((out/f'{c}-train-evaluation.json').read_text());pred=base['predictions'];sp=ev['predictions'];ids=[i for i,r in enumerate(rr) if r['initial_values'][0]!=r['initial_values'][1]]
  strong=sum(all(pred[i]['stages']['initial']['pred'][j]==pred[i]['stages']['initial']['label'][j] and sp[i]['stages']['initial']['pred'][j]==sp[i]['stages']['initial']['label'][j] for j in range(2)) for i in ids)
  byorder={}
  for order in range(2):
   ix=[i for i,r in enumerate(rr) if r['write_order']==order];byorder[str(order)]=dict(n=len(ix),initial_joint=sum(all(p==y for p,y in zip(pred[i]['stages']['initial']['pred'],pred[i]['stages']['initial']['label'])) for i in ix)/len(ix))
  allresults[c]=dict(value_swap_accuracy=ev['metrics']['all']['initial'],value_swap_strict_joint=strong/len(ids),distinct_value_pairs=len(ids),by_order=byorder,training_seconds=base['training_seconds'],updates_per_second=150/base['training_seconds'],ids_per_second=150*8*64/base['training_seconds'],response_targets_per_second=150*8/base['training_seconds'])
  dump(c+'-swap-evaluation.json',ev)
  with torch.no_grad():
   logits,tr=m(torch.tensor([r['ids'] for r in rr[:16]]),trace=True)
   torch.save(dict(states=torch.stack([t['memory'] for t in tr],1),write=torch.stack([t['write'] for t in tr],1),erase=torch.stack([t['erase'] for t in tr],1),change=torch.stack([t['change'] for t in tr],1),ids=[r['id'] for r in rr[:16]]),out/f'{c}-full-trace.pt')
  # Dev visibility and causal state at actual later supervision boundary.
  dev=data(c,True);x=torch.tensor([r['ids'] for r in dev[:8]]);captured=[]
  handle=m.core.blocks[0].register_forward_pre_hook(lambda module,args:captured.append(args[1].clone()))
  try:
   with torch.no_grad():
    y,t=m(x,trace=True);xx=x.clone();xx[:,32:]=120;z,tt=m(xx,trace=True);assert torch.equal(t[3]['memory'],tt[3]['memory']);assert captured[0][:,31,16:32].all();assert not captured[0][:,31,:16].any()
  finally:handle.remove()
 dump('paired-analysis.json',allresults);dump('output-verification.json',dict(initial_states_identical=True,batch_orders_identical=True,dev_causal_visibility=True,source_preserved=history()==[(p,h) for p,h in json.loads((out/'historical-before.json').read_text())]))
 print({k:{'swap_joint':v['value_swap_strict_joint'],'seconds':v['training_seconds']} for k,v in allresults.items()})
if __name__=='__main__':main()
