from tests import *
from evaluation import memory_panel,consume
class ExtraContracts(unittest.TestCase):
 def test_identical_initialization(self):
  models=[create(k) for k in ['ice','no_ice','transformer']]
  for name,p in models[0].state_dict().items():
   for m in models[1:]:self.assertTrue(torch.equal(p,m.state_dict()[name]),name)
 def test_stream_encode_decode_reference(self):
  t=tokenizer()
  for text in ['¿Español? 👩🏽‍💻 e\u0301\n\t fin','English_name(x): a+b == 3','  many    spaces\n\n','<|assistant|> hola']:
   ids=t.encode(text);self.assertEqual(ids,t.encode_reference(text))
   for stride in [1,2,7]:
    enc=StreamingEncoder(t);b=text.encode();got=[]
    for i in range(0,len(b),stride):got+=enc.feed(b[i:i+stride])
    got+=enc.finish();self.assertEqual(got,ids)
   decoder=StreamingDecoder(t);decoded=''.join(decoder.feed([i]) for i in ids)+decoder.finish();self.assertEqual(decoded,text)
  with self.assertRaises(ValueError):t.encode('\ud800')
  with self.assertRaises(ValueError):t.token_bytes(256)
 def test_loss_manual(self):
  m=create('ice');x=torch.tensor([[257,512,513,256]]);valid=x!=256;d=torch.zeros_like(x);y=m(x,d,valid);ce,n=loss(y,x,d,valid);manual=torch.nn.functional.cross_entropy(y[0,:2],x[0,1:3]);self.assertEqual(n,2);self.assertTrue(torch.equal(ce,manual))
 def test_session_checkpoint(self):
  m=create('ice');s=m.initial('x')
  for i in range(23):_,s=m.step(512+i,s,'x')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'session.pt';torch.save({'memory':s.memory.detach(),'pending':s.pending,'id':s.session_id,'completed':s.completed},p);c=torch.load(p,weights_only=True);r=Session(c['memory'],c['pending'],c['id'],c['completed'])
   for i in range(23,39):
    a,s=m.step(512+i,s,'x');b,r=m.step(512+i,r,'x');self.assertTrue(torch.equal(a,b));self.assertTrue(torch.equal(s.memory,r.memory))
 def test_boundary_rule(self):
  m=create('ice');x=(torch.arange(16)+512)[None];mem=torch.randn(1,8,32);h,old=m.chunk_hidden(x,mem,False);h2,new=m.chunk_hidden(x,mem,True);self.assertTrue(torch.equal(h,h2));self.assertTrue(torch.equal(mem,old));self.assertFalse(torch.equal(new,old))
  k=torch.nn.functional.normalize(m.address(m.emb(x[:,-1])),dim=-1,eps=1e-6);delta=new-old
  self.assertLess(float(torch.linalg.matrix_rank(delta[0])),2) # unchanged single outer-product update
 def test_memory_access_contract(self):
  panel=memory_panel();m=create('ice');p=panel[0];s=consume(m,p['prefix']);self.assertEqual(s.pending,[]);self.assertEqual(tuple(s.memory.shape),(1,8,32));self.assertEqual(set(vars(s)),{'memory','pending','session_id','completed'});self.assertGreater(len(p['prefix']),64)
  a=create('no_ice');s1=consume(a,panel[0]['prefix']);s2=consume(a,panel[1]['prefix']);self.assertTrue(torch.equal(s1.memory,s2.memory))
 def test_no_ice_prefix_invariance(self):
  m=create('no_ice');x=(torch.arange(48)+512)[None];y=x.clone();y[:,:32]+=200;self.assertTrue(torch.equal(m(x)[:,32:],m(y)[:,32:]))
 def test_data_uniqueness(self):
  r=records();hashes=[a['text_sha'] for a in r];self.assertEqual(len(hashes),len(set(hashes)));manifest=json.loads((ROOT/'results/data-manifest.json').read_text());self.assertEqual(manifest['cross_split_12word_matches'],0)
if __name__=='__main__':torch.set_num_threads(1);unittest.main(verbosity=2)
