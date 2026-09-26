import json, os, tempfile, unittest, zipfile, subprocess, sys
from pathlib import Path
from unittest.mock import patch
from localrisk.configuration import configured, read_settings
from localrisk.easy import parser, env_role
from collect_results import collect
ROOT=Path(__file__).resolve().parents[1]
class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.path=self.root/'config.json'
        self.data={'defaults':{'base_url':'https://example.invalid/v1','api_key':'fixture-secret-one'},'roles':{'draft':{'base_url':'https://draft.invalid/v1','api_key':'fixture-secret-two'}}};self.save()
    def save(self):self.path.write_text(json.dumps(self.data))
    def test_inheritance_and_stale_environment_isolation(self):
        args=parser().parse_args(['--config',str(self.path)])
        with patch.dict(os.environ,{'TEST_DRAFT_BASE_URL':'https://stale.invalid','SECOND_JUDGE_API_KEY':'stale-key','DRAFT_EXTRA_BODY':'{"bad":true}'}):
            with configured(args):
                r=env_role('LLM');b=env_role('TEST_DRAFT',fallback='DRAFT');k=env_role('SECOND_JUDGE',fallback='DRAFT')
                self.assertEqual(r['model'],'gpt-5.6-terra');self.assertEqual(b['model'],'deepseek-flash')
                self.assertEqual(b['base_url'],'https://draft.invalid/v1');self.assertEqual(k['base_url'],b['base_url'])
                self.assertEqual(os.environ[k['api_key_env']],'fixture-secret-two');self.assertNotIn('bad',b['generation'])
                self.assertNotIn('fixture-secret',json.dumps([r,b,k]))
            self.assertEqual(os.environ['SECOND_JUDGE_API_KEY'],'stale-key')
    def test_separate_role_override_and_http(self):
        self.data['roles']['test_draft']={'api_key':'third-key'};self.data['allow_http']=True;self.save()
        args=parser().parse_args(['--config',str(self.path)])
        with configured(args):
            self.assertTrue(args.allow_http);self.assertEqual(os.environ['TEST_DRAFT_API_KEY'],'third-key')
            self.assertEqual(os.environ['SECOND_JUDGE_API_KEY'],'fixture-secret-two')
        self.assertFalse(args.allow_http)
    def test_invalid_json_and_url_errors_do_not_echo_secrets(self):
        for url in ['[https://example.invalid](https://example.invalid)','https://fixture-secret@host/v1','https://host/v1?key=fixture-secret']:
            self.data['defaults']['base_url']=url;self.save()
            with self.assertRaises(ValueError) as raised:read_settings(self.path)
            self.assertNotIn('fixture-secret',str(raised.exception))
        self.path.write_text('{"api_key":"fixture-secret", broken}')
        with self.assertRaises(ValueError) as raised:read_settings(self.path)
        self.assertNotIn('fixture-secret',str(raised.exception))
    def test_typos_rejected(self):
        self.data['roles']['test']={};self.save()
        with self.assertRaises(ValueError):read_settings(self.path)
    def test_collection_excludes_config_and_scrubs_keys_without_environment(self):
        run=self.root/'run';run.mkdir();(run/'debug.log').write_text('fixture-secret-one and fixture-secret-two')
        (run/'config.json').write_text(self.path.read_text())
        custom=self.root/'other.json';custom.write_text('{"api_key":"custom-credential"}')
        (run/'custom.log').write_text('custom-credential');out=self.root/'return.zip'
        with patch.dict(os.environ,{},clear=True):collect([run],out,self.root,custom)
        with zipfile.ZipFile(out) as z:
            self.assertFalse(any(n.endswith('/config.json') for n in z.namelist()))
            payload=b'\n'.join(z.read(n) for n in z.namelist())
            for key in [b'fixture-secret-one',b'fixture-secret-two',b'custom-credential']:self.assertNotIn(key,payload)
    def test_cli_dry_run_and_key_rotation_preserve_protocol(self):
        out=self.root/'dry';cmd=[sys.executable,str(ROOT/'run_main.py'),'--config',str(self.path),'--dry-run','--out',str(out)]
        result=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
        protocol=(out/'_study/protocol.json').read_bytes();self.data['defaults']['api_key']='rotated-secret';self.save()
        result=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(protocol,(out/'_study/protocol.json').read_bytes())
        for p in out.rglob('*'):
            if p.is_file():
                self.assertNotIn(b'fixture-secret',p.read_bytes());self.assertNotIn(b'rotated-secret',p.read_bytes())
if __name__=='__main__':unittest.main()
