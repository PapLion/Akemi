from mw_run import *
def main():
 report={}
 for K in [1,2]:
  m,d,o,rng=setup(K);rows=C.data('same')[::40];x=torch.tensor([r['ids'] for r in rows]);errors=[]
  for mode in [False,True]:
   m.train(mode)
   with torch.no_grad():
    y=m(x)
    for cut in [4,8,12,16,24,32,48]:
     xx=x.clone();xx[:,cut:]=120;z=m(xx);err=float((y[:,:cut]-z[:,:cut]).abs().max());assert torch.equal(y[:,:cut],z[:,:cut]);errors.append(dict(train=mode,cut=cut,max_abs=err))
  report[str(K)]=errors
 a=torch.load(OUT/'B-initial.pt',weights_only=True)['model']['core.memory_head.summary_query'];b=torch.load(OUT/'B-300.pt',weights_only=True)['model']['core.memory_head.summary_query'];changes=(a-b).norm(dim=-1).tolist();assert all(x>0 for x in changes);report['both_query_rows_changed']=changes
 dump('additional-causality-edges.json',report);print('PASS all within-chunk edges and both query updates')
if __name__=='__main__':main()
