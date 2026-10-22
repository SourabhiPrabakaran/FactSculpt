# FactSculpt final manuscript review

Review date: 15 October 2026. The corrected editable manuscript is `FactSculpt_IEEE_Conference_Paper_Final_Review.docx` in the project root. This review continues the completed reproducibility audit; it does not replace that audit or treat diagnostic labels as human ground truth.

## Decision

The document is ready for final author review as an evidence-qualified prototype and diagnostic study. **It is not cleared for submission as a validated empirical research paper.** Essential evidence for the central six-facet contribution and repair quality is still missing. The user confirmed that independent human annotators are not available now; this is an explicit blocker, not an experiment completed by generated judgments. A prototype, demonstration, or systems track may be a more appropriate eventual target, subject to its actual call and evaluation expectations. No acceptance prediction is made.

## 1. Revision report

The final document preserves the four validated figure binaries, seven tables, five numbered native Word equations, and 19 references. Only `word/document.xml` changed relative to the retained revised manuscript. The revised input and all 61 checked original source/documentation files remain unchanged. The final render has eight pages; all eight were visually inspected for clipping, overlaps, equation visibility, figure readability, and reference flow. Duplicate result prose was removed while retaining the protocol and numerical results; no smaller body font or forced page target was used.

Substantive corrections:

- Distinguished source claim `u` from the scope coordinate `sc` in equations, definitions, and Table II.
- Added two executed scalar controls to Table V, with their post hoc, uncalibrated status and differing decision coverage disclosed. Revised the abstract, introduction, and conclusion: the current transfer experiment does not establish an advantage of vector decisions.
- Added mechanical repair execution results and explicitly withheld claims about fidelity, fluency, residual exaggeration, or repair quality.
- Added a reproducibility appendix with environment, model/data revisions, execution distinctions, and replay guidance. Exact executable commands are in [README_REPRODUCIBILITY.md](README_REPRODUCIBILITY.md).
- Corrected the WiCE author attribution to J. Diego Rodriguez and added its publisher DOI. Checked citation-to-reference consistency for all 19 entries.
- Retained author/affiliation placeholders. These require the actual authors; they must not be invented.

Before finalization, the material review risks were ambiguous source/scope notation, interpretation of transfer performance as full-system validation, absence of a scalar control, unsupported repair-quality interpretation, incomplete predecessor recovery, and unresolved venue-template certification. The first four were corrected or explicitly qualified. Predecessor and venue certification limitations remain disclosed below.

## 2. Claims and contribution evidence

The complete 14-row adjudication is [claim_status.csv](claim_status.csv). Its principal conclusions are:

| Proposed claim | Review outcome | Required evidence or qualification |
|---|---|---|
| Six signed facets, ordinal scaling, research rules, and repair orchestration are implemented | Implementation verified; scientific validity unestablished | Source-backed mechanism description is defensible; independent facet labels and utility evaluation are needed |
| FactSculpt introduces a new ordinal probability model | Reject novelty claim | Bradley–Terry comparison and tanh transformation are established techniques; hand-authored scales and their integration are engineering choices |
| The six-facet combination provides better decisions | Not supported by current transfer results | Scalar controls exceed corresponding adapter point estimates; six-facet construct validity, mixed-case decisions, and explanation utility require independent testing |
| 0.3612 Macro-F1 is full-system accuracy | Reject wording | It is an ordinal, whole-conclusion regex transfer adapter on causal-relation labels; extraction, alignment, and repair are not jointly validated |
| Repair executes on the real test pairs | Verified mechanical result | 563 completed, 32 changed; this supplies no independent quality or semantic fidelity estimate |
| The historical README results are reproduced | Unresolved; excluded | Original datasets/full hashes, checkpoints, predictions, and protocol are still needed |
| NLI is generally unsuitable | Reject generalization | The measured result concerns one pinned checkpoint, score, and task only |

The defensible contribution is a transparent prototype combining interpretable signed facets, ordinal term comparisons, explicit rules, and bounded repair, accompanied by reproducibility and failure diagnostics. This is a combination and engineering contribution, not demonstrated new learning theory or established state-of-the-art performance. Related work already addresses exaggeration detection, relation strength comparison, factual consistency, and fine-grained verification. Implementation differences alone do not establish novelty. The manuscript positions the richer representation as a hypothesis whose utility remains to be tested.

