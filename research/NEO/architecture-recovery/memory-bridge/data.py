from setup import *
NAMES=['Nora','Iris','Mira','Luna']
TOK=tokenizer()
COLORS={'en':['red','white','black','gold'],'es':['rojo','azul','verde','negro']}
TRAIN_PAIRS=[(0,1),(2,3)]
DEV_PAIRS=[(0,2),(1,3)]
CONFIRM_PAIRS=[(0,3),(1,2)]
def oracle(events):
 state={}
 for entity,value in events:state[entity]=value
 return state

def make(pair,values,lang,correction=False,offset=1,order=0,layout=0,distance=96,corrected=0):
 t=TOK;names=[NAMES[i] for i in pair];current=list(values);initial=list(values)
 if correction:initial[corrected]=(values[corrected]+offset)%4
 events=[];parts=[]
 for j in ([0,1] if order==0 else [1,0]):
  name=names[j];color=COLORS[lang][initial[j]]
  if lang=='en':phrase=[f'{name} received a {color} parcel. ',f'The parcel given to {name} was {color}. ',f'A parcel, {color} in color, belonged to {name}. '][layout]
  else:phrase=[f'{name} recibió un paquete de color {color}. ',f'El paquete entregado a {name} era de color {color}. ',f'Un paquete de color {color} pertenecía a {name}. '][layout]
  parts.append(phrase);events.append((pair[j],initial[j]))
 if correction:
  name=names[corrected];color=COLORS[lang][values[corrected]]
  parts.append((f'The record was corrected: the parcel for {name} was {color}. ' if lang=='en' else f'El registro se corrigió: el paquete de {name} era de color {color}. '));events.append((pair[corrected],values[corrected]))
 facts=''.join(parts);fact_ids=[257]+t.encode(facts)
 # Engineering boundary alignment; no clipping of facts or invented semantic extractor.
 filler=('Travelers discussed the station timetable. A clock stood beside an empty bench. ' if lang=='en' else 'Los viajeros comentaron el horario de trenes. Un reloj estaba junto a un banco vacío. ')
 neutral=t.encode(filler);remaining=distance-len(fact_ids);assert remaining>=16,(len(fact_ids),distance)
 ids=fact_ids+neutral*(remaining//len(neutral))+[32]*(remaining%len(neutral))
 assert t.decode(ids[1:]).encode('utf8')
 assert len(ids)==distance and distance%16==0
 state=oracle(events);assert [state[e] for e in pair]==current
 program={'pair':list(pair),'values':current,'initial_values':initial,'events':events,'lang':lang,'correction':correction,'corrected':corrected,'order':order,'layout':layout,'distance':distance,'facts':facts,'neutral_text':filler,'prefix':ids,'fact_tokens':len(fact_ids),'prefix_sha':digest(ids),'provenance':'authored controlled language templates V2; not open natural language'}
 program['program_id']=digest({k:program[k] for k in ['pair','values','initial_values','lang','correction','corrected','order','layout','distance']})
 return program

def questions(program):
 t=TOK;rows=[]
 for j,e in enumerate(program['pair']):
  name=NAMES[e];lang=program['lang'];layout=program['layout']
  if lang=='en':query=[f'What color was the parcel for {name}? Answer:',f'Give the parcel color assigned to {name}:',f'Recall the color of the parcel belonging to {name}:'][layout]
  else:query=[f'¿De qué color era el paquete de {name}? Respuesta:',f'Indica el color del paquete asignado a {name}:',f'Recuerda el color del paquete que pertenecía a {name}:'][layout]
  q=t.encode(query);assert len(q)<=32
  choices=[t.encode(' '+c) for c in COLORS[lang]];assert all(len(c)==1 for c in choices)
  # Query can span chunks; reset/swap intervene before the first query token.
  rows.append({**program,'query':q,'query_text':query,'query_entity':e,'query_side':j,'answer':choices[program['values'][j]][0],'choices':[c[0] for c in choices],'gold':program['values'][j],'role':'corrected' if program['correction'] and j==program['corrected'] else 'preserved' if program['correction'] else 'formation','example_id':program['program_id']+f'-{j}'})
 return rows

def panel(pairs,layouts,distances,corrections=True):
 rows=[]
 for pair,lang,va,vb,layout,distance,order in itertools.product(pairs,['en','es'],range(4),range(4),layouts,distances,range(2)):
  # Complete four-value Cartesian products, both questions per story; two orders balanced across values.
  rows+=questions(make(pair,[va,vb],lang,order=order,layout=layout,distance=distance))
  if corrections:
   for offset in [1,2,3]:
    corrected=(va+vb+offset)%2
    rows+=questions(make(pair,[va,vb],lang,True,offset,order,layout,distance,corrected))
 return rows

def build():
 train=panel(TRAIN_PAIRS,[0],[96,128]);dev=panel(DEV_PAIRS,[0],[96]);structural=panel(TRAIN_PAIRS,[1,2],[160]);micro=questions(make((0,1),[0,0],'en'))
 micro=[]
 for a,b in itertools.product(range(4),repeat=2):micro+=questions(make((0,1),[a,b],'en',distance=96))
 save_json('train',train);save_json('dev-combinations',dev);save_json('dev-structures',structural);save_json('micro',micro)
 # New confirmatory identities reserved by pair; seed recipe only, contents never materialized or evaluated.
 seal={'pairs':CONFIRM_PAIRS,'layouts':[1,2],'distances':[192],'reserved_seed':97031,'status':'sealed recipe; not materialized, opened or used for development','generator_sha':file_sha(__file__)}
 save_json('confirmatory-seal',seal)
 stats={}
 for name,rows in [('train',train),('dev-combinations',dev),('dev-structures',structural),('micro',micro)]:
  from collections import Counter
  counts=Counter(f"{r['lang']}/{r['query_entity']}/{r['role']}/{r['gold']}" for r in rows)
  stats[name]={'examples':len(rows),'programs':len({r['program_id'] for r in rows}),'sha':digest(rows),'targets':len(rows),'target_ids':dict(Counter(r['answer'] for r in rows)),'conditioned_frequencies':dict(sorted(counts.items())),'prefix_tokens':dict(Counter(r['distance'] for r in rows))}
  assert all(len({r['gold'] for r in rows if r['lang']==lang and r['query_entity']==e})==4 for lang,e in {(r['lang'],r['query_entity']) for r in rows})
 assert not {r['program_id'] for r in train}&{r['program_id'] for r in dev+structural}
 save_json('data-manifest',{'sets':stats,'tokenizer_fp':FP,'tokenizer_sha':file_sha(ARTIFACT),'model_sha':file_sha(BASE/'language-bridge/model.py'),'provenance':'all authored controlled experimental templates; no external corpus; no source acquisition','seal':seal,'prefix_alignment':'complete facts and complete neutral sentences, then explicit byte-space padding to synthetic boundary; no source documents truncated'})
 print({k:v['examples'] for k,v in stats.items()})
if __name__=='__main__':build()
