# Historical README — unsupported claims retained for provenance

The following is historical project text, NOT the release documentation or verified results. Its performance numbers, test badges, preregistration and MIT license badge are not established by this package. Referenced historical artifacts were not recovered. See the root README and final review.

---

# FactSculpt: Closed-World Evidence-Strengthening & Exaggeration Detection

[![CI Tests](https://img.shields.io/badge/pytest-233%20passed-brightgreen.svg)]()
[![Dataset Freeze](https://img.shields.io/badge/SHA--256-9dd24d17...-blue.svg)](data/splits/FREEZE_MANIFEST.md)
[![Pre-Registration](https://img.shields.io/badge/PREREGISTRATION-Committed-purple.svg)](PREREGISTRATION.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

FactSculpt is a rigorous, publication-grade Natural Language Processing (NLP) research project. Its primary contribution is two-fold:
1. **A Diagnostic Benchmark**: Exposing that standard Natural Language Inference (NLI) and factual consistency evaluators suffer from severe **Strengthening Blindness (SBR $\ge 92.8\%$)** on **Support-Preserving Strengthening (SPS)** under closed-world evidence constraints.
2. **A Baseline Detector with Stated Generalization Limits**: An attribute-differencing system evaluated honestly under automated end-to-end extraction alongside an oracle gold-span upper bound.

### Generalization Spectrum & Honest Evaluation Summary
We state in-distribution, template-disjoint, and real-data numbers side by side:

| Benchmark Split | End-to-End Headline Macro-F1 (95% CI) | Headline Acc | Oracle Upper Bound Macro-F1 (95% CI) | Oracle Acc | Status & Generalization Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **In-Distribution Held-Out Test** ($N=540$) | **0.3095** [0.2779, 0.3399] | 39.3% | **0.7498** [0.7309, 0.7696] | 77.0% | Outperforms RoBERTa-MNLI (0.1968, $p=0.0002$) and SummaC-ZS (0.2148, $p=0.0001$). |
| **Template-Disjoint Test** ($N=540$) | **0.0815** [0.0645, 0.0982] | 13.0% | **0.8285** [0.8026, 0.8539] | 83.0% | Exposes dependency of automated NLP extraction on seen templates; oracle upper bound remains robust. |
| **Genuine Human-Labeled Test** | *Awaiting Human Data* | *--* | *--* | *--* | Real human annotation files required; fake labels strictly refused per Hard Rule #1. Pilot quarantined. |

> **Scoped Claims Notice**: Minority classes (**C2** weakened, **C4** unsupported addition, **C5** mixed) exhibit low end-to-end recall under automated extraction. Per research integrity rules, all claims regarding detector accuracy on C2, C4, and C5 on natural/real text are explicitly removed until genuine human-annotated data is acquired.

---

## 1. The Core Research Phenomenon: Support-Preserving Strengthening (SPS)

When Large Language Models (LLMs) rewrite text (e.g., polishing resumes, drafting scientific press releases, or formatting product claims), they systematically escalate claims:
- **Role/Agency**: Demoting collaboration into sole leadership (*"contributed to"* $\rightarrow$ *"spearheaded"*),
- **Qualifiers**: Adding promotional framing (*"a tool"* $\rightarrow$ *"an industry-leading, enterprise-grade architecture"*),
- **Scope**: Generalizing regional findings to universal claims (*"in our pilot cohort"* $\rightarrow$ *"across all demographics"*),
- **Certainty**: Converting epistemic hedging into absolute assertions (*"findings suggest"* $\rightarrow$ *"irrefutably proves"*),
- **Impact**: Inflating modest outcomes into transformative shifts (*"improved metrics"* $\rightarrow$ *"revolutionized workflows"*),
- **Quantity Bounds**: Shifting numeric ranges and lower bounds (*"up to 50%"* $\rightarrow$ *"over 50%"*).

### Entailment Asymmetry & Strengthening Blindness (SBR)
Standard Natural Language Inference (NLI) models operate under classical logical entailment: an exaggerated rewrite (e.g. hypothesis *"spearheaded"*) often preserves the predicate domain of the source evidence (premise *"contributed"*) without triggering an explicit contradiction. Under default premise-to-hypothesis scoring, standard NLI models judge strengthened rewrites as supported (**92.8% to 100.0% Strengthening Blindness Rate**). This does not indicate that NLI models are fundamentally defective at logical inference; rather, logical entailment is benevolent toward semantic strengthening, making it insufficient on its own for detecting evidence inflation.

---

## 2. Canonical Evidential Taxonomy (C1–C5)

Every claim in the generated text is classified into one of five mutually exclusive categories:

| Code | Canonical Name | Evidential Definition |
| :--- | :--- | :--- |
| **C1** | **UNCHANGED_FAITHFUL** | Meaning, evidence strength, modality, scope, and bounds are strictly preserved. |
| **C2** | **WEAKENED** | Evidential strength is attenuated (demoted role, restricted scope, lowered certainty). |
| **C3** | **STRENGTHENED** | Evidential strength is amplified in $\ge 1$ attribute without opposing weakening (SPS). |
| **C4** | **UNSUPPORTED_ADDITION** | Extrinsic claims or entities with zero basis in the source evidence. |
| **C5** | **MIXED** | Simultaneous strengthening in $\ge 1$ attribute and weakening in $\ge 1$ other attribute. |

---

## 3. Benchmark Architecture: FactSculpt-Bench

FactSculpt-Bench comprises **3,600 pairs across 1,200 unique source clusters** spanning 3 domains, strictly partitioned to prevent lexical or syntactic leakage:

| Split | Pairs Count | Source Clusters | Class Distribution (C1 / C2 / C3 / C4 / C5) | Domain Breakdown | SHA-256 Checksum |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | 2,520 | 840 | 840 / 264 / 840 / 298 / 278 | Professional (50%), Scientific (25%), Product (25%) | `06fbe863dd47...` |
| **Validation** | 540 | 180 | 180 / 60 / 180 / 63 / 57 | Professional (50%), Scientific (25%), Product (25%) | `feda90525667...` |
| **Held-Out Test** | 540 | 180 | 180 / 56 / 180 / 65 / 59 | Professional (50%), Scientific (25%), Product (25%) | **`9dd24d178534...` [SEALED]** |
| **Minimal-Pairs** | 1,260 | N/A | 408 (ctrl) / 426 (weaken) / 426 (strengthen) | Counterfactual single-attribute variations | `cbff3beeb1e5...` |
| **Hard-Cases** | 10 | 10 | Curated edge cases | Hedging, Negation, Multi-sentence, Bounds | `e0f3a224b72b...` |

---

## 4. Key Experimental Findings (Held-Out Test Split)

All results are produced by uncheated models evaluated once on `frozen_test.json` after pre-registration (`PREREGISTRATION.md`), with **10,000-sample bootstrap 95% confidence intervals**:

### Table 2: Primary Held-Out Test Evaluation
| System / Model | End-to-End Macro-F1 (95% CI) | End-to-End Acc | Oracle Macro-F1 (Gold Upper Bound) | Oracle Acc | SBR (%) | Dir-Sens |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FactSculpt GBDT** | **0.7230** [0.6776, 0.7637] | **0.7685** | **0.9543** [0.9341, 0.9723] | 0.9630 | 93.9% | +0.1543 |
| **FactSculpt LogReg** | 0.4117 [0.3663, 0.4542] | 0.6204 | 0.8268 [0.7973, 0.8563] | 0.8981 | 97.8% | +0.1690 |
| **FactSculpt Rules** | 0.3153 [0.2857, 0.3443] | 0.5611 | 0.7931 [0.7620, 0.8236] | 0.8722 | 99.4% | +0.1593 |
| **Length-Only Baseline** | 0.5117 [0.4802, 0.5401] | 0.5093 | -- | -- | 31.1% | +0.6353 |
| **Template-ID Baseline** | 0.1000 [0.0910, 0.1089] | 0.3333 | -- | -- | 100.0% | +0.0000 |
| **Vanilla NLI Baseline** | 0.1968 [0.1682, 0.2241] | 0.3833 | -- | -- | 92.8% | +0.0093 |
| **Lexical Overlap** | 0.1946 [0.1769, 0.2118] | 0.4241 | -- | -- | 63.3% | +0.0096 |
| **Embedding Cosine** | 0.1963 [0.1787, 0.2132] | 0.4093 | -- | -- | 47.2% | +0.0303 |
| **Majority Baseline** | 0.1000 [0.0910, 0.1089] | 0.3333 | -- | -- | 100.0% | +0.0000 |

*Strengthening Blindness Rate (SBR)*: The percentage of evidentially strengthened rewrites judged as "supported" by the model under evaluation. Due to entailment benevolence, standard NLI misses 92.8% to 99.4% of evidential strengthening shifts on held-out test data.

### Minimal-Pair Benchmark (1,260 Counterfactuals)
- **NLI Support Scores**: Entailment score assigns high support indiscriminately to strengthened (0.6833) and weakened (0.7167) edits, yielding near-zero directional sensitivity ($\Delta \text{Dir} = +0.0333$).
- **FactSculpt**: Establishes large directional separation ($\Delta \text{Dir} = +0.7500$), with the symbolic differencer achieving 100.0% counterfactual isolation across all 6 linguistic dimensions.

### Attribute-Targeted Minimal Repair
- **FactSculpt Targeted Repair (Evaluated Directly)**: Evaluated on held-out test split, actively rewriting 88.0% of inflated claims with 0.0% verbatim copies, achieving **0.7810** semantic preservation and reducing residual exaggeration to **2.0%** (Lexical Judge) and **16.0%** (NLI Judge) in **0.9** mean iterations.
- **External Generator Baselines (Prompting, Regeneration, Best-of-N)**: Honestly tracked as `PENDING_REAL_LLM_GENERATION` (awaiting live commercial API keys per Section 0 Rule 7).

---

## 5. One-Command Reproducibility

### 1. Verify Split Partitioning and Zero-Leakage
```bash
python scripts/check_leakage.py
```
*Validates that zero source documents, cluster IDs, or char 5-grams cross train/val/test splits.*

### 2. Validate Baseline Models on Validation Split
```bash
python scripts/run_baselines_val.py
```

### 3. Run Single Pre-Registered Final Test Evaluation
```bash
python -m factsculpt.experiments.run_final_test
```
*Verifies SHA-256 seal and runs official 10,000 bootstrap resample test evaluation.*

### 4. Execute Multi-Model Repair Study
```bash
python scripts/run_repair_study.py
```

### 5. Regenerate All Markdown and LaTeX Tables
```bash
python scripts/generate_paper_tables.py
```

### 6. Run Complete Regression Test Suite
```bash
python -m pytest tests/ -v
```

---

## 6. Project Layout

```
FactSculpt/
├── AUDIT.md                        # Formal reproduction of repo defects A1-A13
├── BLOCKERS.md                     # Documented dependencies (APIs, human annotators)
├── DATASHEET.md                    # Data provenance and licensing
├── DECISIONS.md                    # Canonical taxonomy & architecture decisions
├── PREREGISTRATION.md              # Pre-registered hypotheses (H1-H7) & evaluation protocol
├── MODEL_CARD.md                   # Model documentation and intended uses
├── RESPONSIBLE_NLP.md              # ACL Responsible NLP Research checklist
├── data/
│   └── splits/                     # Leakage-proof dataset partitions
│       ├── train.json              # 2,520 training pairs
│       ├── val.json                # 540 validation pairs
│       ├── frozen_test.json        # 540 held-out test pairs [SEALED]
│       ├── minimal_pairs.json      # 1,260 single-attribute pairs
│       ├── hard_cases.json         # 10 curated stress cases
│       └── FREEZE_MANIFEST.md      # Checksums & integrity manifest
├── factsculpt/
│   ├── taxonomy.py                 # Single source of truth for C1-C5
│   ├── classifier/                 # GBDT, LogReg, and Rule classifiers
│   ├── features/                   # Uncheated pair feature extraction
│   ├── repair/                     # Targeted evidence-grounded repair loop
│   └── experiments/                # Test runner and metric computations
├── paper/                          # Publication assets
│   ├── claims_to_evidence.md       # Exact claim-to-artifact mapping
│   ├── paper_outline.md            # ACL structural blueprint
│   ├── limitations.md              # Candid boundary analysis
│   └── *.tex                       # Auto-generated LaTeX tables
├── results/                        # Machine-readable evaluation JSONs and Markdown tables
├── scripts/                        # Verification, leakage audit, and table generators
└── tests/                          # 233 passing regression and integrity tests
```

---

## 7. Research Integrity & Non-Fabrication Standards

In strict compliance with empirical research standards:
1. **Zero Metric Fabrication**: Every metric reported in tables, figures, and docs is computed directly from saved model outputs.
2. **Audit & Quarantine**: All datasets are tracked with explicit provenance (`human | llm | system`). Preliminary pilot ratings are quarantined in `annotation/quarantine/` as an unverified pilot (`llm_or_unverified_pilot_*.csv`). All unverified claims of human verification, human-labeled real ground truth, and human seals have been expunged per research audit.
3. **Leakage Protection**: All splits are partitioned by source cluster; exact duplicates and near-duplicates across splits are audited and prohibited.
4. **Frozen Evaluation**: `frozen_test.json` was evaluated exactly once after pre-registration and hash verification.
