# FactSculpt reproducibility and evidence-recovery audit

Audit date: 15 October 2026. This extends the existing foundation review; it does not repeat the initial architecture analysis or draft a paper. Original implementation files were not edited. All experiments ran in a separate working copy under `audit_workspace/FactSculpt`.

**Subsequent evidence:** [The research-positioning stage](../research_positioning/README.md) later enabled genuine MiniLM NLI in a separate neural environment and executed a real-pair causal-strength transfer probe. Its outputs supersede the execution-blocker status for that model only. The failed commands below remain accurate records of this audit's earlier environment; historical scores and the central independent annotation gaps are still unresolved.

## Decision

**Do not proceed to a results-bearing IEEE conference paper using the README's empirical claims.** There is now sufficient evidence for a precise method description, a transparent synthetic diagnostic study and an implementation audit. There is still insufficient evidence for claims about real pretrained NLI failures, human-text generalization, historical GBDT performance, independent repair safety, or preregistered final-test significance.

The audit recovered reproducibility of synthetic generation and established new diagnostic results, but did not recover the historical experiment evidence. The distinction is essential: new measurements on a newly reconstructed split cannot certify a prior result, even when a number happens to match.

## 1. Recovery search and artifact disposition

Search records are in `discovery.json`. The search covered the complete current project and the members of `Downloads/FactSculpt_minimal.zip` and `Downloads/dist.zip`; targeted file-name searches also covered Downloads, Documents and Desktop. Generated audit outputs and common dependency directories were excluded from that external search. Common Hugging Face and torch cache paths, plus configured cache-path variables if present, were checked. This is a scoped search, not a claim that every disk, cloud account or remote repository has been inspected.

The original FactSculpt ZIP contains **61 files**, all matching the corresponding supplied workspace source hashes. It contains no extra dataset, test suite or saved result. The other ZIP is an unrelated browser extension, with no relevant evidence filenames. The scoped external search did not locate another FactSculpt implementation or the named missing research artifacts. No Git metadata or remote recovery source is present in this snapshot.

| Artifact | Finding | Recoverability and consequence |
|---|---|---|
| Train/validation/frozen-test JSON | Historical originals not located | Current builder regenerates 2,520/540/540 pairs and 840/180/180 source IDs with the documented class distributions; all three byte hashes differ from README prefixes |
| Minimal-pair JSON | Historical original not located | Current generator yields 1,260 records; full new hash begins with the README's `cbff3beeb1e5` prefix |
| Hard-case JSON | Historical original not located | Ten supplied curated case definitions regenerate; hash prefix matches `e0f3a224b72b`. No cluster-ID field establishes the claimed ten clusters |
| Original tests / pytest config | Absent in scoped files and original ZIP | README's 233 tests cannot be recovered from implementation alone; new audit tests are explicitly separate |
| Original prediction/evaluation JSONs and logs | Not located | Historical scores, CIs, p-values and SBR cannot be independently recomputed |
| Learned-model checkpoints | Not located | New deterministic models can be fitted to generated labels; this does not recover old fitted models |
| `run_final_test`, leakage and table-generation scripts | Referenced entry points absent | Historical one-command commands fail or reference nonexistent paths |
| Preregistration/freeze manifest/datasheet/annotation files | Historical versions not located | Original chronology, annotation provenance and one-time test use cannot be established |
| Model weights | No files found in checked common caches or supplied archives | Genuine NLI and dense-embedding inference remain unavailable locally |
| Dependency/environment specification | Original minimum-version requirements present; no historical lockfile | New audit dependencies installed into a workspace-only target; exact versions recorded separately |

Generated files preserve source behavior. The builder emits a manifest with a fixed historical date literal; that raw output is retained as `raw_generated_manifest_NOT_PREREGISTRATION.md`. The working copy's manifest is prefixed with an explicit warning, and `AUDIT_COPY_NOTICE.md` identifies all new split data as template-generated reconstruction. No historical freeze or human annotation is inferred from this text.

