from runner import *
from data import oracle
from collections import Counter

def main():
 result={}
 for name in ['train','dev-combinations','dev-structures','micro']:
  rows=read(name);counts=Counter();prior={}
  for r in rows:
   gold=oracle(r['events'])[r['query_entity']];reverse=next(v for e,v in reversed(r['events']) if e==r['query_entity']);assert reverse==gold;assert gold==r['gold'];assert r['answer']==r['choices'][gold];counts['oracle_correct']+=1
   counts['first_global_correct']+=r['events'][0][1]==gold;counts['last_global_correct']+=r['events'][-1][1]==gold
   key=(tuple(r['query']),r['lang']);prior.setdefault(key,Counter())[gold]+=1
  ceiling=sum(max(v.values()) for v in prior.values())/len(rows);result[name]={'n':len(rows),'exact_oracle_accuracy':counts['oracle_correct']/len(rows),'first_global':counts['first_global_correct']/len(rows),'last_global':counts['last_global_correct']/len(rows),'presence_query_only_majority_ceiling':ceiling}
  assert ceiling==.25 and counts['oracle_correct']==len(rows)
 # Separate learned linear readout on explicit value one-hot; no learned Hielo involved.
 torch.manual_seed(17);head=torch.nn.Linear(4,4);o=torch.optim.AdamW(head.parameters(),lr=.003);x=torch.eye(4).repeat(8,1);y=torch.arange(4).repeat(8);initial=float(F.cross_entropy(head(x),y))
 for _ in range(100):o.zero_grad();ce=F.cross_entropy(head(x),y);ce.backward();o.step()
 accuracy=float((head(x).argmax(-1)==y).float().mean());assert accuracy==1
 result['explicit_linear_reader']={'accuracy':accuracy,'ce_initial':initial,'ce_final':float(F.cross_entropy(head(x),y).detach()),'updates':100,'capacity':20,'scope':'oracle-supplied value one-hot, diagnostic only; not autonomous memory learning'}
 save_json('positive-controls',{'passed':True,'results':result});print(json.dumps(result,indent=2))
if __name__=='__main__':main()
