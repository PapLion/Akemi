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
    @unittest.skipUnless(Path('/home/dani.pp/evaluations/cryo-legacy-viability/.venv/bin/python').exists(),
                         'Local ML dependency environment is not present on this host')
    def test_actual_scientific_verifier_imports_in_configured_python(self):
        r=subprocess.run(['/home/dani.pp/evaluations/cryo-legacy-viability/.venv/bin/python',
                          str(o.ROOT/'validate_archive.py'),'--import-check'],capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)['scientific_validator_imports'],'PASS')

    def test_external_arm_failure_prevents_any_paid_create(self):
        class ReadOnlyAPI:
            def __init__(self):self.calls=[]
            def cli(self,*args):
                self.calls.append(args)
                if args==('show','volumes'):return []
                if args==('show','user'):return {'credit':1}
                if args[:2]==('search','offers'):
                    return [{'id':123,'dph_total':.1,'storage_cost':0,'inet_up_cost':0,'inet_down_cost':0}]
                raise AssertionError('Unexpected provider mutation')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);bundle=root/'bundle';bundle.write_bytes(b'frozen')
            cfg={'job_id':'neo-test-123456789012','max_runtime_seconds':120,'recovery_seconds':30,
                 'hourly_usd':.1,'max_usd':1,'transfer_reserve_usd':.1,
                 'authorization_reference':'TEST ONLY (no actual authorization)',
                 'bundle':str(bundle),'bundle_sha256':o.sha(bundle),'python':sys.executable,
                 'required_files':['checkpoint'],'validate_command':['dummy'],
                 'offer_id':123,'selected_offer':{'machine_id':30501},'disk_gb':40,'max_transfer_gb':1}
            config=root/'config.json';o.atomic(config,cfg);api=ReadOnlyAPI()
            with patch.object(o,'PRIVATE',root/'state'),patch.object(o,'helpers',return_value=api),\
                 patch.object(o,'Provider') as provider,patch.object(o,'credential_preflight'),\
                 patch.object(o,'command',return_value=b''),patch.object(o,'DriveStore',return_value=o.LocalStore(root/'storage')),\
                 patch.object(o,'arm',side_effect=TimeoutError('No external receipt')):
                provider.return_value.instances.return_value=[]
                with self.assertRaises(TimeoutError):o.run(config)
            self.assertFalse(any(c[:2]==('create','instance') for c in api.calls))
            self.assertTrue(any(c[:3]==('search','offers','machine_id=30501') for c in api.calls))

    def test_nonfinite_budget_fails_closed(self):
        cfg={'job_id':'neo-test-123456789012','max_runtime_seconds':120,'recovery_seconds':30,
             'hourly_usd':float('nan'),'max_usd':1,'transfer_reserve_usd':.1}
        with self.assertRaises(ValueError):o.validate_budget(cfg)

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
