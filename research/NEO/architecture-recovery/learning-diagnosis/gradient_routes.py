from diagnose import *
def main():
 rows=datasets()['4'];m,_,_=restore(OUT/'level-4-final.pt',rows);captured=[]
 handle=m.emb.register_forward_hook(lambda mod,args,out:(out.retain_grad(),captured.append(out)) and None)
 x,last,labels=h.tensors(rows);hidden,_=m.chunk_hidden(x,torch.zeros(len(rows),8,32),False);selected=hidden[torch.arange(len(rows)),last];y=F.linear(selected,m.emb.weight);y.retain_grad();F.cross_entropy(y,labels).backward();handle.remove()
 head=y.grad.T@selected.detach();total=m.emb.weight.grad.detach();encoder=total-head;start=len(rows[0]['prefix']);embgrad=captured[0].grad
 result={'tied_embedding':True,'head_and_encoder_not_independent_parameters':True,'head_gradient_norm':float(head.norm()),'encoder_embedding_gradient_norm':float(encoder.norm()),'total_tied_embedding_gradient_norm':float(total.norm()),'query_input_representation_gradient_norm':float(embgrad[:,start:].norm()),'facts_input_representation_gradient_norm':float(embgrad[:,97:108].norm()),'loss_mean_over_answer_positions':len(rows),'vocabulary_softmax_dimension':8192,'neutral_prefix_gradient_norm':float(embgrad[:,:97].norm()),'effective_exposures':{}}
 for level,r in datasets().items():
  steps=json.loads((ROOT/'PROTOCOL.json').read_text())['updates'][level];idx=h.order(r,17);used=[r[idx[(u*8+j)%len(r)]] for u in range(steps) for j in range(8)];result['effective_exposures'][level]={'answers':len(used),'entities':dict(Counter(v['query_entity'] for v in used)),'values':dict(Counter(v['gold'] for v in used)),'unique_inputs':len(r)}
 put('gradient-routes',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
