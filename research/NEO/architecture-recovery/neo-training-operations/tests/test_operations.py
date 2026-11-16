import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import operations as o
import watchdog as w


class Provider:
    def __init__(self):
        self.rows = [{'id': 42, 'label': 'neo-test-123456789012'},
                     {'id': 99, 'label': 'unrelated'}]
        self.deleted = []

    def instances(self):
        return self.rows

    def destroy(self, instance):
        self.deleted.append(instance)
        self.rows = [r for r in self.rows if r['id'] != instance]


class FailingStore:
    def __init__(self):
        self.calls = 0

    def put(self, source, key, timeout):
        self.calls += 1
        raise OSError('simulated upload failure')


class Tests(unittest.TestCase):
    def test_attach_accepts_installed_cli_python_dict_and_json(self):
        for raw in (b"{'success': True}\n",b'{"success":true}\n'):
            with patch.object(o,'command',return_value=raw) as run:
                self.assertTrue(o.attach_ssh(42,'public.pub')['success'])
                self.assertEqual(run.call_args.args[0],
                                 ['vastai','attach','ssh','42','public.pub','--raw'])

    def test_attach_rejects_failed_exit_unconfirmed_or_invalid_response(self):
        with patch.object(o,'command',side_effect=RuntimeError('exit 1')):
            with self.assertRaises(RuntimeError):o.attach_ssh(42,'public.pub')
        for raw in (b"{'success': False}",b'{}',b'[]',b'not-data'):
            with patch.object(o,'command',return_value=raw):
                with self.assertRaises((RuntimeError,ValueError,SyntaxError)):
                    o.attach_ssh(42,'public.pub')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def worker(self, code, timeout=5):
        out = self.root / 'output'
        out.mkdir(exist_ok=True)
        cfg = {'job_id': 'neo-test-123456789012', 'cwd': str(out),
               'command': [sys.executable, '-c', code], 'max_seconds': timeout,
               'term_grace_seconds': .1, 'required_files': ['checkpoint.json']}
        p = self.root / 'worker.json'
        o.atomic(p, cfg)
        return subprocess.Popen([sys.executable, str(ROOT/'worker.py'), str(p)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE), out

    def test_success_exit_and_output_inventory(self):
        p, out = self.worker("from pathlib import Path;Path('checkpoint.json').write_text('{\"cursor\": 7}')")
        self.assertEqual(p.wait(timeout=8), 0)
        s = o.read(out/'.neo-worker/status.json')
        self.assertEqual(s['returncode'], 0)
        self.assertEqual(s['outcome'], 'completed')
        self.assertIn('checkpoint.json', s['files'])
        self.assertTrue(s['outputs_valid'])
        p.stderr.close()

    def test_training_failure_retains_partial_output(self):
        p, out = self.worker("from pathlib import Path;Path('checkpoint.json').write_text('partial');raise SystemExit(7)")
        self.assertEqual(p.wait(timeout=8), 7)
        s = o.read(out/'.neo-worker/status.json')
        self.assertEqual(s['returncode'], 7)
        self.assertEqual(s['outcome'], 'failed')
        self.assertIn('checkpoint.json', s['files'])
        p.stderr.close()

    def test_timeout(self):
        p, out = self.worker('import time;time.sleep(30)', timeout=.2)
        p.wait(timeout=8)
        self.assertEqual(o.read(out/'.neo-worker/status.json')['outcome'], 'timeout')
        p.stderr.close()

    def test_interruption(self):
        p, out = self.worker('import time;time.sleep(30)')
        for _ in range(100):
            if (out/'.neo-worker/running.json').exists():
                break
            time.sleep(.01)
        p.send_signal(signal.SIGTERM)
        p.wait(timeout=8)
        self.assertEqual(o.read(out/'.neo-worker/status.json')['outcome'], 'interrupted')
        p.stderr.close()

    def test_no_duplicate_worker_on_reentry(self):
        p, out = self.worker("from pathlib import Path;Path('checkpoint.json').write_text('once')")
        self.assertEqual(p.wait(timeout=8), 0)
        original = (out/'.neo-worker/status.json').read_bytes()
        q = subprocess.run([sys.executable, str(ROOT/'worker.py'), str(self.root/'worker.json')])
        self.assertEqual(q.returncode, 0)
        self.assertEqual(original, (out/'.neo-worker/status.json').read_bytes())
        p.stderr.close()

    def test_finalization_idempotent_and_hash_verified(self):
        src = self.root/'archive.tar';src.write_bytes(b'checkpoint-and-rng')
        store = o.LocalStore(self.root/'persistent')
        provider = Provider()
        manifest = self.root/'manifest.json'
        o.atomic(manifest, {'job_id': 'neo-test-123456789012', 'instance_id': 42,
                            'label': 'neo-test-123456789012', 'training': {'outcome':'completed','returncode':0,'outputs_valid':True}})
        a = o.finalize(manifest, src, store, provider, time.time()+10, retries=2, backoff=.01)
        b = o.finalize(manifest, src, store, provider, time.time()+10, retries=2, backoff=.01)
        self.assertTrue(a['archive']['verified'])
        self.assertTrue(b['cleanup']['confirmed'])
        self.assertEqual(provider.deleted, [42])
        self.assertEqual(len(list((self.root/'persistent').rglob('*.tar'))), 1)
        self.assertEqual(b['outcome'], 'completed_archived_shutdown_confirmed')

    def test_upload_failure_is_bounded_and_always_destroys(self):
        src = self.root/'a.tar';src.write_bytes(b'partial')
        manifest = self.root/'m.json'
        o.atomic(manifest, {'job_id':'neo-test-123456789012', 'instance_id':42, 'label':'neo-test-123456789012'})
        store = FailingStore();provider = Provider()
        r = o.finalize(manifest, src, store, provider, time.time()+5, retries=3, backoff=.001)
        self.assertEqual(store.calls, 4)  # three artifact attempts + one bounded manifest attempt after cleanup
        self.assertFalse(r['archive']['verified'])
        self.assertTrue(r['cleanup']['confirmed'])
        self.assertEqual(provider.deleted, [42])
        self.assertTrue(src.exists())

    def test_hash_corruption_rejected(self):
        src = self.root/'a';src.write_bytes(b'abc')
        target = self.root/'store';store = o.LocalStore(target)
        key = 'job/a';store.put(src,key,10)
        (target/key).write_bytes(b'bad')
        with self.assertRaises(ValueError):
            store.put(src,key,10)

    def test_watchdog_only_destroys_owned_job(self):
        provider = Provider()
        plan = {'job_id':'neo-test-123456789012','label':'neo-test-123456789012','instance_id':42,'deadline':1}
        r = w.enforce(plan, provider, now=2)
        self.assertTrue(r['confirmed'])
        self.assertEqual(provider.deleted, [42])
        self.assertEqual(provider.rows, [{'id':99,'label':'unrelated'}])

    def test_watchdog_does_not_destroy_before_deadline(self):
        p=Provider();w.enforce({'label':'neo-test-123456789012','deadline':100},p,now=2)
        self.assertEqual(p.deleted, [])

    def test_watchdog_fails_closed_on_wrong_label(self):
        p=Provider()
        with self.assertRaises(ValueError):
            w.enforce({'label':'other','instance_id':42,'deadline':1},p,now=2)
        self.assertEqual(p.deleted, [])

    def test_missing_credentials_no_launch(self):
        with self.assertRaises(FileNotFoundError):
            o.credential_preflight(self.root/'missing-key', self.root/'missing-rclone')

    def test_budget_and_recovery_reserve(self):
        cfg={'job_id':'neo-test-123456789012','max_runtime_seconds':7200,
             'hourly_usd':.3,'max_usd':.5,'transfer_reserve_usd':.1,'recovery_seconds':600}
        with self.assertRaises(ValueError):
            o.validate_budget(cfg)
        cfg['max_usd']=.75
        self.assertGreater(o.validate_budget(cfg)['maximum_usd'], .6)


if __name__ == '__main__':
    unittest.main()
