"""Recover evaluation/generation after missing tokenizer dependency; no optimizer updates."""
from pathlib import Path
import json,time,subprocess,resource
import torch
import worker,f2
R=Path(__file__).resolve().parent
assert __name__=='__main__'
torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
out=R/'results/F2';m=f2.make('F2').cuda();o=f2.opt(m);d=worker.Data('train');c=worker.restore(out/'final.pt',m,o,d,'cuda')
assert d.cursor==len(d.windows) and c['extra']['seen']==4922444
final_sha=worker.sha(out/'final.pt');dev=worker.evaluate(m,'cuda');gens=worker.generate(m,'cuda');worker.dump(out/'generations.json',gens)
td=worker.Data('train');sn=0.;nt=0;m.eval()
with torch.no_grad():
 while td.cursor<min(256,len(td.windows)):
  x,doc,v,n,_,_=td.batch('cuda');sn+=float(f2.language_loss(m(x,doc,v),x,doc,v))*n;nt+=n
birth=float(subprocess.check_output(['stat','-c','%W',str(R/'F2.log')],text=True));initial=json.loads((out/'initial-dev.json').read_text())['seconds']
assert birth>0
summary=dict(kind='F2',parameters=sum(p.numel() for p in m.parameters()),targets=c['extra']['seen'],updates=c['update'],online_train_nll=c['extra']['weighted']/c['extra']['seen'],final_train_fixed_sample_nll=sn/nt,final_train_sample_targets=nt,dev=dev,update_seconds=c['extra']['elapsed'],wall_seconds_this_process=time.time()-birth-initial,wall_time_note='reconstructed from log birth UTC rounded to second; includes dependency repair/re-evaluation pause; not uninterrupted worker time',targets_per_second=c['extra']['seen']/c['extra']['elapsed'],peak_gpu_allocated=torch.cuda.max_memory_allocated(),peak_gpu_note='finalization process only; training allocation recorded per update',peak_rss_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,dataset_sha=worker.sha(R/'dataset.json'),checkpoint_sha=final_sha,config=worker.CFG,recovered_evaluation_without_optimizer_updates=True)
assert final_sha==worker.sha(out/'final.pt')
worker.dump(out/'summary.json',summary);print(json.dumps(summary),flush=True)
