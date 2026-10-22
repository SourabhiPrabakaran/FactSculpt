"""Five-class metrics computed directly from per-example outputs; no sklearn dependency."""
LABELS=['C1','C2','C3','C4','C5']
def compute(rows,threshold=.65):
    if not rows:raise ValueError('Cannot evaluate an empty dataset')
    matrix={a:{b:0 for b in LABELS} for a in LABELS}
    for r in rows:
        if r['gold'] not in LABELS or r['predicted'] not in LABELS:raise ValueError('Unknown label')
        matrix[r['gold']][r['predicted']]+=1
    per={}
    for c in LABELS:
        tp=matrix[c][c];fp=sum(matrix[a][c] for a in LABELS if a!=c);fn=sum(matrix[c][b] for b in LABELS if b!=c)
        per[c]=dict(f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,recall=tp/(tp+fn) if tp+fn else 0,support=tp+fn)
    c3=[r['support'] for r in rows if r['gold']=='C3' and r.get('support') is not None]
    c2=[r['support'] for r in rows if r['gold']=='C2' and r.get('support') is not None]
    observed=[c for c in LABELS if per[c]['support']>0]
    return dict(n=len(rows),accuracy=sum(matrix[c][c] for c in LABELS)/len(rows),macro_f1=sum(per[c]['f1'] for c in LABELS)/5,macro_f1_observed_gold_classes=sum(per[c]['f1'] for c in observed)/len(observed),observed_gold_classes=observed,per_class=per,confusion_matrix=matrix,sbr=sum(s>=threshold for s in c3)/len(c3) if c3 else None,directional_sensitivity=sum(c2)/len(c2)-sum(c3)/len(c3) if c2 and c3 else None,support_threshold=threshold,c3_denominator=len(c3))
