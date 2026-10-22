"""Metric-by-metric documentation registry; never promote new runs to historical evidence."""
from pathlib import Path
import csv,json,re
H=Path(__file__).resolve().parent;W=H.parents[1];R=W/'FactSculpt'
rows=[]
MISSING='Unverified because evidence is missing'
VERIFIED='Verified and reproducible'
CONTRADICTED='Contradicted by other evidence'
def add(location,subject,metric,value,status=MISSING,artifact='No original predictions, run log or complete result artifact recovered',action='Recover original data hashes, configuration and per-example predictions; recompute independently',qualification='Historical numerical claim is not validated by a new synthetic run'):
    rows.append(dict(id=f'M{len(rows)+1:03}',source=location,subject=subject,metric=metric,documented_value=value,supporting_artifact=artifact,verification_status=status,required_action=action,qualification=qualification))
lines=(R/'README.md').read_text(encoding='utf-8').splitlines(); headers=[]
for i,line in enumerate(lines,1):
    if not line.startswith('|'):headers=[];continue
    cells=[v.strip() for v in line.strip('|').split('|')]
    if all(re.match(r'^:?-+:?$',x.replace(' ','')) for x in cells):continue
    if not headers:headers=cells;continue
    subject=re.sub(r'\*|\$','',cells[0])
    for j,value in enumerate(cells[1:],1):
        # Skip C1/C2 labels alone; retain numeric values, intervals and hashes.
        if not re.search(r'\d',re.sub(r'C[1-5]','',value)):continue
        name=headers[j] if j<len(headers) else f'column_{j}'
        status=MISSING;artifact='No original underlying result artifact recovered';q='Reported number is historical and unverified'
        action='Recover original run lineage and predictions; recompute on the exact original split'
        if 60<=i<=64:
            status=VERIFIED if j in [1,2,3,4] and i!=64 else MISSING
            artifact='regenerated_dataset_audit.json; audit_workspace/FactSculpt/data/splits/*.json'
            q='Only reconstructed-source counts/distributions verified; historical dataset identity unverified'
            action='Retain explicit synthetic reconstruction provenance; obtain historical originals before attributing old results'
            if j==5:
                status=VERIFIED if i in [63,64] else CONTRADICTED
                q='Minimal/hard checksum PREFIX reproduced' if i in [63,64] else 'Current generator bytes differ from published prefix; LF normalization also does not match; historical data not recovered'
            if i==64 and j in [1,2]:
                status=VERIFIED if j==1 else MISSING
                q='10 cases regenerated; no cluster-ID field, so 10 clusters not established'
        if i in [17,75] and j in [1,2,3,4]:
            status=CONTRADICTED;q='Documentation gives incompatible headline/table numbers without run/model lineage; neither value selected';action='Identify whether these are different models, data versions or inference paths; link each to immutable original runs'
        add(f'README.md:{i}',subject,name,value,status,artifact,action,q)

extras=[
(3,'CI badge','Passing historical tests','233'),
(9,'Central diagnostic claim','Pretrained/model SBR','>=92.8%'),
(36,'NLI narrative','SBR range','92.8% to 100.0%'),
(56,'Benchmark','Pair count / cluster count / domains','3600 / 1200 / 3'),
(70,'Statistical protocol','Bootstrap resamples / interval','10000 / 95%'),
(85,'NLI narrative','SBR range','92.8% to 99.4%'),
(88,'Minimal pairs NLI','Mean strengthened support','0.6833'),
(88,'Minimal pairs NLI','Mean weakened support','0.7167'),
(88,'Minimal pairs NLI','Directional sensitivity','+0.0333'),
(89,'Minimal pairs FactSculpt','Directional sensitivity','+0.7500'),
(89,'Minimal pairs FactSculpt','Counterfactual isolation','100.0% across 6 dimensions'),
(92,'Repair','Actively edited rate','88.0%'),
(92,'Repair','Verbatim source rate','0.0%'),
(92,'Repair','Semantic preservation (actually token Jaccard)','0.7810'),
(92,'Repair','Residual lexical-judge exaggeration','2.0%'),
(92,'Repair','Residual NLI-judge exaggeration','16.0%'),
(92,'Repair','Mean iterations','0.9'),
(103,'Leakage audit','Shared character 5-grams','0'),
(176,'Historical test protocol','Number of final-test evaluations','exactly once')]
for line,subject,metric,value in extras:
    status=MISSING;artifact='No original supporting artifacts recovered';q='Historical claim unverified'
    if line==56:status=VERIFIED;artifact='regenerated_dataset_audit.json';q='Counts reproducible from current source; original split identity unverified'
    if line==103:status=CONTRADICTED;artifact='regenerated_dataset_audit.json overlap';q='Reconstructed source corpora share 2548/2520/2461 distinct lowercased character 5-grams; not a near-duplicate rate'
    add(f'README.md:{line}',subject,metric,value,status,artifact,qualification=q)
