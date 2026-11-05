import study as S
import torch
rows,order=S.schedule(17,'B');m,d,o,s=S.restore(S.O/'B-17.pt',rows,order);m.eval();case=S.evaluation()['held_pair'][0];other=S.D.transform(case,'current');xx=torch.tensor([case['ids'],other['ids']]);print('changed positions',torch.nonzero(xx[0]!=xx[1]).flatten().tolist(),'window',m.core.visible_window)
with torch.no_grad():
 hh=m.core.hidden(xx,None,None);zz=m(xx,intervention='reset');print('hidden maxdiff',float((hh[0,-16:]-hh[1,-16:]).abs().max()),'reset logits diff',float((zz[0,-1]-zz[1,-1]).abs().max()))