### Reconstructed data checks

| Split | Records | Distinct source texts | Source IDs | C1 / C2 / C3 / C4 / C5 |
|---|---:|---:|---:|---|
| Train | 2,520 | 840 | 840 | 840 / 264 / 840 / 298 / 278 |
| Validation | 540 | 180 | 180 | 180 / 60 / 180 / 63 / 57 |
| Reconstructed test | 540 | 180 | 180 | 180 / 56 / 180 / 65 / 59 |
| Minimal pairs | 1,260 | 1,260 | Not supplied | 408 / 426 / 426 / 0 / 0 |
| Hard cases | 10 | 10 | Not supplied | Stored under `gold_class`; no independent annotation evidence |

All main splits have the documented 50/25/25% professional/scientific/product distribution. Source IDs and exact source strings do not overlap across these reconstructed splits. Their source corpora do share **2,548 train–validation, 2,520 train–test and 2,461 validation–test distinct lowercased character 5-grams**. This contradicts the literal zero-shared-5-grams claim for the reconstructed data. Shared short n-grams are not, by themselves, evidence of harmful near-duplicate leakage: that requires a defined similarity criterion and pair-level audit. Do not replace one exaggerated leakage claim with another.

`regenerated_dataset_audit.json` records full hashes, class/domain counts and overlap samples. Main-split hashes also remain different after LF normalization, so a simple line-ending explanation did not resolve them. Matching truncated hash prefixes for the auxiliary sets provides useful regeneration evidence; it does not recover historical files or validate their labels scientifically.

## 2. Numerical results and conflict resolution

`metric_verification.csv` and `METRIC_VERIFICATION.md` provide **269 entries** covering historical numerical table cells/prose, illustrative UI constants, and newly computed diagnostic metrics and per-class recall. Reported intervals and p-values are preserved with their source cell rather than silently discarded.

Four statuses are defined: verified and reproducible; supported by an artifact but not independently reproduced; unverified because evidence is missing; contradicted by other evidence. No historical model result qualified for the artifact-supported-but-not-reproduced category, because no historical prediction/run artifact was recovered. Matching new counts and auxiliary checksum prefixes have an explicitly reconstruction-only qualification.

| Disputed claim | Evidence and disposition |
|---|---|
| Headline end-to-end Macro-F1 .3095 versus GBDT .7230 | Both documented; no model/run lineage establishes whether they are different conditions. Flagged as incompatible documentation; neither selected, averaged or replaced |
| Headline oracle Macro-F1 .7498 versus GBDT .9543 | Same unresolved condition/lineage problem |
| NLI .1968, SummaC .2148 and associated p-values | No original predictions, genuine comparator outputs or significance runner recovered |
| NLI strengthening blindness 92.8–100% | Available lexical pseudo-NLI code cannot evidence pretrained-model failure rates |
| 100% counterfactual isolation | Not independently reproduced; current automated-profile minimal-pair diagnostic has errors. This is not a direct refutation of a distinct historical oracle experiment |
| Repair 88% edited, .7810 preservation, 2%/16% residual error | Historical outputs absent; alleged NLI judge in current evaluator is lexical, and preservation is source-token Jaccard |
| 233 tests passed | Original tests absent; new audit tests do not authenticate this count |
| Bootstrap 10,000, 95% CIs, once-only preregistered test | No original resampling outputs, run chronology or preregistration artifact; not reproduced |
| Static HTML: human Cohen's kappa .7080, repair preservation 84.2%, residual error 0% | These are markup literals; no annotator ratings or measurements support them. The human-agreement wording also conflicts with README's awaiting-human-evidence notice |
| Static HTML: +52.6% versus NLI | Based on displayed .7230 and README .1968, the difference is 52.62 percentage points; relative improvement would be a different quantity. Neither base measurement is verified |

