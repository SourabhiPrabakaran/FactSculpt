"""New audit tests; neither recovered historical tests nor human evaluation."""
import importlib.util,json,sys
from pathlib import Path
import pytest
H=Path(__file__).resolve().parent; W=H.parents[1]
sys.path.insert(0,str(H));sys.path.insert(0,str(W/'audit_workspace/FactSculpt'))
from independent_metrics import compute
from strict_nli import label_mapping,StrictNLI

def test_independent_metrics_hand_calculated():
    # Deliberately artificial unit-test fixture, NOT a research dataset.
    rows=[dict(gold=c,predicted=c,support=.9) for c in ['C1','C2','C3','C4','C5']]
    m=compute(rows);assert m['accuracy']==1 and m['macro_f1']==1 and m['c3_denominator']==1
    rows[-1]['predicted']='C1';m=compute(rows)
    assert m['accuracy']==.8 and abs(m['macro_f1']-(2/3+3)/5)<1e-12

def test_metrics_no_empty_or_unknown():
    with pytest.raises(ValueError):compute([])
    with pytest.raises(ValueError):compute([dict(gold='C6',predicted='C1')])

def test_absent_classes_macro_denominator_explicit():
    m=compute([dict(gold='C1',predicted='C1')])
    assert m['macro_f1']==.2 and m['macro_f1_observed_gold_classes']==1

@pytest.mark.parametrize('mapping',[{0:'LABEL_0',1:'LABEL_1',2:'LABEL_2'},{0:'entailment',1:'entailment',2:'neutral'},{0:'positive',1:'negative',2:'neutral'}])
def test_strict_mapping_rejects_ambiguous(mapping):
    with pytest.raises(ValueError):label_mapping(mapping)

def test_strict_mapping_preserves_semantics():
    assert label_mapping({'2':'ENTAILMENT','0':'contradiction','1':'neutral'})=={2:'entailment',0:'contradiction',1:'neutral'}

def test_revision_required():
    with pytest.raises(ValueError):StrictNLI('not-a-model','main')

def test_genuine_nli_missing_dependencies_fail_closed():
    if importlib.util.find_spec('torch') and importlib.util.find_spec('transformers'):
        pytest.skip('Dependency absence is not present; no model download permitted in this test')
    with pytest.raises(ImportError):StrictNLI('facebook/bart-large-mnli','0'*40)

def test_original_hf_wrapper_silent_mock_is_identifiable():
    from factsculpt.nli.models_hf import HuggingFaceNLIClassifier
    if importlib.util.find_spec('transformers'):pytest.skip('This regression expects missing transformers')
    result=HuggingFaceNLIClassifier('unavailable-model').predict('A','B')
    assert result.model_name=='mock-nli-model'

def test_heuristic_not_real_model():
    from factsculpt.experiments.baselines import NLIOnlyBaseline
    b=NLIOnlyBaseline()
    assert b._estimate_nli_scores('a b c d','a b c d')==(.85,.10,.05)

def test_rule_taxonomy_precedence():
    from factsculpt.features.models import EvidenceDeviationFeatures
    from factsculpt.classifier.rules import ResearchRuleBasedClassifier
    f=EvidenceDeviationFeatures(generated_claim_id='g',entailment_score=.1,neutral_score=.1,contradiction_score=.8,shift_vector={'role':1,'scope':-1},is_unsupported_addition=True)
    assert ResearchRuleBasedClassifier().classify(f).classification_code.value=='C4'

def test_many_to_one_not_aggregated_by_main_pipeline():
    from factsculpt.models import AtomicClaim
    from factsculpt.alignment.aligner import EmbeddingClaimAligner
    from factsculpt.alignment.embeddings import MockEmbeddingGenerator
    a=EmbeddingClaimAligner(MockEmbeddingGenerator()).align([AtomicClaim(claim_id='a',text='I develop system'),AtomicClaim(claim_id='b',text='I develop system')],[AtomicClaim(claim_id='g',text='I develop system')])
    assert len(a.alignments[0].source_claim_ids)==2
    # Source evidence: no claim aggregation read in orchestrator.
    text=(W/'audit_workspace/FactSculpt/factsculpt/application/pipeline.py').read_text()
    assert 'align.source_claim_id' in text and 'align.source_claim_ids' not in text

def test_regenerated_counts_and_separation():
    report=json.loads((H/'regenerated_dataset_audit.json').read_text())
    assert report['splits']['train']['count']==2520
    assert report['splits']['minimal_pairs']['count']==1260
    assert all(o['shared_cluster_ids']==0 and o['shared_exact_sources']==0 for o in report['overlap'].values())

def test_character_5grams_are_shared():
    report=json.loads((H/'regenerated_dataset_audit.json').read_text())
    assert all(o['shared_character_5grams']>0 for o in report['overlap'].values())
