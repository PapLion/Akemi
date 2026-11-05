from common import *
import collections,re
SOURCE=PROJECT/'data/d0.1/accepted.jsonl'
LICENSES=[PROJECT/'data/d0/raw/oasst_README.md',PROJECT/'data/d0.1/raw/click-LICENSE.rst',PROJECT/'data/d0.1/raw/requests-LICENSE']
def build():
 t=tokenizer();rows=[];excluded=[]
 for r in map(json.loads,SOURCE.open()):
  # Never read sealed sources or use their records. Only existing train/dev and recorded permissive collections.
  if r['split'] not in ('train','dev'):continue
  use=r['domain']=='conversation' and r['source'].startswith('oasst') or r['id'] in ['click-docs_arguments.rst','requests-requests_structures.py']
  if not use:continue
  text=r['text'];assert sha(text.encode())==r['text_sha256'];assert r['provenance']['license'] in ('Apache-2.0','BSD-3-Clause');ids=t.encode(text);assert t.decode(ids)==text
  assert not re.search(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',text)
  rows.append({'id':r['id'],'split':r['split'],'lang':r['lang'],'domain':r['domain'],'text':text,'synthetic':False,'license':r['provenance']['license'],'group':r['group'],'provenance':r['provenance'],'text_sha':r['text_sha256'],'ids':[257]+ids+[258],'tokenizer':t.fingerprint,'quality_note':'original text preserved; spelling/factual/code errors not silently corrected; agent review only'})
 for i in range(32):
  lang='es' if i%2 else 'en';name=['Mira','Nora','Iris','Luna'][(i//2)%4];color=['red','blue','green','gold'][(i//8)%4]
  if lang=='en':text=f'{name} checked the parcel list at the station. Her parcel was {color}. Other passengers discussed train times while the clerk searched a different shelf. Later she asked for her parcel again.'
  else:
   color={'red':'rojo','blue':'azul','green':'verde','gold':'dorado'}[color];text=f'{name} revisó la lista de paquetes en la estación. Su paquete era {color}. Otros viajeros hablaron de los horarios mientras el encargado buscaba en otra estantería. Más tarde preguntó de nuevo por su paquete.'
  rows.append({'id':f'controlled-train-{i}','split':'train','lang':lang,'domain':'controlled_narrative','text':text,'synthetic':True,'license':'original experiment fixture; provenance code and commit','group':f'controlled-layout-{i%4}','text_sha':sha(text.encode()),'ids':[257]+t.encode(text)+[258],'tokenizer':t.fingerprint})
 train={r['text_sha'] for r in rows if r['split']=='train'};dev={r['text_sha'] for r in rows if r['split']=='dev'};assert not train&dev
 groups={s:{r['group'] for r in rows if r['split']==s} for s in ['train','dev']};assert not groups['train']&groups['dev']
 # Global normalized 12-word overlap audit; snippets are not printed.
 sh={}
 for split in ['train','dev']:
  ss=set()
  for r in rows:
   if r['split']!=split:continue
   words=re.findall(r'\w+',r['text'].lower());ss.update(tuple(words[i:i+12]) for i in range(len(words)-11))
  sh[split]=ss
 manifest={'source_sha':sha(SOURCE.read_bytes()),'tokenizer_fp':FP,'artifact_sha':sha(ARTIFACT.read_bytes()),'license_evidence':[{ 'path':str(p),'sha':sha(p.read_bytes())} for p in LICENSES],'documents':[{k:v for k,v in r.items() if k not in ('text','ids')} for r in rows],'cross_split_exact':0,'cross_split_groups':0,'cross_split_12word_matches':len(sh['train']&sh['dev']),'limits':'OASST collection Apache notice is verified; individual provenance/factual quality not independently certified; no redistribution of source text; public-domain PG excluded due jurisdiction qualification'}
 target=ROOT/'results/data.json';payload=json.dumps(rows,ensure_ascii=True,indent=2)
 if target.exists() and target.read_text()!=payload:raise FileExistsError('Refuse to replace dataset with different contents')
 target.write_text(payload);dump('data-manifest',manifest);return rows
if __name__=='__main__':build();print('DATA MATERIALIZED')
