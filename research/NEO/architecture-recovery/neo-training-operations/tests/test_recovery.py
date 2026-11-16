"""Failure/recovery boundary tests: no real provider writes or paid resources."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import operations as o
from test_operations import Provider


class Recovery(unittest.TestCase):
    def test_cloud_deployment_probe_never_deletes(self):
        import watchdog
        p=Provider()
        r=watchdog.enforce({'label':'neo-test-123456789012','deadline':1,'probe_only':True},p,now=2)
        self.assertFalse(r['armed_for_paid_job'])
        self.assertEqual(p.deleted,[])

    def test_deletion_failure_never_claims_shutdown(self):
        p=Provider()
        p.destroy=lambda instance: (_ for _ in ()).throw(ConnectionError())
        r=o.destroy_owned(p,{'instance_id':42,'label':'neo-test-123456789012'})
        self.assertFalse(r['confirmed'])
        self.assertTrue(r['attempted'])

    def test_state_does_not_destroy_unrelated_label(self):
        p=Provider()
        r=o.destroy_owned(p,{'instance_id':99,'label':'neo-test-123456789012'})
        self.assertFalse(r['confirmed'])
        self.assertEqual(p.deleted,[])

    def test_remote_process_survives_launcher_exit(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); cfg=root/'config.json'
            o.atomic(cfg,{'job_id':'neo-test-123456789012','cwd':td,'max_seconds':10,
                         'required_files':['done'], 'command':[sys.executable,'-c',
                         "import time;from pathlib import Path;time.sleep(.2);Path('done').write_text('ok')"]})
            code="import subprocess,sys;subprocess.Popen([sys.executable,sys.argv[1],sys.argv[2]],start_new_session=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)"
            subprocess.run([sys.executable,'-c',code,str(o.ROOT/'worker.py'),str(cfg)],check=True)
            for _ in range(150):
                if (root/'.neo-worker/status.json').exists():break
                time.sleep(.02)
            self.assertEqual(o.read(root/'.neo-worker/status.json')['returncode'],0)
            self.assertEqual((root/'done').read_text(),'ok')

    def test_missing_authorization_cannot_start_service(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'config.json'
            o.atomic(p,{'job_id':'neo-test-123456789012','max_runtime_seconds':120,'recovery_seconds':30,
                        'hourly_usd':.1,'max_usd':1,'transfer_reserve_usd':.1})
            with patch.object(o,'command') as c:
                with self.assertRaises(PermissionError):o.launch(p)
                c.assert_not_called()

    def test_archive_preserved_when_optional_validator_fails(self):
        # A bad scientific checkpoint is still evidence; archival is not conditional on an ML import.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);archive=root/'bad-model.tar';archive.write_bytes(b'broken-checkpoint')
            m=root/'m.json'
            o.atomic(m,{'job_id':'neo-test-123456789012','instance_id':42,'label':'neo-test-123456789012',
                        'checkpoint_validation':{'passed':False},'training':{'outcome':'completed','returncode':0,'outputs_valid':True}})
            r=o.finalize(m,archive,o.LocalStore(root/'store'),Provider(),time.time()+5)
            self.assertTrue(r['archive']['verified'])
            self.assertNotEqual(r['outcome'],'completed_archived_shutdown_confirmed')

    def test_failure_and_success_are_distinct_from_archive_and_cleanup(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);archive=root/'a.tar';archive.write_bytes(b'partial')
            m=root/'m.json';o.atomic(m,{'job_id':'neo-test-123456789012','instance_id':42,'label':'neo-test-123456789012',
                                       'training':{'outcome':'failed','returncode':7}})
            r=o.finalize(m,archive,o.LocalStore(root/'store'),Provider(),time.time()+5)
            self.assertEqual(r['outcome'],'failed_or_unknown_training_artifacts_recovered_shutdown_confirmed')


if __name__=='__main__':unittest.main()
