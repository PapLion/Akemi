from pathlib import Path
import json,torch
import f2,count_v3
ROOT=Path(__file__).resolve().parent;tok=count_v3.load();sel=json.loads((ROOT/'results/f2-selection.json').read_text());r=next(x for x in sel['documents'] if x['split']=='train');ids=[257]+tok.encode(Path(r['path']).read_text())+[258];x=torch.tensor([ids[:128]]);doc=torch.zeros_like(x);v=torch.ones_like(x,dtype=torch.bool);out={}
for kind in ['F2','Transformer']:
 m=f2.make(kind);o=f2.opt(m);o.zero_grad(set_to_none=True);loss=f2.language_loss(m(x,doc,v),x,doc,v);loss.backward();assert torch.isfinite(loss) and all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters());torch.nn.utils.clip_grad_norm_(m.parameters(),1);o.step();prefix=torch.tensor([[257]+tok.encode('The command line interface')])
 with torch.no_grad():
  for _ in range(8):prefix=torch.cat([prefix,m(prefix)[:,-1].argmax(-1,keepdim=True)],1)
 generated=prefix[0,1:].tolist();out[kind]={'loss_single_technical_update':float(loss.detach()),'targets':127,'generation_decodes':isinstance(tok.decode(generated),str),'generation_ids':generated,'input_sha':r['sha'],'purpose':'One technical update on approved train input, not an F2 quality/learning experiment'}
(ROOT/'results/real-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
