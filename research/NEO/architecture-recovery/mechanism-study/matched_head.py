"""Keep original Event/Delta memory initialization exactly; change foreground only."""
from variants import build
from experiment import make_model
def build_matched(arm,seed):
 kind=arm.removesuffix('_matched');m=build(kind,seed);original=make_model(kind,seed)
 state={k:v for k,v in original.state_dict().items() if not k.startswith(('emb.','blocks.','norm.'))}
 m.memory_head.load_state_dict(state,strict=True);return m
