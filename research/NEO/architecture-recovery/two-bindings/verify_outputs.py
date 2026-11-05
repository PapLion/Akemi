from two_bindings import *
def main():
 out=R/'results';rows=data();dev=data(True)
 assert not set(r['id'] for r in rows)&set(r['id'] for r in dev)
 counts=collections.Counter((r['q'],*r['initial_values']) for r in rows);assert set(counts.values())=={4}
 for r in rows:
  assert r['stages'][0]<r['stages'][1]<6
  assert len(P.encode(r['ops'],r['q']))==64
  for index,j in enumerate(r['stages']):
   oracle={}
   for op,e,v in r['ops'][:2*j+2]:
    if op in '=!':oracle[e]=int(v)
   assert len(oracle)==2
   for e in [r['q'],r['other']]:assert oracle[e]==P.oracle(r['ops'][:2*j+2],e)
 ca=json.loads((out/'A-curves.json').read_text());cb=json.loads((out/'B-curves.json').read_text());assert len(ca)==len(cb)==150;assert [r['indices'] for r in ca]==[r['indices'] for r in cb]
 aa=torch.load(out/'A-initial.pt',weights_only=True);bb=torch.load(out/'B-initial.pt',weights_only=True)
 for k in ['model','decoder','optimizer','torch_rng','rng','dataset_sha256']:assert I.equal(aa[k],bb[k])
 m,d,o,rng=setup();x=torch.tensor([r['ids'] for r in rows[:2]])
 with torch.no_grad():base=m(x)
 original=d.forward
 def reject(*args,**kwargs):raise AssertionError('Aux decoder used in normal inference')
 d.forward=reject
 try:
  with torch.no_grad():assert torch.equal(m(x),base)
 finally:d.forward=original
 changes={}
 for arm in 'AB':
  final=torch.load(out/f'{arm}-150.pt',weights_only=True)
  changes[arm]=dict(model_tensors_changed=sum(not torch.equal(v,final['model'][k]) for k,v in aa['model'].items()),decoder_tensors_changed=sum(not torch.equal(v,final['decoder'][k]) for k,v in aa['decoder'].items()),adamw_state_tensors=len(final['optimizer']['state']))
 assert all(v['model_tensors_changed']>0 and v['decoder_tensors_changed']>0 for v in changes.values())
 dump(out/'output-verification.json',dict(pass_all=True,joint_pair_frequency=4,identical_initial_state=True,identical_150_batch_orders=True,normal_inference_decoder_unused=True,changes=changes,source_preserved=provenance()==json.loads((out/'historical-hashes-before.json').read_text())))
 # tuple/list difference above does not prove mismatch; canonical JSON digest used below.
 check=json.loads((out/'output-verification.json').read_text());check['source_preserved']=digest(provenance())==digest(json.loads((out/'historical-hashes-before.json').read_text()));assert check['source_preserved'];dump(out/'output-verification.json',check)
 print('PASS output verification')
if __name__=='__main__':main()
