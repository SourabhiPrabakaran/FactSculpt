"""New deterministic synthetic diagnostics. Not historical final-test reproduction."""
from pathlib import Path
import collections,hashlib,json,sys,time
import numpy as np
H=Path(__file__).resolve().parent; W=H.parents[1]; R=W/'audit_workspace/FactSculpt'
sys.path.insert(0,str(R));sys.path.insert(0,str(H))
from independent_metrics import compute
from factsculpt.experiments.baselines import MajorityBaseline,LexicalOverlapBaseline,EmbeddingSimilarityBaseline,NLIOnlyBaseline
from factsculpt.extraction.regex import RegexEvidenceProfileExtractor
from factsculpt.features.extraction import extract_pair_features
from factsculpt.dataset.schema import PairExample
from factsculpt.classifier.rules import ResearchRuleBasedClassifier
from factsculpt.classifier.learned import LearnedExaggerationClassifier
from factsculpt.models import AtomicClaim
from factsculpt.differencing.engine import AttributeDifferenceEngine
from factsculpt.scales.ordinal_scaler import BradleyTerryOrdinalScaler
from factsculpt.features.generator import EvidenceDeviationFeatureGenerator
from factsculpt.nli.models import EvidenceAnalysisResult,NLIResult,NLILabel

OUT=H/'results';OUT.mkdir(exist_ok=True)
raw={k:json.loads((R/f'data/splits/{k}.json').read_text()) for k in ['train','val','frozen_test','minimal_pairs','hard_cases']}
ext=RegexEvidenceProfileExtractor(); clf=ResearchRuleBasedClassifier(); summaries={}; checks=[]
def save(name,rows,threshold=.65):
    path=OUT/f'{name}_predictions.jsonl'
    with path.open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    # Independent recomputation after reopening actual saved predictions.
    reread=[json.loads(s) for s in path.read_text().splitlines()]
    m=compute(reread,threshold);m['predictions_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    summaries[name]=m;return m
def prediction(p,out,backend,support=None):
    return dict(id=p.get('example_id',p.get('pair_id',p.get('case_id'))),cluster=p.get('source_cluster_id'),gold=p.get('main_class',p.get('gold_class')),predicted=out.classification_code.value if hasattr(out,'classification_code') else out.predicted_class.value,support=support,backend=backend,source=p['source_text'],rewrite=p['enhanced_text'])

for key,b in [('majority',MajorityBaseline()),('lexical_jaccard',LexicalOverlapBaseline()),('bag_of_words_cosine',EmbeddingSimilarityBaseline()),('lexical_pseudo_nli',NLIOnlyBaseline())]:
    b.fit_or_tune(raw['train'],raw['val']);rows=[]
    for p in raw['frozen_test']:
        o=b.predict_pair(p['source_text'],p['enhanced_text']);rows.append(prediction(p,o,key,o.support_score))
    m=save(key,rows,b.support_threshold)
    original=b.evaluate_dataset(raw['frozen_test'],split_name='NEW_reconstructed_diagnostic')
    # Original implementation rounds each per-class F1 before averaging.
    assert abs(m['macro_f1']-original.macro_f1)<.00011
    assert abs(m['accuracy']-original.accuracy)<.00011
    checks.append(dict(system=key,original_metric_agrees_with_independent=True,original_macro_f1=original.macro_f1,independent_macro_f1=m['macro_f1']))

datasets={k:[PairExample(**p) for p in raw[k]] for k in ['train','val','frozen_test']}
def feat(p,mode):
    return extract_pair_features(p,use_predicted_extraction=mode=='regex',extractor=ext)
for mode in ['regex','oracle']:
    rows=[]
    for p,d in zip(raw['frozen_test'],datasets['frozen_test']):
        f=feat(d,mode);o=clf.classify(f)
        rows.append(prediction(p,o,f'{mode}_attributes+lexical_pseudo_nli',f.entailment_score))
    save('research_rules_'+mode,rows)
    for modeltype in ['logreg','gradient_boosting']:
        model=LearnedExaggerationClassifier(model_type=modeltype)
        def matrix(split):
            return np.array([feat(p,mode).to_feature_vector() for p in datasets[split]],dtype=np.float32),np.array([int(p.main_class.value[1:])-1 for p in datasets[split]])
        x,y=matrix('train');xv,yv=matrix('val');model.fit(x,y,xv,yv)
        rows=[]
        for p,d in zip(raw['frozen_test'],datasets['frozen_test']):
            f=feat(d,mode);o=model.classify(f);r=prediction(p,o,f'{modeltype}:{mode}_attributes+lexical_pseudo_nli',None)
            r.update(probabilities=o.probabilities,abstain=o.abstain,calibrated=model.calibrated_model is not None)
            rows.append(r)
        save(modeltype+'_'+mode,rows)

# Genuine component substitution: rerun difference engine with and without scaler
# on the SAME regex-extracted profiles. No gold shift vector is used here.
for name,engine in [('handcoded',AttributeDifferenceEngine()),('seed_ordinal',AttributeDifferenceEngine(ordinal_scaler=BradleyTerryOrdinalScaler()))]:
    rows=[]
    for p in raw['minimal_pairs']:
        s=AtomicClaim(claim_id='s',text=p['source_text']);g=AtomicClaim(claim_id='g',text=p['enhanced_text'])
        s.profile=ext.extract_profile(s);g.profile=ext.extract_profile(g);d=engine.compare(s,g)
        # Explicit neutral placeholder isolates attribute behavior, not NLI accuracy.
        n=NLIResult(source_claim_id='s',generated_claim_id='g',label=NLILabel.NEUTRAL,entailment_score=0,neutral_score=1,contradiction_score=0,model_name='audit_neutral_placeholder')
        f=EvidenceDeviationFeatureGenerator().generate(EvidenceAnalysisResult(source_claim_id='s',generated_claim_id='g',nli_result=n,attribute_difference=d))
        o=clf.classify(f);r=prediction(p,o,'regex_profiles+'+name+'+neutral_placeholder')
        r.update(attribute=p['attribute'],direction=p['direction'],predicted_shifts=d.shift_vector,generator_shifts=p['shift_vector'])
        rows.append(r)
    save('minimal_pairs_'+name,rows)
    counts=collections.defaultdict(lambda:collections.Counter())
    for r in rows:
        counts[r['attribute']]['n']+=1;counts[r['attribute']]['label_correct']+=r['gold']==r['predicted']
        counts[r['attribute']]['target_shift_sign_correct']+=(0 if r['generator_shifts'][r['attribute']]==0 else (1 if r['generator_shifts'][r['attribute']]>0 else -1))==(0 if abs(r['predicted_shifts'][r['attribute']])<=.05 else (1 if r['predicted_shifts'][r['attribute']]>0 else -1))
    summaries['minimal_pairs_'+name]['by_attribute']={k:dict(v) for k,v in counts.items()}

# Independently judged repair study is blocked. Only internal mechanical behavior
# is executed on the supplied curated hard-case definitions, preserving case IDs.
import factsculpt.extraction.llm as llm
from factsculpt.repair.pipeline import AttributeTargetedRepairPipeline
old=llm.LLMEvidenceProfileExtractor;llm.LLMEvidenceProfileExtractor=lambda:ext
try:
    repairs=[]
    for p in raw['hard_cases']:
        r=AttributeTargetedRepairPipeline().repair(p['source_text'],p['enhanced_text'])
        repairs.append(dict(case_id=p['case_id'],generator_gold=p['gold_class'],result=r.model_dump()))
    (OUT/'hard_case_repair_internal_only.json').write_text(json.dumps(repairs,indent=2))
finally:llm.LLMEvidenceProfileExtractor=old
(OUT/'diagnostic_summary.json').write_text(json.dumps(dict(scope='NEW synthetic diagnostics; generator labels NOT human gold; main data hashes differ from README; no actual NLI or embeddings; no historical confidence intervals or significance reproduction.',systems=summaries,metric_crosschecks=checks),indent=2))
table=['# Newly executed synthetic diagnostics','', 'These numbers describe the reconstructed diagnostic data only. No historical result is certified. Macro-F1 (5) averages C1-C5 with zero for absent classes. Observed-class Macro-F1 averages classes present in the gold data (3 for minimal pairs). SBR is calculated from each named support signal, never substituted with class confidence. Learned models have no independently defined support score here.','', '| System / condition | N | Macro-F1 (5) | Macro-F1 (observed) | Accuracy | SBR |','|---|---:|---:|---:|---:|---:|']
for k,m in summaries.items():table.append(f"| {k} | {m['n']} | {m['macro_f1']:.6f} | {m['macro_f1_observed_gold_classes']:.6f} | {m['accuracy']:.6f} | {m['sbr'] if m['sbr'] is not None else 'N/A'} |")
(OUT/'diagnostic_results.md').write_text('\n'.join(table)+'\n')
print('\n'.join(table))