Primary implementation anchors are `FactSculpt/factsculpt/differencing/engine.py`, `scales/ordinal_scaler.py`, `classifier/rules.py`, `features/extraction.py`, `nli/analyzer.py`, `nli/models_hf.py`, and `repair/pipeline.py` (paths after the first share `FactSculpt/factsculpt/`). CLI, Streamlit, and repair use different paths; the manuscript does not equate them. The contribution mappings from the completed foundation remain the baseline; this review qualifies claims rather than redrawing supported components.

## 3. Equation verification

| Equation | Meaning and implementation anchor | Verification and limits | Render page |
|---|---|---|---|
| (1) Δ(u,g) in [-1,1]^6 | Signed differences for role, quantity, scope, certainty, information, numeric facets; differencing/engine.py and models.py | Source `u` and scope `sc` distinct; six coordinates and direction consistent | 2 |
| (2) P_a(y ≻ x) = σ(λ_a(y) − λ_a(x)) | Pairwise ordinal term scaling; scales/ordinal_scaler.py | Bradley–Terry form; established technique, not new probability theory | 3 |
| (3) δ_a(u,g) = tanh(λ_a(y) − λ_a(x)) | Bounded ordinal difference; differencing/engine.py | Direction, range, clipping, rounding, and missing/unknown behavior explained | 3 |
| (4) v = min(1, Σ w_a |δ_a|) | Magnitude-based severity; classifier/rules.py | Weights (.25,.15,.20,.15,.15,.10), active threshold .05 and C4 override .85 disclosed; severity is not signed class direction | 3 |
| (5) d(u,g) = p_ent(g,u) − p_ent(u,g) | Separate genuine-NLI experiment harness | Reverse-minus-forward score and entailment index checked; not substituted for lexical pseudo-NLI | 5 |

The index set is A={r,q,sc,c,i,n}; all symbols are defined. Formulas are conceptual summaries of the identified research path, not claims that every interface executes identical operations. All five equations are editable native Word mathematics. Their numbering, citations, and visible layout passed final checks.

## 4. References and literature comparison

The 19-row [reference_verification.csv](reference_verification.csv) records each primary URL, metadata check, relevance, and limitation. Fifteen ACL publisher BibTeX records were fetched anew and compared. FAVA and RIGOURATE were checked against primary arXiv records; RIGOURATE remains a 2026 preprint, not an asserted peer-reviewed publication. Bradley–Terry metadata was checked against the publisher record/index; full text was not available. The dataset repository was verified as a versioned repository, not a journal publication. All 19 entries are cited in the manuscript. Access failures are retained in `primary_source_checks.json` rather than concealed.

