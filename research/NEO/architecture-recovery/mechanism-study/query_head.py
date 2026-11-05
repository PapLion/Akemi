"""Exact answer-only reduction of the no_ice diagnostic, not a replacement LM."""
import torch
import torch.nn.functional as F
def answer_only(model,ids,doc=None,valid=None):
 if model.arm!='no_ice':raise ValueError('Only the nonrecurrent no_ice ablation admits this reduction')
 x=model.hidden(ids,doc,valid)[:,-1];fast=x
 for _ in range(2):fast=model.fast_norm(fast+model.fast(torch.cat([fast,x,torch.zeros_like(x)],-1)).tanh())
 return F.linear(model.slow_norm(fast),model.emb.weight)
