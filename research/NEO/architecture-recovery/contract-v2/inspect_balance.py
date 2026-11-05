"""Auditable balance and response heuristics; no model or sealed data access."""
import collections,json
import trapos_data as D
out={}
for fam,rr in [('train',D.train(17)),*D.dev().items()]:
 cells=collections.Counter();conditional=collections.Counter();events=collections.Counter()
 for r in rr:
  conditional[r['q'],r['goal'].index(r['q']),r['label']-48]+=1
  for j,ev in enumerate(r['events']):
   p=ev['record']*4;cells[ev['entity'],r['ids'][p+2]-48,j,r['labels'][j]]+=1
   events[ev['type'],r['labels'][j]]+=1
 out[fam]={'query_entity_slot_value':[{'entity':e,'slot':s,'value':v,'n':n} for (e,s,v),n in sorted(conditional.items())],'event_type_acceptance':[{'type':t,'accept':a,'n':n} for (t,a),n in sorted(events.items())],'entity_value_position_acceptance':[{'entity':e,'value':v,'position':p,'accept':a,'n':n} for (e,v,p,a),n in sorted(cells.items())],'response_heuristics':D.frequencies(rr)['heuristics']}
(D.R/'results/balance-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('Balance audit saved; finite cells are reported, not asserted uniformly equal.')
