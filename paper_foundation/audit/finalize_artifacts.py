"""Summarize observed outputs, record provenance and final integrity hashes."""
from pathlib import Path
import collections,hashlib,importlib.metadata,json
H=Path(__file__).resolve().parent;W=H.parents[1];R=W/'FactSculpt';C=W/'audit_workspace/FactSculpt';OUT=H/'results'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((H/'discovery.json').read_text());original=json.loads((H/'original_source_hashes.json').read_text())
for a in d['archives']:
    if Path(a['path']).name=='FactSculpt_minimal.zip':
        comparisons=[]
        for item in a['members']:
            relative=item['name'].removeprefix('FactSculpt/')
            comparisons.append(dict(path=relative,same_as_workspace=original.get(relative)==item['sha256']))
        d['original_archive_source_comparison']=comparisons
(H/'discovery.json').write_text(json.dumps(d,indent=2))
after={p.relative_to(R).as_posix():sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
(H/'original_preservation.json').write_text(json.dumps(dict(unchanged=after==original,files_checked=len(original),differences=[k for k in set(original)|set(after) if original.get(k)!=after.get(k)]),indent=2))
requirements=sorted({p.metadata['Name']+'=='+p.version for p in importlib.metadata.distributions(path=[str(W/'audit_workspace/deps')])}|{'pydantic=='+importlib.metadata.version('pydantic')})
(H/'requirements-audit.lock.txt').write_text('\n'.join(requirements)+'\n')
notice='''# Audit copy provenance

This is a separate working copy of the supplied minimal source snapshot. Original project source hashes are preserved in paper_foundation/audit/original_source_hashes.json.

data/splits/*.json were regenerated during the 15 October 2026 audit. They are synthetic template outputs with generator-assigned labels, NOT recovered historical files, human annotations, or a newly preregistered untouched final test. The generator's historical date literal is not evidence of freeze chronology. Original output is archived separately as raw_generated_manifest_NOT_PREREGISTRATION.md. New model predictions, tests and metric calculations live under paper_foundation/audit.
'''
(C/'AUDIT_COPY_NOTICE.md').write_text(notice)
manifest=C/'data/splits/FREEZE_MANIFEST.md'
if manifest.exists():
    raw=manifest.read_text()
    if not raw.startswith('# NOT A HISTORICAL FREEZE OR PREREGISTRATION'):
        manifest.write_text('# NOT A HISTORICAL FREEZE OR PREREGISTRATION\n\nGenerated during the current audit; see AUDIT_COPY_NOTICE.md. The following is unmodified generator output, including a historical date literal.\n\n'+raw)
summary=json.loads((OUT/'diagnostic_summary.json').read_text())
errors={}
for name,m in summary['systems'].items():
    path=OUT/f'{name}_predictions.jsonl';rows=[json.loads(s) for s in path.read_text().splitlines()]
    wrong=[r for r in rows if r['gold']!=r['predicted']]
    errors[name]=dict(n=len(rows),errors=len(wrong),confusions=dict(collections.Counter(f"{r['gold']}->{r['predicted']}" for r in wrong)),examples=wrong[:5])
(OUT/'error_analysis.json').write_text(json.dumps(dict(note='Errors relative to generator assertions, not independently annotated human truth.',systems=errors),indent=2))
dataset=json.loads((H/'regenerated_dataset_audit.json').read_text())
for k in dataset['splits']:
    p=C/f'data/splits/{k}.json';dataset['splits'][k]['lf_normalized_sha256']=hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
(H/'regenerated_dataset_audit.json').write_text(json.dumps(dataset,indent=2))
manifest={p.relative_to(H).as_posix():sha(p) for p in H.rglob('*') if p.is_file() and p.name!='audit_output_hashes.json' and '__pycache__' not in p.parts}
(H/'audit_output_hashes.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(dict(original_source_unchanged=after==original,archive_files_matching=sum(c['same_as_workspace'] for c in d['original_archive_source_comparison']),archive_files_total=len(d['original_archive_source_comparison']),systems_evaluated=len(summary['systems']),saved_predictions=sum(m['n'] for m in summary['systems'].values()))))
