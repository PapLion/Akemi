from mw_run import *
import statistics

def main():
 results={}
 for arm,K,condition in [('A',1,'same'),('B',2,'same')]:
  m,d,o,rng,step=load(OUT/f'{arm}-300.pt',C.data(condition),K);head=m.core.memory_head;torch.manual_seed(77);fast=torch.randn(8,8,32,requires_grad=True);memory=torch.randn(8,8,32,requires_grad=True);valid=torch.ones(8,8,dtype=torch.bool);samples=[]
  for i in range(55):
   m.zero_grad(set_to_none=True);fast.grad=None;memory.grad=None;t=time.perf_counter();z=head._summarize(fast[:,None],valid[:,None])[:,0];keys=F.normalize(head.key(z),dim=-1,eps=1e-6);values=head.value(z).tanh();ctrl=head.control(z).sigmoid();new=memory
   for slot in range(K):new=delta_step(new,keys[:,slot],values[:,slot],.9+.09*ctrl[:,slot,:1],ctrl[:,slot,1:2],ctrl[:,slot,2:],K)
   t1=time.perf_counter();new.square().mean().backward();t2=time.perf_counter()
   if i>=5:samples.append([1000*(t1-t),1000*(t2-t1)])
  results[arm]=dict(forward_median_ms=statistics.median(x[0] for x in samples),backward_median_ms=statistics.median(x[1] for x in samples),iterations=50,warmup=5,scope='Isolated writer re-expression, fixed random fast/memory batch8; no reader/refinement/optimizer. Not additive attribution of full update.')
 dump('writer-cost.json',results);print(results)
if __name__=='__main__':main()
