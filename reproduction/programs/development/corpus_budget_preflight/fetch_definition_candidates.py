from pathlib import Path
import urllib.request,hashlib,json,tarfile,io
ROOT=Path(__file__).resolve().parent/'candidate_sources';ROOT.mkdir(exist_ok=True)
urls={'sara.tar.gz':'https://nlp.jhu.edu/law/sara/sara.tar.gz','gitlab_support.html':'https://handbook.gitlab.com/handbook/support/support-idk/','gitlab_sales.html':'https://handbook.gitlab.com/handbook/sales/sales-term-glossary/','gitlab_licensing.html':'https://handbook.gitlab.com/handbook/support/license-and-renewals/license-and-renewals-glossary/'}
manifest=[]
for name,url in urls.items():
 p=ROOT/name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=60) as r:data=r.read(30*1024*1024+1)
  if len(data)>30*1024*1024:raise ValueError('Source exceeds bounded download')
  p.write_bytes(data)
 manifest.append({'file':name,'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 print(name,p.stat().st_size,flush=True)
with tarfile.open(ROOT/'sara.tar.gz','r:gz') as tar:
 members=[{'name':m.name,'size':m.size} for m in tar.getmembers() if m.isfile()]
 (ROOT/'sara_archive_inventory.json').write_text(json.dumps(members,indent=2)+'\n')
 for m in tar.getmembers():
  if m.isfile() and ('statutes/source/' in m.name or 'license' in m.name.lower() or 'readme' in m.name.lower() or m.name.endswith('splits/train')):
   dest=ROOT/'sara_inspect'/m.name
   if not dest.resolve().is_relative_to((ROOT/'sara_inspect').resolve()):raise ValueError('Unsafe archive member')
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(tar.extractfile(m).read())
(ROOT/'download_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Source definitions and provenance saved; no target model calls')