The newly executed majority baseline reproduces .1000 Macro-F1 and .3333 accuracy on the reconstruction, but this confirms a mathematical baseline under the new class distribution, not the identity of an old run. The complete registry makes this distinction explicit.

## 3. NLI implementation audit

| Path | Actual behavior | Interpretation / risk |
|---|---|---|
| `nli/models_hf.py:HuggingFaceNLIClassifier` | Code genuinely tokenizes a premise/hypothesis, runs `AutoModelForSequenceClassification` with torch and applies softmax when weights/dependencies are available | A valid model-inference implementation path exists, but it was not executable here; load/inference exceptions silently return a mock |
| `MockNLIClassifier` | Constant neutral-dominant distribution or test-specified outputs | Test utility, not learned NLI; model name is `mock-nli-model` |
| Streamlit detection factory | Configures BART-large-MNLI; main pipeline invokes NLI on the selected aligned pair | Configured name is not proof of successful model execution; UI does not establish backend provenance and displays fixed empirical diagnostic prose |
| Default application pipeline | Configures MiniLM cross-encoder wrapper lazily | Different configuration from Streamlit; mock extraction and legacy taxonomy remain other defaults |
| Aligner optional reranking | Genuine model predictions only if a real NLI object is injected | Not wired by Streamlit factory; no evidence of active reranking in the documented app path |
| `NLIOnlyBaseline` | Token overlap and new-token count select fixed probability triples | Lexical pseudo-NLI; its support scores do not measure pretrained NLI behavior |
| `features/extraction.py` | Jaccard/new-token rules supply NLI probabilities for learned/rule experiments | Separate feature path, including oracle gold shifts by default; no actual cross-encoder scores |
| `app/detect.py` | Default lexical baseline; optional HF wrapper; fixed similarity .85 | Successful demo CLI execution is not a successful pretrained NLI experiment; backend metadata is not exposed in output |
| `repair/pipeline.py:_detect` | Entailment = 1 − differencer severity; neutral = severity; contradiction = 0 | Deterministic pseudo-NLI derived from the same evidence attributes being verified |
| `repair/evaluator.py` “NLI judge” | Uses `NLIOnlyBaseline`, not a cross-encoder | Describing this as independent pretrained-model verification changes the meaning of the experiment |
| External published baselines | Availability stubs for named packages | “READY” or package presence does not constitute an executed comparator |

Silent fallback is experimentally material. On absent dependencies, an injected original wrapper returned `mock-nli-model`, verified by a new regression test. Fixed scores and lexical thresholds can create directional-blindness behavior by construction; they cannot support general statements about the failure rate of actual NLI models. NLI has three relation labels, whereas FactSculpt has five evidential labels, so an arbitrary conversion can also confound comparison.

### Separate correction and genuine-inference harness

`strict_nli.py` implements a **fail-closed** adapter outside the original source. It requires an immutable model commit, uses only exact semantic label names, records model/revision/backend and allows load/inference errors to propagate. It does not fall back to rules or a mock. `run_genuine_nli.py` preserves raw three-way outputs and computes SBR/directional sensitivity relative to supplied C2/C3 generator classes; it deliberately does not invent a five-class mapping. It writes a completed prediction file only after every example succeeds.

Fifteen audit tests cover metrics, absent-class denominators, semantic label mapping, revision validation, dependency failure, original mock fallback, heuristic scores, rule precedence, source alignment behavior and reconstructed-data checks. These tests validate safeguards and mechanics, **not the adapter's real neural predictions**, which require absent dependencies and weights.

