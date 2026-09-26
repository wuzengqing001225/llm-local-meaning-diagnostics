import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
from localrisk.responses import response_text,ResponseFailure
from localrisk.authoring import DraftClient
from localrisk.backends import run_http

def payload(content='',finish='length'):
 return {'model':'test-model','choices':[{'message':{'content':content,'reasoning_content':'private-reasoning'},'finish_reason':finish}], 'usage':{'completion_tokens':2048,'completion_tokens_details':{'reasoning_tokens':2048}}}
def response(raw):
 r=MagicMock();r.__enter__.return_value.read.return_value=json.dumps(raw).encode();return r
class ResponseTests(unittest.TestCase):
 def test_reasoning_is_not_used_as_answer(self):
  with self.assertRaises(ResponseFailure) as raised:response_text(payload('', 'stop'))
  self.assertEqual(raised.exception.kind,'empty_response');self.assertTrue(raised.exception.metadata['has_reasoning_content'])
  self.assertNotIn('private-reasoning',json.dumps(raised.exception.metadata))
 def test_truncation_is_failure_even_if_nonempty(self):
  with self.assertRaises(ResponseFailure) as raised:response_text(payload('{"answer":"A"}', 'length'))
  self.assertEqual(raised.exception.kind,'truncated_response');self.assertEqual(response_text(payload('A', 'stop')),'A')
 def test_failed_draft_is_logged_but_not_cached_and_can_resume(self):
  with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'TEST_KEY':'unit-secret'}):
   client=DraftClient({'model':'test-model','base_url':'https://example.invalid','api_key_env':'TEST_KEY','generation':{'max_tokens':2048}},d)
   with patch('urllib.request.urlopen',return_value=response(payload())) as api:
    with self.assertRaises(RuntimeError) as raised:client.complete('system','prompt')
    self.assertEqual(api.call_count,1);self.assertIn('reasoning_tokens=2048',str(raised.exception))
   self.assertEqual(len(list(Path(d).glob('*.json'))),0)
   log=next((Path(d)/'_errors').glob('*.json')).read_text();self.assertNotIn('unit-secret',log);self.assertNotIn('private-reasoning',log)
   with patch('urllib.request.urlopen',return_value=response(payload('{}','stop'))) as api:
    self.assertEqual(client.complete('system','prompt'),'{}');self.assertEqual(client.complete('system','prompt'),'{}');self.assertEqual(api.call_count,1)
 def test_reader_empty_output_is_error_not_wrong_answer(self):
  cfg={'model':'test-model','base_url':'https://example.invalid','api_key_env':'TEST_KEY'}
  plan=({'reader':cfg,'mode':'real','plan_id':'p'},[{'request_id':'r','payload':{},'n_options':2}],[])
  with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'TEST_KEY':'unit-secret'}),patch('localrisk.backends.load_plan',return_value=plan),patch('urllib.request.urlopen',return_value=response(payload('', 'stop'))):
   out=Path(d)/'predictions.jsonl';result=run_http('dummy',out)
   self.assertEqual(result['new_errors'],1);row=json.loads(out.read_text());self.assertEqual(row['status'],'error');self.assertEqual(row['error_type'],'empty_response');self.assertNotIn('prediction',row)