# Embedded UI numerical values are demonstration constants, not measured outputs.
for i,line in enumerate((R/'web/app.js').read_text(encoding='utf-8').splitlines(),1):
    if re.search(r'confidence:\s*"\d+%"|score:\s*-?\d|label:\s*"[+-]?\d',line):
        add(f'web/app.js:{i}','Static UI demonstration','Preset confidence / attribute score',line.strip(),CONTRADICTED,'Literal PRESETS data in source','Label as illustrative UI data and exclude from research evaluation','Value exists as a constant; it is not a measured model result')
for i,line in enumerate((R/'app.py').read_text(encoding='utf-8').splitlines(),1):
    if '99.4%' in line:add(f'app.py:{i}','Streamlit diagnostic','Claimed standard-NLI SBR','99.4%',MISSING,'Hardcoded displayed text; no independent measurement','Replace with run-specific measured score or remove empirical wording','Displayed for C3 regardless of measured NLI decision')
htmlclaims=[(232,'Default displayed confidence','94%'),(343,'Residual exaggeration','0.0%'),(347,'Semantic preservation','84.2%'),(367,'Claimed benchmark training pairs','3600'),(367,'Claimed leakage','0%'),(367,'Claimed human Cohen kappa','0.7080'),(381,'Raw-text Macro-F1','0.7230'),(383,'Improvement versus NLI','+52.6%'),(386,'Oracle upper bound','0.9543'),(391,'Claimed NLI strengthening blindness','93.9%'),(396,'Claimed human Cohen kappa','0.7080')]
for line,metric,value in htmlclaims:
    q='Static HTML literal; no underlying measurement or human annotation artifact recovered'
    if line==383:q+='; .7230 minus .1968 is .5262 (52.62 percentage points), not 52.6% relative improvement'
    if metric=='Claimed human Cohen kappa':q+='; conflicts with README statement that human evidence awaits collection'
    add(f'web/index.html:{line}','Static research/repair UI',metric,value,MISSING,'Static HTML markup only; no original result/annotation artifact','Remove or clearly label illustrative values until actual measurements exist',q)
new=H/'results/diagnostic_summary.json'
if new.exists():
    for system,m in json.loads(new.read_text())['systems'].items():
        for field in ['n','macro_f1','macro_f1_observed_gold_classes','accuracy','sbr','directional_sensitivity']:
            if m.get(field) is not None:
                add('NEW audit results/diagnostic_summary.json',system,field,str(m[field]),VERIFIED,'Saved JSONL predictions; independent_metrics.py; diagnostic_experiments.txt','Use only as explicitly synthetic, reconstructed-data diagnostics; do not replace historical README scores','Current source-generated labels; no human validation or genuine NLI inference')
        for c,v in m['per_class'].items():
            add('NEW audit results/diagnostic_summary.json',system,f'{c} recall',str(v['recall']),VERIFIED,'Saved JSONL predictions and independent confusion matrix','Preserve class support and synthetic provenance','Zero-support classes have recall zero by declared convention')
with (H/'metric_verification.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
md=['# Metric-by-metric verification registry','', 'Status applies to the precise qualification. Reconstructed counts do not verify historical model results. Numerical cells preserve reported confidence intervals and p-values verbatim. UI constants are listed separately as demonstration values.','', '| ID | Source | Subject / metric | Documented value | Status | Evidence / qualification | Action |','|---|---|---|---|---|---|---|']
for r in rows:
    esc=lambda s:s.replace('|','/').replace('\n',' ')
    md.append('| '+' | '.join(map(esc,[r['id'],r['source'],r['subject']+' / '+r['metric'],r['documented_value'],r['verification_status'],r['supporting_artifact']+'; '+r['qualification'],r['required_action']]))+' |')
(H/'METRIC_VERIFICATION.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(f'{len(rows)} documented metric entries')