The official model repository currently identifies BART-large-MNLI revision `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`; this was resolved from [Hugging Face repository metadata](https://huggingface.co/api/models/facebook/bart-large-mnli). A pinned local-only invocation was attempted and failed at `import torch`; no genuine prediction artifact was emitted. Torch, transformers, sentence-transformers and the configured weights are not present in the audited environment/caches. Model loading options for local-only operation and immutable revisions are documented in the [Transformers loading API](https://huggingface.co/docs/transformers/v4.52.2/main_classes/model).

**Feasible next experiment:** install CPU-compatible torch, transformers and sentence-transformers into a pinned research environment; fetch the chosen exact model/tokenizer revisions and record hashes/licenses; run this fail-closed harness; pair it with regex-attribute and genuine-embedding full-pipeline configurations on the same annotated splits; save per-example raw scores. Freeze support thresholds on validation data before evaluating. A real [BART MNLI model](https://huggingface.co/facebook/bart-large-mnli) or the project's configured MiniLM cross-encoder is an appropriate NLI comparator. An actual [SummaC implementation](https://aclanthology.org/2022.tacl-1.10/) can address document-level granularity; importing its package is insufficient. Define a common support task for these comparators, and evaluate the five-way task only for systems with an explicitly justified mapping or classifier.

## 4. Execution and testing

Initial dependency installation failed with a sandbox DNS error. A permission-approved retry downloaded audit-only packages into `audit_workspace/deps`; no global project environment or original source was replaced. Final versions: Python 3.12.14, Pydantic 2.13.5, NumPy 2.5.4, SciPy 1.18.1, scikit-learn 1.9.1 and pytest 9.1.1. `requirements-audit.lock.txt` records the full package set used by these audit commands. This is a new audit lock, not a recovered historical environment.

| Executed check | Outcome | Scope |
|---|---|---|
| Original classifier import before installation | Failed: missing sklearn | Confirms initial blocker |
| Normal classifier import after installation | Passed without initializer bypass | Import capability only |
| Source generator | Passed; reconstructed all five JSON outputs | Synthetic regeneration, not historical recovery |
| New `test_audit.py` | **15 passed** | New implementation/metric checks, not original 233 tests |
| Existing foundation offline checks after install | Six groups passed; normal classifier import succeeded | Injected mock/regex pipeline and repair diagnostics |
| Demo detection CLI in working copy | Passed; C3, severity .4; neutral lexical pseudo-NLI | One illustrative offline pair |
| Repair CLI in working copy | Passed mechanically; one edit and internal `verified_safe` | Returned “I assisted with developing an system.”, demonstrating that internal safety does not guarantee grammar |
| Original pytest command after install | Failed, exit 4: tests directory missing | Original suite cannot be run |
| Original final-test module | Failed: module absent | Historical experiment command unreproducible |
| Genuine pinned NLI harness | Failed, exit 1: torch absent | No neural inference or fallback scores produced |
| Streamlit application, live LLM extraction, neural embedding path | Not launched/evaluated | Necessary UI/model dependencies and external execution evidence unavailable |

All command arguments, working directories, exit codes, stdout and stderr are recorded under `logs/` and summarized in `execution_manifest.json`. Offline execution sets HF offline flags and removes supported LLM API key variables from child-process environments, without reading or printing their values. The CLI wrote its profile cache only in the working copy.

### Minimum environment distinctions

- Data-generation audit: Python 3.12 and Pydantic v2; NumPy is needed by baseline modules.
- Normal rule/learned imports in the unmodified project: Pydantic, NumPy and scikit-learn with its SciPy/transitive requirements, because `classifier/__init__.py` eagerly imports learned classes.
- New audit checks and diagnostic evaluation: the exact audit lock plus bundled Python; no API keys, neural weights, pandas or Streamlit are required for these commands.
- Genuine main application: original requirements plus actual embedding/NLI model files; Streamlit and pandas for the UI; configured API key only for live LLM extraction. An installed requirement does not prove an executed model backend.

## 5. Newly executed experiments

These are **new deterministic diagnostics**, using labels assigned by the existing source generator. They do not introduce invented human labels or pretend that templates were live LLM outputs. Main data are source-template disjoint by construction and source-ID/exact-string disjoint by the observed checks; the original “in-distribution” and “template-disjoint” result tables cannot be reconstructed as two historical protocols from the available files.

**Protocol:** training uses reconstructed train records; supplied baseline threshold grids select on reconstructed validation records; evaluation is on reconstructed test records. LogReg/GBDT use the existing fixed random seed 42 and source hyperparameters. Regex conditions use `RegexEvidenceProfileExtractor` explicitly, avoiding cached/live profile ambiguity. Oracle conditions use generator-provided shift annotations and are declared upper-input conditions. All pair-feature runs retain the implementation's lexical pseudo-NLI; they are not the Streamlit embedding/NLI pipeline. No test-driven tuning or CI/p-value estimation was added. Calibration attempts fell back to uncalibrated model probabilities in this current scikit-learn environment; per-example files record `calibrated=false`.

Every condition saves JSONL predictions, reopens them and computes confusion matrices, class recall, accuracy and Macro-F1 with `independent_metrics.py`. For the four built-in baselines, independently recomputed metrics agree with the project metrics within their documented rounding. Learned-system SBR is left undefined because this experiment does not specify an independent support score; maximum class confidence is not substituted for support.

| New reconstructed-test condition | Macro-F1 (C1-C5) | Accuracy |
|---|---:|---:|
| Majority | .100000 | .333333 |
| Lexical Jaccard | .208369 | .446296 |
| Bag-of-words cosine | .263313 | .546296 |
| Lexical pseudo-NLI | .172719 | .401852 |
| Research rules, regex profiles | .264061 | .500000 |
| LogReg, regex profiles | .429111 | .655556 |
| GBDT, regex profiles | .551991 | .629630 |
| Research rules, generator oracle shifts | .758471 | .851852 |
| LogReg, generator oracle shifts | .762136 | .855556 |
| GBDT, generator oracle shifts | .863727 | .872222 |

These values establish only reproducibility of the new diagnostic conditions. They show an extraction/oracle-input gap and class confusions, but do not establish improvement over genuine pretrained comparators or generalization to human text. Even oracle shifts are closely related to generator class construction; high oracle scores may reflect that relationship.

### Controlled ordinal-scale comparison

The same 1,260 generated minimal pairs were regex-profiled once per condition. The actual differencer was rerun with handcoded rules versus the seed-fitted scaler; a declared neutral placeholder isolated attribute behavior without claiming any NLI accuracy. This is a genuine component replacement, unlike the source's simulated “many-to-one off” feature attenuation.

| New minimal-pair condition | Accuracy | Macro-F1 over observed C1/C2/C3 |
|---|---:|---:|
| Handcoded differencing | .901587 | .900879 |
| Seed-fitted ordinal differencing | .845238 | .848313 |

The five-class Macro-F1 is also saved (.540528/.508988), but absent C4/C5 contribute zero by that convention. The three-class average above is the useful denominator for this subset. These values do not reproduce the README's 100% counterfactual claim. Failures include unknown qualifier terms and numeric-bound handling; error counts and examples appear in `error_analysis.json`, and per-attribute counts are saved in the summary. This is one synthetic test, without uncertainty estimates or independent labels; it does not establish universal scale inferiority.

### Repair error inspection

All ten supplied hard-case definitions were exercised with regex extraction and the existing repair mechanics; outputs are saved under `hard_case_repair_internal_only.json`. No independent repair-quality metric is reported. The CLI's grammatical failure and remaining semantic blind spots justify blinded human review, explicit unsupported-addition checks, source-specific substitutions and a no-change exit before repair is presented as reliable.

## 6. Contribution-to-evidence conclusions

The complete mapping is in `contribution_evidence.csv`.

| Proposed contribution | Verified support | Remaining claim boundary |
|---|---|---|
| Five-way evidence-strength representation | Source definitions, rule precedence tests, saved synthetic confusion matrices | Taxonomy novelty, contradiction-only C5 exception and human construct validity unresolved |
| Interpretable detector | Normal imports; offline demo CLI; injected per-claim checks; reconstructed regex/rule/learned predictions | No fully evaluated neural Streamlit configuration, independent human dataset or historical learned-model result |
| Seed-fitted ordinal shifts | Fitting/unknown-term tests and controlled comparison with handcoded differencing | No observed advantage on this synthetic comparison; human preference validation and unknown-vocabulary behavior needed |
| Synthetic diagnostic benchmark | Documented sizes/distributions regenerated; auxiliary checksum prefixes matched; source separation checked | Main historical byte identity differs; template labels lack independent validation; literal zero-n-gram claim fails |
| Attribute-targeted repair | Loop/stop behavior, demo CLI, saved hard-case edits | Internal verification and grammar failures; no independent residual-inflation or preservation measurement |
| Pretrained strengthening blindness | Genuine model-inference code path and fail-closed replacement harness exist | No actual pretrained outputs; no defensible empirical blindness rate yet |

## 7. Minimum work before an IEEE submission

1. **Freeze the actual evaluated system.** Select research taxonomy, inference configuration and immutable model revisions; record real backend and cache provenance; prohibit silent fallback in experiments. Resolve C5 contradiction policy and use all claims in any document-level metric.
2. **Recover or replace historical evidence transparently.** Obtain original data/predictions/configuration if historical scores are retained. Otherwise retire those scores and preregistration language, archive new versioned datasets and report a newly executed protocol.
3. **Obtain independent labels.** Validate source-derived labels, especially C2/C4/C5 and numeric/causal cases; collect a genuinely human-written/annotated held-out set, annotation guide, independent annotators, agreement and adjudication. Do not relabel generator output as human or live-LLM data.
4. **Run genuine comparators.** Use pinned NLI and embedding weights, actual published baseline implementations and a common support task. Save raw outputs and justified class mappings. Reassess strengthening blindness only after these runs.
5. **Run real ablations and uncertainty analysis.** Compare regex/live/oracle extraction; handcoded/seed scales; full-feature versus removed features; genuinely integrated multi-source support if implemented. Cluster-bootstrap confidence intervals and paired comparisons must use shared source groups and frozen validation choices.
6. **Evaluate repair independently or reduce paper scope.** Complete actual prompt/regeneration/best-of-N baselines, blinded factuality/preservation/fluency evaluation, representative sampling, grammar and no-change checks. Omit empirical repair claims if this is not completed.

The four existing diagrams remain source-accurate and unchanged: they already distinguish configured detection, data stores, conditional model execution and the separate repair detector. The added strict adapter is an audit tool, not an integrated application component, so it is not inserted into those figures. IEEE captions and placements remain valid. The prior report now links to this audit as the authoritative update on artifact availability and execution.

## 8. Deliverables

- `REPRODUCIBILITY_AUDIT.md`: findings, interpretation, readiness and minimum next work.
- `METRIC_VERIFICATION.md` / `metric_verification.csv`: documented and new metric registry.
- `results/diagnostic_results.md`, `diagnostic_summary.json`, JSONL predictions: newly verified numerical evidence.
- `results/error_analysis.json`, `hard_case_repair_internal_only.json`: error cases and internal repair traces.
- `discovery.json`, `regenerated_dataset_audit.json`, original/output hashes: recovery scope, dataset provenance and integrity.
- `logs/`, `execution_manifest.json`, `audit_tests.xml`: actual execution records.
- `strict_nli.py`, `run_genuine_nli.py`, `independent_metrics.py`, `test_audit.py`: separate correction, harness and tests.
- `REPRODUCE.md`, `requirements-audit.lock.txt`: commands and package versions.
- Updated main foundation report, source evidence map and `contribution_evidence.csv`; original figures preserved.

No complete paper is drafted at this stage.
