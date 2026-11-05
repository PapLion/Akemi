from engine import *
import itertools,copy

def load(kind):
 m,o,c=restore(ROOT/'results'/f'{kind}-final.pt');return m.eval()

def generate(m,prompt,steps=24):
 t=tokenizer();ids=[257]+t.encode(prompt);generated=[];state=m.initial();raw=[]
 with torch.no_grad():
  if m.kind!='transformer':
   for token in ids:logits,state=m.step(token,state)
  for _ in range(steps):
   if m.kind=='transformer':logits=m(torch.tensor([ids+generated]))[:,-1]
   scores=logits[0].clone();scores[256:512]=-float('inf');scores[258]=logits[0,258];token=int(scores.argmax());generated.append(token)
   if token==258:break
   raw.append(token)
   if m.kind!='transformer':logits,state=m.step(token,state)
 b=t.decode_bytes(raw);return {'prompt':prompt,'generated_ids':generated,'bytes_hex':b.hex(),'bytes_sha':sha(b),'utf8_valid':valid_utf8(b),'display':b.decode('utf8','replace'),'display_policy':'replacement only for display; exact bytes retained'}
def valid_utf8(b):
 try:b.decode('utf8');return True
 except UnicodeDecodeError:return False

def memory_panel():
 t=tokenizer();out=[]
 for lang,correction,valid in itertools.product(['es','en'],[False,True],range(4)):
  colors=['red','blue','green','gold'] if lang=='en' else ['rojo','azul','verde','dorado'];old=(valid+1)%4
  if lang=='en':
   prefix=f'Nora received a {colors[old if correction else valid]} parcel. Iris received a white parcel. '
   if correction:prefix+=f'The clerk corrected the record: Nora received a {colors[valid]} parcel. '
   prefix+='Passengers compared railway schedules. The building has a long corridor and several empty rooms. '*4;query='Nora\'s parcel color was'
  else:
   prefix=f'Nora recibió un paquete {colors[old if correction else valid]}. Iris recibió un paquete blanco. '
   if correction:prefix+=f'El encargado corrigió el registro: Nora recibió un paquete {colors[valid]}. '
   prefix+='Los viajeros compararon horarios de trenes. El edificio tiene un pasillo largo y varias salas vacías. '*4;query='El color del paquete de Nora era'
  ids=[257]+t.encode(prefix);padding=(-len(ids))%16;ids += [32]*padding # Explicit byte-space boundary alignment; not source repair.
  q=t.encode(query);assert len(q)<16;out.append({'id':f'{lang}-{correction}-{valid}','lang':lang,'correction':correction,'valid':valid,'old':old,'prefix':ids,'query':q,'choices':[t.encode(' '+c+'.') for c in colors],'alignment_byte_spaces':padding,'provenance':'new authored controlled diagnostic; not natural-source generalization','prefix_sha':digest(ids),'query_text':query})
 return out

def consume(m,ids):
 s=m.initial()
 for token in ids:_,s=m.step(token,s)
 assert not s.pending;return s

def score_stream(m,state,query,choice):
 s=Session(state.memory.clone(),list(state.pending),state.session_id,state.completed);score=0.
 for token in query:logits,s=m.step(token,s)
 for token in choice:
  score+=float(logits.log_softmax(-1)[0,token]);logits,s=m.step(token,s)
 return score/len(choice) # length-normalized closed-set continuation, not unconstrained accuracy

def score_full(m,prefix,query,choice):
 seq=prefix+query+choice;x=torch.tensor([seq]);y=m(x);start=len(prefix)+len(query)-1
 return sum(float(y[0,start+j].log_softmax(-1)[v]) for j,v in enumerate(choice))/len(choice)

def evaluate_memory():
 panel=memory_panel();dump('memory-fixtures',panel);result={}
 with torch.no_grad():
  for kind in ['no_ice','ice','transformer']:
   m=load(kind);states=[consume(m,p['prefix']) for p in panel] if kind!='transformer' else None;pred=[]
   for i,p in enumerate(panel):
    variants=['normal','reset','swap'] if kind=='ice' else ['normal']
    for mode in variants:
     if kind=='transformer':scores=[score_full(m,p['prefix'],p['query'],c) for c in p['choices']]
     else:
      s=states[i]
      if mode=='reset':s=m.initial()
      if mode=='swap':s=states[(i//4)*4+(p['valid']+1)%4]
      scores=[score_stream(m,s,p['query'],c) for c in p['choices']]
     answer=max(range(4),key=scores.__getitem__);pred.append({'id':p['id'],'lang':p['lang'],'correction':p['correction'],'mode':mode,'gold':p['valid'],'pred':answer,'scores':scores,'correct':answer==p['valid']})
   totals={}
   for r in pred:
    k=f"{r['mode']}/{r['lang']}/{'correction' if r['correction'] else 'retention'}";a=totals.setdefault(k,[0,0]);a[0]+=r['correct'];a[1]+=1
   result[kind]={'groups':{k:{'correct':a,'n':n,'accuracy':a/n} for k,(a,n) in totals.items()},'predictions':pred}
 dump('memory-evaluation',result)
 return result
if __name__=='__main__':
 torch.set_num_threads(1);dump('generations',{k:[generate(load(k),p) for p in ['La estación estaba tranquila.','The traveller returned to the station.']] for k in ['no_ice','ice','transformer']});evaluate_memory();print('EVALUATION COMPLETE')
