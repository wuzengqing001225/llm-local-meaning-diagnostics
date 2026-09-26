import urllib.request,json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
url='https://doc2dial.github.io/multidoc2dial/file/multidoc2dial.zip'
p=ROOT/'multidoc2dial.zip'
if not p.exists():
 with urllib.request.urlopen(url,timeout=60) as r:
  limit=80*1024*1024;length=r.headers.get('Content-Length')
  if length and int(length)>limit:raise RuntimeError('Archive exceeds bounded preflight download size')
  data=r.read(limit+1)
  if len(data)>limit:raise RuntimeError('Archive too large for bounded preflight')
 p.write_bytes(data)
with zipfile.ZipFile(p) as z:
 inventory=[{'name':i.filename,'uncompressed_bytes':i.file_size} for i in z.infolist()]
 print(json.dumps(inventory,indent=2))
 for info in z.infolist():
  if info.filename.endswith('.json') and info.file_size<200*1024*1024:
   dest=ROOT/Path(info.filename).name
   if not dest.exists():dest.write_bytes(z.read(info.filename))
manifest={'url':url,'archive_bytes':p.stat().st_size,'archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':inventory,'use':'source/data feasibility only; no model outcomes'}
(ROOT/'download_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