| Closest literature family | Relationship to FactSculpt | Consequence for claims |
|---|---|---|
| Scientific exaggeration detection, including [Wright and Augenstein's dataset/repository](https://github.com/copenlu/scientific-exaggeration-detection) and [EACL 2021 relation-strength approach](https://aclanthology.org/2021.eacl-main.289/) | Direct task predecessors; relation extraction and strength comparison predate this project | Require a matched predecessor implementation before comparative superiority claims |
| Fine-grained consistency and factuality methods, including [WiCE](https://aclanthology.org/2023.emnlp-main.470/) and [FAVA](https://arxiv.org/abs/2401.06855v4) | Establish decomposed verification and error analysis | Six axes need independent construct/annotation evidence; finer granularity alone is insufficient novelty |
| Directional entailment and factual consistency methods in the verified reference list | Support an NLI diagnostic and comparison design | One near-chance checkpoint result cannot reject NLI as a method family |
| [Bradley–Terry](https://doi.org/10.1093/biomet/39.3-4.324) | Existing ordinal pairwise model | Cite the foundation and distinguish scale engineering from methodological invention |

The EACL predecessor short link was recovered to `jasabanta1992/Exaggeration_Identification`, pinned at `4dc566b813879867d9570fdf591704a2358ba691`. Its inspected inventory contains datasets, sequence-labeling data and LSTM-CRF modifications, but no identified complete BERT-SL checkpoint/compatible inference package. Code is therefore partially recovered, not globally unavailable. Its statement/pair split differs from the present 563-pair test set. The scalar controls below are not reproductions of this predecessor.

## 5. Executed experiments and reproducibility

New execution used `audit_workspace/final_review/FactSculpt`, a separate copy whose 61 source/documentation hashes matched the original. External API key variables were cleared and live API inference disabled. All 1,126 newly computed facet vectors matched the earlier saved vectors. Independent scripts recomputed the metrics below from saved outputs.

| Method on the same 563 released real pairs | Macro-F1 | Accuracy | Coverage |
|---|---:|---:|---:|
| Majority | .2533 | .6128 | 1.0000 |
| Regex hand-coded vector adapter | .2930 | .4796 | .9734 |
| Regex seed-ordinal vector adapter | .3612 | .4707 | .9485 |
| New scalar hand-coded control | .3077 | .5400 | 1.0000 |
| New scalar ordinal control | .3724 | .4920 | 1.0000 |

Scalar controls sum signed active components using existing severity weights, then classify at ±.05. They were chosen after prior test results were known; no tuning search, development-set calibration, uncertainty interval, or significance test supports them. Their decision policy differs from the mixed/abstaining vector adapter. These are exploratory decoder controls, not a clean proof that a scalar representation is superior. They do, however, prevent a claim that the current experiment demonstrates vector-decision benefit.

The original repair pipeline completed 563 attempts without exceptions: 32 changed and 531 unchanged. Stops were 522 `already_safe`, 28 `verified_safe`, and 13 `max_iterations_reached`. These internal names do not establish actual safety. Regex extraction and lexical pseudo-NLI were used; no result is represented as a genuine neural repair judgment. Source-copy would differ from all 563 original rewrites, but is only a prospective quality control, not a useful repair-quality score.

Fifteen isolated audit tests passed again (3.95 s). Their import path uses the earlier separate audit copy; they do not validate the complete deployed application. Earlier six offline diagnostic groups were inspected, not rerun in this final stage. The existing genuine pinned NLI predictions were independently checked, not regenerated: AUROC .508111 on 218 directional pairs; 142/426 strengthened synthetic variants met .65. Generator labels and repeated templates remain diagnostics, not real-world human validation. Previously reported unsupported README numbers remain excluded.

Reproducibility anchors: dataset commit `6e535ca60e1e5b09bb2b9b6119637073036660f0`; 100 train and 563 test pairs (96 down, 345 same, 122 exaggerated); genuine model `cross-encoder/nli-MiniLM2-L6-H768` revision `b95119ce93d3e065de6214e38cd4a97b0f2f2c6d`. All 26 recorded resource hashes and 61 original file hashes were rechecked. Exact commands, dependency/environment details, label order, thresholds, seeds, hashes, cache distinctions, and recovery instructions are in the reproducibility README. Saved hash-only repair outputs avoid redistributing raw licensed text. No observed released source-ID/exact-pair overlap excludes neither model pretraining contamination nor broader dependence.

## 6. Prioritized closure plan and remaining blockers

| Priority | Missing evidence | Exact closure requirement |
|---|---|---|
| P0 | Independent facet ground truth | Recruit at least two independent trained annotators; pilot/freeze guidelines, blind labels, adjudicate disagreements, retain provenance and per-facet agreement with uncertainty. User reports none available now. `ANNOTATION_GUIDELINES.md` and the 563-row blank form are prepared, not completed labels. This causal dataset is not itself a six-facet benchmark. |
| P0 | Central representation utility | On source-group-disjoint human-labeled cases, compare scalar/vector policies under matched coverage, include mixed changes and each axis, freeze development thresholds before held-out testing, report per-axis and joint errors with source-group bootstrap intervals. |
| P0 | Matched predecessor | Recover BERT-SL/strength-classifier checkpoints, tokenizer and configuration or faithfully retrain from identified author resources; validate the reconstruction on its own protocol, then freeze label mapping and run the same held-out pairs. Publish predictions and differences. |
| P0 if repair claim retained | Repair quality | Blinded independent source/original/edit judgments for fidelity, unsupported changes, residual exaggeration and fluency; compare unchanged, source-copy, and actual repair baselines. Report sample selection, failures and uncertainty. Internal verifier acceptance is insufficient. |
| P1 | Extraction/alignment performance | Gold spans and aligned claims, full-source examples and multi-claim failures; separate oracle-profile and actual-extraction runs. |
| P1 | Generalization and ablation | Real independently labeled domains; scalar, individual-facet, ordinal/hand-coded, NLI/no-NLI, extraction and repair ablations with frozen splits and matched decision policies. Measure latency/resources under recorded hardware. |
| P1 | Historical artifacts | Obtain original data bytes/full hashes, split IDs, checkpoints, dependency lock, predictions and evaluation command. Forty-eight investigated serialization variants do not establish a hash match. Otherwise retain historical numbers as unverifiable and excluded. |
| P1 | Backend reproducibility | Pin and record actual extractor/NLI/embedding backends per entry point; test cache provenance and fail-closed genuine inference. Existing CLI/Streamlit/repair defaults differ. |
| Submission gate | Authors and venue requirements | Replace placeholders; verify track, anonymity, rights, AI disclosure policy, PDF requirements and current template; render again after author changes. |

Suitable research questions are whether independent raters can reliably distinguish the six facets, whether their representation improves decisions or explanations under controlled baselines, and whether repair reduces exaggeration while preserving source-supported meaning. Until the P0 studies exist, these remain questions, not confirmed hypotheses. Planned tables should report annotation composition/agreement, matched real-data baselines, per-facet ablations, repair judgments and runtime. Evaluation figures should show per-class/facet errors and uncertainty or selective-risk curves only when actual measurements exist. No decorative improvement charts should be fabricated.

## 7. Manuscript argument and placement

The retained IEEE structure is: Introduction (precise problem and qualified prototype contributions); Related Work (closest exaggeration methods, verification, established ordinal modeling); Methodology (actual entry point, profiles, differences, rules, NLI and repair boundaries); Experimental Setup (real transfer versus synthetic diagnostics, pins and baselines); Results and Discussion (negative controls, failure cases, no end-to-end generalization); Limitations; Conclusion; reproducibility appendix; References. Architecture figures explain implementation, not empirical effectiveness. Captions and surrounding text retain their implementation qualifications. Seven tables and five equations remain in place, including expanded Table V. Existing editable diagram sources remain under `paper_foundation/figures/`.

## 8. Conference and formatting check

The live [IEEE ICSC submission page](https://www.semanticcomputing.org/submission), checked 15 October 2026, specifies English PDF submissions through EasyChair, with eight pages for regular papers, four for concise/industry papers and two for position papers, including figures, tables and references. The current document meets the regular-paper length in this render; that does not establish sufficient research maturity. A four-page concise submission would require a separate substantive condensation. The [dates page](https://www.semanticcomputing.org/dates) lists the extended paper deadline as 3 November 2026, Pacific Time; recheck before submission. Semantic computing is a plausible scope fit, not an acceptance recommendation.

The official IEEE templates page was blocked to automated access, and the attempted official Letter Word download returned zero bytes. The author-authorized standard IEEE layout fallback was retained: Letter, two 3.5-inch columns with .25-inch gap, 10-point Times body, 24-point title, 8-point captions/tables/references, .75-inch top, 1-inch bottom and .625-inch side margins. **This is not official-template certification.** Reviewed venue pages do not settle anonymity or AI disclosure details. Copyright, registration, presentation and originality obligations must be verified by the authors against the final call.

## 9. Final checklist

- [x] Five visible native equations; distinct source/scope notation and symbol definitions.
- [x] Four unchanged figure binaries, seven tables, 19 cited references, three numbered contributions.
- [x] Real/synthetic, neural/heuristic, component/end-to-end and historical/new evidence distinguished.
- [x] New scalar and repair executions saved; independent numerical checks completed.
- [x] Original source and revised input preserved; resource/source hash checks passed.
- [x] Eight rendered pages visually reviewed; no observed clipping, blank pages or overlap.
- [x] Human annotation blocker explicit; blank forms not presented as completed labels.
- [ ] P0 construct-validity, matched-predecessor and contribution-utility experiments completed.
- [ ] Independent repair-quality evidence if repair effectiveness is claimed.
- [ ] Actual author names, affiliations, funding/conflicts and rights confirmed.
- [ ] Current track/template/anonymity/AI disclosure and PDF submission checks completed.
- [ ] Final author-edited Word/PDF rendered and checked again; no submission performed here.

## Integrity and package contents

Final DOCX SHA-256: `40a0d38170c5572f8eb26dbddf9f6456fae17d1d1ee86a81bb565eeab0671018`.

`final_validation.json` records structural, numerical and hash checks. `manuscript_changes.json` records changes. The support archive contains this report, claim/reference tables, guidelines, blank form, replay/verification scripts, metadata inventories, and small result/log files. It excludes QA renders, downloaded model weights, portable LibreOffice, raw dataset text and source-copy caches. It supplements the existing project; it is not a complete standalone public reproduction release.

**Final readiness:** a corrected editable manuscript and defensible prototype foundation are available. A strong full empirical submission still requires essential independent experiments. The missing evidence cannot be resolved by editorial polishing, synthetic diagnostics, or generated annotations.
