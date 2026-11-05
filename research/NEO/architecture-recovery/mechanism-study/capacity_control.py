"""Supplementary active-parameter control; separate from one-component ablations."""
import sys,torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import make_model
from vendor.cryo_historical import Baseline

def build_control(seed,width=32):
 ref=make_model('cryo_history',seed,width=width);torch.manual_seed(seed+321);m=Baseline(v=8192,d=width,layers=2,dropout=0.)
 m.blocks[1].up=torch.nn.Linear(width,4*width,bias=False);m.blocks[1].down=torch.nn.Linear(2*width,width,bias=False);m.blocks[1].up.apply(m.init_weights);m.blocks[1].down.apply(m.init_weights)
 m.emb.load_state_dict(ref.emb.state_dict(),strict=True);m.blocks[0].load_state_dict(ref.blocks[0].state_dict(),strict=True);m.norm.load_state_dict(ref.slow_norm.state_dict(),strict=True)
 return m
