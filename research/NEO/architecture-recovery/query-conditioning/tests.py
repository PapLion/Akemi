import unittest,tempfile
from run import *
class Contracts(unittest.TestCase):
 def test_tokenization_all_names(self):
  last=[]
  for name in NAMES:
   a=TOK.encode(f'What does {name} have? Answer:');b=TOK.encode(f'What does have? Answer: {name}')
   self.assertEqual(len(a),len(b));self.assertEqual(Counter(a),Counter(b));last.append(b[-1]);self.assertEqual(a[-1],58)
  self.assertEqual(len(set(last)),len(NAMES))
 def test_pairing_and_balance(self):
  a,b=dataset('A'),dataset('B')
  for split in a:
   self.assertEqual(len(a[split]),48)
   for x,y in zip(a[split],b[split]):
    self.assertEqual(x['prefix'],y['prefix']);self.assertEqual(x['answer'],y['answer']);self.assertEqual(Counter(x['query']),Counter(y['query']));self.assertNotEqual(*x['values'])
   self.assertEqual(set(Counter((r['query_side'],r['gold']) for r in b[split]).values()),{6})
 def test_real_attention(self):
  a,_=inspect_attention(model('full'),dataset('A')['train']);b,_=inspect_attention(model('full'),dataset('B')['train'])
  self.assertEqual(a['q_max_delta'],0);self.assertGreater(b['q_max_delta'],0);self.assertEqual(b['k_fact_max_delta'],0);self.assertGreater(b['relative_fact_attention_max_delta'],1e-5)
 def test_restore_and_optimizer(self):
  for fmt in ['A','B']:
   m,o,cp=restore(ROOT/'results'/f'short-{fmt}-17.pt',dataset(fmt)['train']);self.assertEqual(cp['cursor_updates'],200);self.assertEqual(cp['cursor_samples'],1600);self.assertEqual(len(o.state),sum(p.requires_grad for p in m.parameters()));self.assertTrue(all(torch.isfinite(p).all() for p in m.parameters()))
 def test_causal_label_independence(self):
  rows=dataset('B')['train'][:2];m=model('full');alter=[{**r,'answer':r['choices'][(r['gold']+1)%4]} for r in rows];self.assertTrue(torch.equal(logits(m,rows,'full'),logits(m,alter,'full')))
  x,last,_=tensors(rows);mem=torch.zeros(2,8,32)
  for mode in [True,False]:
   m.train(mode);h,_=m.chunk_hidden(x,mem,False);changed=x.clone();changed[:,110:]=(changed[:,110:]+7)%8192;other,_=m.chunk_hidden(changed,mem,False);self.assertTrue(torch.equal(h[:,:110],other[:,:110]))
 def test_exact_resume_both_formats(self):
  for fmt in ['A','B']:
   rows=dataset(fmt)['train'];m=model('full');o=optimizer(m)
   for i in range(3):update(m,o,rows,i,'full')
   with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'resume.pt';checkpoint(path,m,o,3,rows,'full',17)
    for i in range(3,8):update(m,o,rows,i,'full')
    rng=torch.get_rng_state();prng=random.getstate();n,opt,cp=restore(path,rows)
    for i in range(cp['cursor_updates'],8):update(n,opt,rows,i,'full')
    self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertEqual(prng,random.getstate())
    for k,v in m.state_dict().items():self.assertTrue(torch.equal(v,n.state_dict()[k]),k)
    for x,y in zip(o.state.values(),opt.state.values()):
     for k in x:self.assertTrue(torch.equal(x[k],y[k]))
 def test_exact_oracle_swap(self):
  rows=dataset('B')['train'];look={(tuple(r['values']),r['order'],r['query_side']):r for r in rows}
  for r in rows:
   s=look[(tuple(reversed(r['values'])),r['order'],r['query_side'])];self.assertNotEqual(s['answer'],r['answer']);self.assertEqual(s['gold'],r['values'][1-r['query_side']])
if __name__=='__main__':unittest.main(verbosity=2)
