"""Provider-independent deadline loop; executed on GitHub, outside the GPU and workstation."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.request


class Vast:
    def __init__(self):
        self.key = os.environ.get('VAST_API_KEY', '').strip()
        if not self.key:raise PermissionError('Missing Vast watchdog credential')

    def request(self, method, path):
        request = urllib.request.Request('https://console.vast.ai/api/v0/'+path,
                  headers={'Authorization':'Bearer '+self.key}, method=method)
        with urllib.request.urlopen(request, timeout=20) as r:
            return json.load(r)

    def instances(self):
        data = self.request('GET', 'instances/')
        return data['instances'] if isinstance(data, dict) else data

    def destroy(self, instance):
        return self.request('DELETE', f'instances/{int(instance)}/')


def validate(plan):
    if not re.fullmatch(r'neo-[a-z0-9-]{12,75}', plan['job_id']):
        raise ValueError('Invalid unique job ID')
    if plan['label'] != plan['job_id']:raise ValueError('Job/label mismatch')
    if not 0 < plan['deadline']-plan['armed_at'] <= 14400:
        raise ValueError('Watchdog runtime must be between zero and four hours')
    if plan['deadline'] < time.time():raise ValueError('Expired watchdog')


def enforce(plan, provider, now=None):
    now = time.time() if now is None else now
    rows = provider.instances()
    if plan.get('probe_only'):
        return {'confirmed':False,'active_ids':[],'probe_read_only':True,'armed_for_paid_job':False}
    target = plan.get('instance_id')
    if target is not None:
        row = next((r for r in rows if int(r['id']) == int(target)), None)
        if row and row.get('label') != plan['label']:
            raise ValueError('Ownership mismatch: refusing deletion')
    owned = [r for r in rows if r.get('label') == plan['label'] and
             (target is None or int(r['id']) == int(target))]
    if now < plan['deadline']:
        return {'confirmed':False, 'active_ids':[r['id'] for r in owned]}
    for row in owned:provider.destroy(row['id'])
    remaining = provider.instances()
    ids = [r['id'] for r in remaining if r.get('label') == plan['label'] and
           (target is None or int(r['id']) == int(target))]
    return {'confirmed':not ids, 'active_ids':ids, 'checked':time.time()}


def main():
    mode, filename = sys.argv[1:3]
    p = Path(filename);plan = json.loads(p.read_text());validate(plan)
    provider = Vast()
    if mode == 'prepare':
        provider.instances()  # credential check is read-only; fail before armed receipt
        Path('armed.json').write_text(json.dumps({'job_id':plan['job_id'], 'plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'deadline':plan['deadline'],'credential_verified':True,'external':True}))
        return
    seen = False; errors = 0
    while time.time() < plan['deadline']+180:
        try:
            state = enforce(plan, provider)
            if state['active_ids']:seen = True
            Path('watchdog-status.json').write_text(json.dumps(state))
            if plan.get('probe_only'):return
            if state['confirmed'] or (seen and not state['active_ids']):return
            errors = 0
        except Exception as exc:
            # Do not log API bodies or credentials. Retry provider outages independently of worker health.
            errors += 1;print('PROVIDER_RETRY', type(exc).__name__, errors, flush=True)
        time.sleep(min(20, max(.1, plan['deadline']-time.time())))
    raise RuntimeError('GPU shutdown attempted but NOT confirmed')


if __name__ == '__main__':main()
