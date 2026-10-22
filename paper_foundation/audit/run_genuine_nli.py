"""Record real NLI outputs or fail; never generate heuristic replacements."""
from pathlib import Path
import argparse,hashlib,json
from strict_nli import StrictNLI
p=argparse.ArgumentParser()
p.add_argument('--data',required=True);p.add_argument('--output',required=True)
p.add_argument('--model',required=True);p.add_argument('--revision',required=True)
p.add_argument('--allow-download',action='store_true');p.add_argument('--support-threshold',type=float,default=.65)
args=p.parse_args()
if not 0<=args.support_threshold<=1:raise ValueError('Support threshold outside [0,1]')
path=Path(args.data);data=json.loads(path.read_text(encoding='utf-8'))
if not data:raise ValueError('Empty dataset')
engine=StrictNLI(args.model,args.revision,local_files_only=not args.allow_download)
rows=[]
for r in data:
    o=engine.predict(r['source_text'],r['enhanced_text'])
    o.update(example_id=r.get('example_id',r.get('pair_id')),generator_class=r.get('main_class'),source_cluster_id=r.get('source_cluster_id'))
    rows.append(o)
out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
temp=out.with_suffix(out.suffix+'.tmp')
with temp.open('w',encoding='utf-8') as f:
    for r in rows:f.write(json.dumps(r)+'\n')
temp.replace(out)
c3=[r['scores']['entailment'] for r in rows if r['generator_class']=='C3'];c2=[r['scores']['entailment'] for r in rows if r['generator_class']=='C2']
summary=dict(status='COMPLETED_GENUINE_NLI',model=args.model,revision=args.revision,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),prediction_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),n=len(rows),support_threshold=args.support_threshold,c3_n=len(c3),sbr=sum(s>=args.support_threshold for s in c3)/len(c3) if c3 else None,directional_sensitivity=sum(c2)/len(c2)-sum(c3)/len(c3) if c3 and c2 else None,note='Raw NLI has 3 labels, not the FactSculpt 5-way taxonomy. No invented five-way label mapping; generator-class analysis is synthetic unless independently validated.')
out.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
