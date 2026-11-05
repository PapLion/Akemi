"""Tensor-only state persistence at detached boundaries; never serializes autograd graphs."""
from models import MemoryState

def pack_state(state):
 return {'version':1,'memory':state.memory.detach().clone(),'last_doc':state.last_doc.clone(),'offset':state.offset.clone(),'session_id':state.session_id,'contract':'detached-boundary-only'}
def unpack_state(payload):
 if set(payload)!={'version','memory','last_doc','offset','session_id','contract'} or payload['version']!=1 or payload['contract']!='detached-boundary-only':raise ValueError('Unknown state schema')
 return MemoryState(payload['memory'],payload['last_doc'],payload['offset'],payload['session_id'])
