"""Isolated depth experiment. Imports frozen data, logits and metrics read-only."""
from pathlib import Path
import sys,json,hashlib,random,time,math,resource,itertools,os
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
sys.path.insert(0,str(BASE/'query-conditioning'))
import run as historical
import runner as old
import torch
from torch import nn
import torch.nn.functional as F
from vendor.cryo_historical import Block
P=json.loads((ROOT/'PROTOCOL.json').read_text())
torch.set_num_threads(P['threads'])
TOK=historical.TOK
FP=historical.FP
ARTIFACT=historical.ARTIFACT
NAMES=historical.NAMES
COLORS=historical.COLORS

def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(name,obj):
 path=ROOT/'results'/f'{name}.json'
 if path.exists():raise FileExistsError(path)
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2)+'\n')
def get(name):return json.loads((ROOT/'results'/f'{name}.json').read_text())
def data():return historical.dataset('B','short')
def state_sha(m):return digest({k:hashlib.sha256(v.detach().cpu().numpy().tobytes()).hexdigest() for k,v in m.state_dict().items()})
def model(arm,seed=17):
 m=old.model('full',seed)
 if arm=='B':
  with torch.random.fork_rng():
   torch.manual_seed(seed+1000);block=Block(32)
   for module in block.modules():
    if isinstance(module,nn.Linear):nn.init.normal_(module.weight,std=.02)
   m.blocks.append(block)
 elif arm=='C':
  original=m.blocks[0]
  with torch.random.fork_rng():
   torch.manual_seed(seed+2000);up=nn.Linear(32,578,bias=False);down=nn.Linear(289,32,bias=False)
   nn.init.normal_(up.weight,std=.02);nn.init.normal_(down.weight,std=.02)
  with torch.no_grad():
   up.weight[:128].copy_(original.up.weight[:128]);up.weight[289:289+128].copy_(original.up.weight[128:]);down.weight[:,:128].copy_(original.down.weight)
  original.up=up;original.down=down
 elif arm!='A':raise ValueError(arm)
 return m

def optimizer(m):return historical.optimizer(m)
def logits(m,rows):return old.logits(m,rows,'full')
def tensors(rows):return old.tensors(rows)
def order(rows,seed):return old.order(rows,seed)
def sources():return {str(p.relative_to(BASE)):file_sha(p) for p in [ROOT/'harness.py',ROOT/'PROTOCOL.json',BASE/'language-bridge/model.py',BASE/'vendor/cryo_historical.py',BASE/'memory-bridge/runner.py',BASE/'query-conditioning/run.py',BASE/'binding-diagnostic/experiment.py']}
def update(m,opt,rows,cursor,seed):return old.update(m,opt,rows,cursor,'full',seed)
def snapshot(path,m,opt,arm,seed,cursor,rows):
 if path.exists():raise FileExistsError(path)
 torch.save({'model':m.state_dict(),'optimizer':opt.state_dict(),'arm':arm,'seed':seed,'cursor_updates':cursor,'cursor_samples':cursor*P['batch'],'microsteps':cursor,'pending_gradients':None,'accumulation':1,'scheduler':None,'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),'dataset_sha':digest(rows),'order':order(rows,seed),'tokenizer_fingerprint':FP,'tokenizer_sha':file_sha(ARTIFACT),'protocol':P,'sources':sources()},path)
def restore(path,rows):
 c=torch.load(path,weights_only=True);assert c['protocol']==P and c['dataset_sha']==digest(rows) and c['order']==order(rows,c['seed']) and c['sources']==sources() and c['tokenizer_sha']==file_sha(ARTIFACT) and c['tokenizer_fingerprint']==FP
 m=model(c['arm'],c['seed']);m.load_state_dict(c['model']);opt=optimizer(m);opt.load_state_dict(c['optimizer']);torch.set_rng_state(c['torch_rng']);random.setstate(c['python_rng']);return m,opt,c

def evaluate(m,rows):
 met,pred=historical.metrics(m,rows)
 for oid in [0,1]:
  selected=[(p,r) for p,r in zip(pred,rows) if r['order']==oid];programs={}
  for p,r in selected:programs.setdefault(r['program_id'],[]).append(p['correct'])
  met[f'order-{oid}']={'accuracy':sum(p['correct'] for p,r in selected)/len(selected),'joint':sum(all(v) for v in programs.values())/len(programs)}
 return met,pred

def parameter_report(m,arm,rows):
 # Analytic multiply-add estimates, forward only: actual padding length and selective LM head.
 x,_,_=tensors(rows[:8]);batch,T=x.shape;d=32;linear=0;attention=0
 for block in m.blocks:
  inner=block.down.in_features
  linear+=2*T*(3*d*d+3*d*inner) # GQA Q/O dxd plus K/V dxd/2; gated MLP.
  attention+=4*T*T*d # dense QK and AV, even causal kernel may implement differently.
 fast=2*2*T*(3*d*d);head=2*d*8192
 forward=linear+attention+fast+head
 return {'arm':arm,'allocated_parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),'trainable_tensors':sum(p.requires_grad for p in m.parameters()),'blocks':len(m.blocks),'inner_widths':[b.down.in_features for b in m.blocks],'valid_sequence_length':len(rows[0]['prefix'])+len(rows[0]['query']),'padded_sequence_length':T,'analytic_forward_flops_per_sequence':forward,'analytic_training_flops_per_response_approx_3x_forward':3*forward,'analytic_flops_per_processed_input_id':3*forward/(len(rows[0]['prefix'])+len(rows[0]['query'])),'omitted_flops':'normalization, softmax, SiLU/tanh, RoPE, bias, clipping, AdamW; not measured FLOPs; backward3x heuristic; full-vocab head selective last position'}

def train(arm,seed,rows):
 tag=f'{arm}-{seed}';path=ROOT/'results'/f'{tag}-final.pt';assert not path.exists()
 m=model(arm,seed);opt=optimizer(m);initial=state_sha(m);curves=[];m.train();start=time.perf_counter()
 for cursor in range(P['updates']):
  record=update(m,opt,rows,cursor,seed);curves.append(record)
  if (cursor+1)%100==0:print(tag,cursor+1,record['ce_answer'],flush=True)
 elapsed=time.perf_counter()-start;snapshot(path,m,opt,arm,seed,P['updates'],rows)
 put(tag+'-training',{'arm':arm,'seed':seed,'initial_weights_sha':initial,'updates':P['updates'],'responses':P['updates']*P['batch'],'seconds_train':elapsed,'responses_s':P['updates']*P['batch']/elapsed,'processed_ids_s':sum(r['input_ids'] for r in curves)/elapsed,'seconds_per_processed_input_id':elapsed/sum(r['input_ids'] for r in curves),'process_peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'curves':curves,'parameters':parameter_report(m,arm,rows),'checkpoint_sha':file_sha(path)})
 return m

def gate(evaluations):
 return all(e['joint']['accuracy']>=P['gates']['joint_min'] and e['strict_swap']['accuracy']>=P['gates']['strict_swaps_min'] and all(v>=P['gates']['each_entity_min'] for v in e['entity_sides'].values()) and all(e[f'order-{o}']['joint']>=P['gates']['each_fact_order_joint_min'] for o in [0,1]) for s,e in evaluations.items() if s!='train')
