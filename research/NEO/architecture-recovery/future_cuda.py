"""Future synthetic CUDA benchmark. Dry-run by default; never rents a GPU."""
import argparse,json,time,statistics,dataclasses
from pathlib import Path
import torch
from models import CryoNext,causal_loss
from experiment import make_model,optimizer
from tasks import FP
ARMS=['b0_local','b0_full','cryo_history','event','delta','delta_scan']
def synchronize():torch.cuda.synchronize()
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--seconds',type=int,default=180);p.add_argument('--output',default='results/future-cuda.json');a=p.parse_args()
 plan={'arms':ARMS,'lengths':[128,256],'batch':4,'precision':'fp32','chunk':32,'width':32,'layers':1,'warmup':2,'measurements':5,'tokenizer':FP,'max_seconds':a.seconds,'scope':'synthetic engineering throughput; no corpus; no rental; CUDA contracts require independent certification'}
 if not a.execute:print(json.dumps(plan,indent=2));return
 if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable; no CPU result substituted')
 torch.cuda.set_per_process_memory_fraction(.5);torch.backends.cuda.matmul.allow_tf32=False;start=time.monotonic();rows=[]
 for length in plan['lengths']:
  torch.manual_seed(17);ids=torch.randint(32,127,(4,length),device='cuda')
  for arm in ARMS:
   if time.monotonic()-start>a.seconds:break
   m=make_model('delta' if arm=='delta_scan' else arm,chunk=32).cuda();op=optimizer(m)
   for mode in [True,False]:
    m.train(mode);other=ids.clone();other[:,length//2:]=(other[:,length//2:]+1)%8192
    with torch.no_grad():
     left=m(ids);right=m(other);left=left.logits if hasattr(left,'logits') else left;right=right.logits if hasattr(right,'logits') else right
     torch.testing.assert_close(left[:,:length//2],right[:,:length//2],rtol=1e-4,atol=2e-5)
   m.train();timings=[];torch.cuda.reset_peak_memory_stats()
   for update in range(7):
    synchronize();ts=time.perf_counter();op.zero_grad(set_to_none=True)
    out=m(ids,parallel=arm=='delta_scan') if isinstance(m,CryoNext) else m(ids)
    logits=out.logits if hasattr(out,'logits') else out;loss=causal_loss(logits,ids);assert torch.isfinite(loss);loss.backward()
    for name,q in m.named_parameters():
     if q.requires_grad:assert q.grad is not None and torch.isfinite(q.grad).all(),name
    torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True);op.step();synchronize()
    if update>=2:timings.append(time.perf_counter()-ts)
   rows.append({'arm':arm,'length':length,'batch':4,'update_seconds':timings,'targets_s':4*(length-1)/statistics.median(timings),'vram_peak_bytes':torch.cuda.max_memory_allocated(),'parameters':sum(q.numel() for q in m.parameters()),'precision':'fp32','certification':'limited causality and gradients only; not full CUDA/resume certificate'})
   Path(a.output).write_text(json.dumps({'plan':plan,'gpu':torch.cuda.get_device_name(),'torch':str(torch.__version__),'results':rows},indent=2));del m,op,out,logits;torch.cuda.empty_cache()
if __name__=='__main__':main()
