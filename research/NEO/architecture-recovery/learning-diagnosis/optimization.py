from diagnose import *
def main():
 rows=datasets()['4'];m,opt,c=restore(OUT/'level-4-final.pt',rows);initial=h.model('B');historical,_,_=h.restore(BASE/'foreground-binding/results/B-17-final.pt',rows)
 result={'level4_exactly_reproduces_historical_B_weights':h.state_sha(m)==h.state_sha(historical),'activation_probes':{},'gradient_conflicts':{},'batch_balance':[]}
 idx=h.order(rows,17)
 for start in range(0,48,8):
  batch=[rows[i] for i in idx[start:start+8]];result['batch_balance'].append({'sides':dict(Counter(r['query_side'] for r in batch)),'values':dict(Counter(r['gold'] for r in batch))})
 for phase,net in [('initial',initial),('final',m)]:
  cap={};handles=[]
  for name,mod in net.named_modules():
   if name=='fast' or name.endswith(('n1','n2')):
    def hook(mod,args,out,key=name):cap.setdefault(key,[]).append({'input_rms':float(args[0].detach().square().mean().sqrt()),'output_rms':float(out.detach().square().mean().sqrt()),'abs_output_gt3_fraction':float((out.detach().abs()>3).float().mean()),'max_abs':float(out.detach().abs().max())})
    handles.append(mod.register_forward_hook(hook))
  h.logits(net,rows[:8]);[x.remove() for x in handles];result['activation_probes'][phase]=cap
  gs=[]
  for r in datasets()['3']:
   net.zero_grad(set_to_none=True);F.cross_entropy(h.logits(net,[r]),torch.tensor([r['answer']])).backward();gs.append(torch.cat([p.grad.flatten() for p in net.parameters() if p.requires_grad]))
  result['gradient_conflicts'][phase]={'cosines':[[float(F.cosine_similarity(a,b,dim=0)) for b in gs] for a in gs],'interpretation':'per-example CE gradients, opposing targets can conflict; not proof this causes optimization failure'}
 records=json.loads((OUT/'level-4.json').read_text())['curves'];result['clipping']={'fraction':sum(r['pre_clip_norm']>1 for r in records)/len(records),'first':records[0]['pre_clip_norm'],'last':records[-1]['pre_clip_norm'],'min_scale':min(r['clip_scale'] for r in records)}
 result['AdamW']={'lr':opt.param_groups[0]['lr'],'weight_decay':opt.param_groups[0]['weight_decay'],'betas':opt.param_groups[0]['betas'],'steps':sorted(set(int(v['step']) for v in opt.state.values())),'last_parameter_update_norms':records[-1]['parameter_update_norms'],'last_gradient_norms':records[-1]['gradients'],'decay_multiplier_per_step':1-.003*.01}
 put('optimization-diagnostics',result);print(json.dumps({k:v for k,v in result.items() if k!='activation_probes'},indent=2))
if __name__=='__main__':main()
