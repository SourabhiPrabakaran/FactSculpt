"""Read-only recovery search; reconstruct source-generated data in a separate copy."""
from pathlib import Path
import collections, hashlib, importlib.metadata, importlib.util, json, os, platform, shutil, subprocess, sys, zipfile
H=Path(__file__).resolve().parent; W=H.parents[1]; SRC=W/'FactSculpt'; A=W/'audit_workspace'; COPY=A/'FactSculpt'
H.mkdir(exist_ok=True); (H/'logs').mkdir(exist_ok=True,parents=True); A.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args,cwd=None):
    env=os.environ.copy();env['PYTHONPATH']=str(A/'deps')+os.pathsep+str(COPY)
    env['HF_HUB_OFFLINE']='1';env['TRANSFORMERS_OFFLINE']='1';env['PYTHONDONTWRITEBYTECODE']='1'
    r=subprocess.run(args,cwd=cwd or W,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (H/'logs'/f'{name}.txt').write_text('COMMAND: '+subprocess.list2cmdline(args)+'\nCWD: '+str(cwd or W)+'\nEXIT: '+str(r.returncode)+'\nSTDOUT:\n'+r.stdout+'\nSTDERR:\n'+r.stderr,encoding='utf-8')
    return r
original={p.relative_to(SRC).as_posix():sha(p) for p in SRC.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
(H/'original_source_hashes.json').write_text(json.dumps(original,indent=2))
archives=[]
for p in [W.parent/'FactSculpt_minimal.zip',W.parent/'dist.zip']:
    if p.exists():
        with zipfile.ZipFile(p) as z:
            names=z.namelist(); relevant=[n for n in names if any(t in n.lower() for t in ['factsculpt','frozen_test','preregistration','pytest','test_','results','checkpoint'])]
            members=[]
            for n in names:
                if not n.endswith('/'):
                    data=z.read(n)
                    members.append(dict(name=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
            archives.append(dict(path=str(p),sha256=sha(p),members=members,relevant_names=relevant))
found=[];errors=[]
tokens=['factsculpt','frozen_test','preregistration','freeze_manifest','run_final_test']
roots=[W.parent,Path.home()/'Documents',Path.home()/'Desktop']
for root in roots:
    def err(e):errors.append(str(e))
    for base,dirs,files in os.walk(root,onerror=err):
        dirs[:]=[d for d in dirs if d not in ['node_modules','.git','__pycache__','.venv','venv','deps'] and Path(base)/d not in [W/'paper_foundation',W/'audit_workspace']]
        for f in files:
            if any(t in f.lower() for t in tokens):found.append(str(Path(base)/f))
cachepaths=[Path.home()/'.cache/huggingface',Path.home()/'.cache/torch',Path.home()/'.cache/torch/sentence_transformers']
for name in ['HF_HOME','HF_HUB_CACHE','TRANSFORMERS_CACHE','SENTENCE_TRANSFORMERS_HOME']:
    if os.getenv(name):cachepaths.append(Path(os.environ[name]))
cache=[]
for p in cachepaths:
    cache.append(dict(path=str(p),exists=p.exists(),files=[str(q.relative_to(p)) for q in p.rglob('*') if q.is_file()] if p.exists() else []))
packages={}
for n in ['pydantic','numpy','scipy','scikit-learn','pytest','pandas','matplotlib','streamlit','sentence-transformers','transformers','torch']:
    try:packages[n]=importlib.metadata.version(n)
    except importlib.metadata.PackageNotFoundError:packages[n]=None
discovery=dict(search_roots=list(map(str,roots)),excluded_directories=['node_modules','.git','__pycache__','.venv','venv','deps','generated audit outputs'],search_filename_terms=tokens,matching_files=found,search_errors=errors,archives=archives,caches=cache,environment=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),packages=packages),scope_limit='No claim of exhaustive disk/cloud/other-account search; Documents/Desktop/Downloads targeted filenames plus complete supplied archives and workspace inventory.')
(H/'discovery.json').write_text(json.dumps(discovery,indent=2),encoding='utf-8')
if not COPY.exists():shutil.copytree(SRC,COPY,ignore=shutil.ignore_patterns('__pycache__','data'))
run('normal_import_original',[sys.executable,'-c',f"import sys; sys.path.insert(0,{str(SRC)!r}); import factsculpt.classifier; print('normal package import OK')"])
run('original_tests_command',[sys.executable,'-m','pytest',str(SRC/'tests'),'-q'])
run('missing_final_runner',[sys.executable,'-m','factsculpt.experiments.run_final_test'])
run('rebuild_splits',[sys.executable,'-c','from factsculpt.dataset.builder import build_all_splits; build_all_splits()'],COPY)
# Newly generated manifest contains a historical literal; quarantine it as raw generator output.
manifest=COPY/'data/splits/FREEZE_MANIFEST.md'
if manifest.exists():shutil.copy2(manifest,H/'raw_generated_manifest_NOT_PREREGISTRATION.md')
summary={}; sets={}; allrows={}
for name in ['train','val','frozen_test','minimal_pairs','hard_cases']:
    p=COPY/f'data/splits/{name}.json'
    if not p.exists():continue
    rows=json.loads(p.read_text());allrows[name]=rows
    clusters={r['source_cluster_id'] for r in rows if 'source_cluster_id' in r}
    sources={r['source_text'] for r in rows}; sets[name]=(clusters,sources)
    summary[name]=dict(count=len(rows),clusters=len(clusters),distinct_sources=len(sources),classes=dict(collections.Counter(r.get('main_class','missing') for r in rows)),domains=dict(collections.Counter(r.get('domain','missing') for r in rows)),directions=dict(collections.Counter(r.get('direction','missing') for r in rows)),sha256=sha(p))
overlap={}
for a,b in [('train','val'),('train','frozen_test'),('val','frozen_test')]:
    if a in sets and b in sets:
        grams=lambda xs:{s[i:i+5].lower() for s in xs for i in range(max(0,len(s)-4))}
        ga,gb=grams(sets[a][1]),grams(sets[b][1]); shared=ga&gb
        overlap[f'{a}__{b}']=dict(shared_cluster_ids=len(sets[a][0]&sets[b][0]),shared_exact_sources=len(sets[a][1]&sets[b][1]),shared_character_5grams=len(shared),sample_shared_5grams=sorted(shared)[:20])
claims={'train':'06fbe863dd47','val':'feda90525667','frozen_test':'9dd24d178534','minimal_pairs':'cbff3beeb1e5','hard_cases':'e0f3a224b72b'}
for k,prefix in claims.items():
    if k in summary:summary[k]['readme_hash_prefix']=prefix;summary[k]['prefix_matches']=summary[k]['sha256'].startswith(prefix)
(H/'regenerated_dataset_audit.json').write_text(json.dumps(dict(provenance='NEW source-generated synthetic records, not recovered historical files or human gold. Class labels and shifts are generator assertions.',splits=summary,overlap=overlap),indent=2),encoding='utf-8')
after={p.relative_to(SRC).as_posix():sha(p) for p in SRC.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
(H/'original_preservation.json').write_text(json.dumps(dict(unchanged=original==after,files_checked=len(original),added=list(after.keys()-original.keys()),removed=list(original.keys()-after.keys())),indent=2))
print(json.dumps(dict(archives=len(archives),rebuild=summary,overlap=overlap,original_unchanged=original==after),indent=2))
