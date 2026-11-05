import torch,json
import run_addressable as R
A=R.A;O=R.O;rows=R.C.data('same');m,d,o,rng,step=A.restore(O/'main.certified.pt',rows)
x=torch.tensor([r['ids'] for r in rows[::40]]);checks=[]
for mode in [False,True]:
 m.train(mode);y=m(x)
 for cut in range(1,64):
  xx=x.clone();xx[:,cut:]=120
  assert torch.equal(y[:,:cut],m(xx)[:,:cut]);checks.append([mode,cut])
y,tr=m(x,trace=True);torch.nn.functional.cross_entropy(y[:,-1],torch.tensor([r['label'] for r in rows[::40]])).backward()
g=float(tr[1]['memory'].grad.norm());assert g>0
for name in ['resume-check','microfit','main']:
 a=torch.load(O/(name+'.pt'),weights_only=True);b=torch.load(O/(name+'.certified.pt'),weights_only=True)
 for field in ['model','decoder','optimizer','rng','torch_rng','python_rng','cursor','step']:
  assert A.I.equal(a[field],b[field]),(name,field)
R.dump('final-verification.json',dict(all_126_train_eval_suffix_cuts_exact=True,answer_gradient_to_written_memory=g,certified_copy_model_optimizer_rng_identical=True,source_step=step))
print('126 causal cuts PASS; answer gradient',g,'; certified metadata parity PASS')
