from harness import *
import unittest,tempfile
from collections import Counter
class Engineering(unittest.TestCase):
 def test_original_and_homology(self):
  a=model('A');reference=old.model('full',17);self.assertEqual(state_sha(a),state_sha(reference));b=model('B');c=model('C')
  for name,p in a.state_dict().items():
   if name not in ['blocks.0.up.weight','blocks.0.down.weight']:self.assertTrue(torch.equal(p,c.state_dict()[name]),name)
   self.assertTrue(torch.equal(p,b.state_dict()[name]),name)
  self.assertTrue(torch.equal(a.blocks[0].up.weight[:128],c.blocks[0].up.weight[:128]));self.assertTrue(torch.equal(a.blocks[0].up.weight[128:],c.blocks[0].up.weight[289:417]));self.assertTrue(torch.equal(a.blocks[0].down.weight,c.blocks[0].down.weight[:,:128]))
  self.assertLess(abs(sum(p.numel() for p in b.parameters())-sum(p.numel() for p in c.parameters()))/sum(p.numel() for p in b.parameters()),.001)
 def test_data_tokenizer_oracles(self):
  ds=data();old_ds=json.loads((BASE/'query-conditioning/results/datasets.json').read_text())['B'];self.assertEqual(ds,old_ds)
  for rows in ds.values():
   self.assertEqual(set(Counter((r['query_side'],r['gold']) for r in rows).values()),{6})
   for i in range(0,len(rows),2):self.assertNotEqual(rows[i]['query'][-1],rows[i+1]['query'][-1])
   for r in rows:
    self.assertNotEqual(*r['values']);self.assertEqual(TOK.encode(r['query_text']),r['query']);self.assertEqual(TOK.decode(TOK.encode(r['facts'])),r['facts']);self.assertEqual(r['gold'],r['values'][r['query_side']])
   for rule in ['first_entity','last_entity','last_value','majority_constant','correct_binding']:
    def predict(r):return r['values'][0] if rule=='first_entity' else r['values'][1] if rule=='last_entity' else r['last_value'] if rule=='last_value' else 0 if rule=='majority_constant' else r['values'][r['query_side']]
    acc=sum(predict(r)==r['gold'] for r in rows)/len(rows);self.assertEqual(acc,1 if rule=='correct_binding' else .25 if rule=='majority_constant' else .5)
 def test_causality_batch_padding_and_targets(self):
  rows=data()['train'][:2];x,last,_=tensors(rows)
  for arm in P['primary_arms']:
   m=model(arm);mem=torch.zeros(2,8,32)
   for training in [True,False]:
    m.train(training);h,_=m.chunk_hidden(x,mem,False);xp=x.clone();xp[:,110:]=(xp[:,110:]+7)%8192;hp,_=m.chunk_hidden(xp,mem,False);self.assertTrue(torch.equal(h[:,:110],hp[:,:110]))
    alone,_=m.chunk_hidden(x[:1],mem[:1],False);self.assertTrue(torch.allclose(h[:1],alone,atol=1e-6,rtol=1e-5))
    # Tail padding cannot alter selected valid logits.
    valid=x[:,:int(last.max())+1];short,_=m.chunk_hidden(valid,mem,False);self.assertTrue(torch.allclose(short[torch.arange(2),last],h[torch.arange(2),last],atol=1e-6,rtol=1e-5))
   y=logits(m,rows);changed=[{**r,'answer':r['choices'][(r['gold']+1)%4]} for r in rows];self.assertTrue(torch.equal(y,logits(m,changed)))
   self.assertTrue(all(int(last[i])==len(r['prefix'])+len(r['query'])-1 for i,r in enumerate(rows)))
 def test_gradients_optimizer_and_updates(self):
  rows=data()['train'][:8]
  for arm in P['primary_arms']:
   m=model(arm);opt=optimizer(m);active={id(p) for p in m.parameters() if p.requires_grad};group=[id(p) for g in opt.param_groups for p in g['params']];self.assertEqual(len(group),len(set(group)));self.assertEqual(active,set(group));before={n:p.clone() for n,p in m.named_parameters()};update(m,opt,rows,0,17)
   for n,p in m.named_parameters():
    if p.requires_grad:self.assertIsNotNone(p.grad,n);self.assertTrue(torch.isfinite(p.grad).all(),n);self.assertGreater(float(p.grad.norm()),0,n);self.assertFalse(torch.equal(p,before[n]),n)
    else:self.assertTrue(torch.equal(p,before[n]),n)
   self.assertEqual(len(opt.state),len(active))
 def test_second_layer_contextualized_input(self):
  m=model('B');rows=data()['train'][:2];x,last,_=tensors(rows);changed=x.clone();changed[:,97]=76 # Only first entity initial token; same value tokens, same future query.
  snapshots=[]
  h0=m.blocks[0].register_forward_hook(lambda mod,args,out:snapshots.append(('output0',out.detach())))
  h1=m.blocks[1].register_forward_pre_hook(lambda mod,args:snapshots.append(('input1',args[0].detach())))
  m.chunk_hidden(x,torch.zeros(2,8,32),False);m.chunk_hidden(changed,torch.zeros(2,8,32),False);h0.remove();h1.remove()
  self.assertTrue(torch.equal(snapshots[0][1],snapshots[1][1]));self.assertTrue(torch.equal(snapshots[2][1],snapshots[3][1]));self.assertFalse(torch.equal(snapshots[1][1][:,100],snapshots[3][1][:,100]));self.assertTrue(torch.equal(m.emb(x)[:,100],m.emb(changed)[:,100]))
  value_before=m.blocks[0].k(m.blocks[0].n1(m.emb(x)))[:,100];value_changed=m.blocks[0].k(m.blocks[0].n1(m.emb(changed)))[:,100];self.assertTrue(torch.equal(value_before,value_changed))
  after=m.blocks[1].k(m.blocks[1].n1(snapshots[1][1]))[:,100];other=m.blocks[1].k(m.blocks[1].n1(snapshots[3][1]))[:,100];self.assertGreater(float((after-other).abs().max()),0)
 def test_exact_resume(self):
  rows=data()['train']
  for arm in P['primary_arms']:
   m=model(arm);opt=optimizer(m)
   for i in range(3):update(m,opt,rows,i,17)
   with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'state.pt';snapshot(path,m,opt,arm,17,3,rows)
    for i in range(3,8):update(m,opt,rows,i,17)
    rng=torch.get_rng_state();prng=random.getstate();n,o,c=restore(path,rows)
    for i in range(c['cursor_updates'],8):update(n,o,rows,i,17)
    self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertEqual(prng,random.getstate())
    for k,v in m.state_dict().items():self.assertTrue(torch.equal(v,n.state_dict()[k]),k)
    for a,b in zip(opt.state.values(),o.state.values()):
     for k in a:self.assertTrue(torch.equal(a[k],b[k]))
 def test_eval_determinism(self):
  for arm in P['primary_arms']:
   m=model(arm);m.eval();rows=data()['train'][:2];self.assertTrue(torch.equal(logits(m,rows),logits(m,rows)))
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Engineering);r=unittest.TextTestRunner(verbosity=2).run(suite)
 if not r.wasSuccessful():sys.exit(1)
 evidence={'passed':True,'tests':r.testsRun,'sources':sources(),'tokenizer_sha':file_sha(ARTIFACT),'protocol_sha':file_sha(ROOT/'PROTOCOL.json')}
 if (ROOT/'results/engineering.json').exists():assert get('engineering')==evidence
 else:put('engineering',evidence)
