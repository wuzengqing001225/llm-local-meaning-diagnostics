from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text())
errors=[]
for item in manifest['files']:
 p=root/item['path']
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append(item['path'])
if errors:raise SystemExit('Missing or changed release files: '+', '.join(errors))
print('Verified',len(manifest['files']),'release files.')
