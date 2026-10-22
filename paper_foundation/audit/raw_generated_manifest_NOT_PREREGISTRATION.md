# FROZEN TEST SET MANIFEST & CRYPTOGRAPHIC SEAL

**Date of Freeze**: 2026-10-05
**Benchmark Name**: FactSculpt-Bench
**Primary Domain**: Multi-Domain (Domain A: Professional Statements, Domain B: Scientific Communication, Domain C: Product & News Claims)
**Random Seed**: 42

## Split Statistics & Checksums

| Split File | Pair Count | Cluster Count | SHA-256 Checksum | Split Status |
| :--- | :--- | :--- | :--- | :--- |
| `train.json` | 2520 | 840 | `df69a7848256a4a543958cdf993887e75c61c556d64d9fff9f2b7e4659a869a8` | Training Set |
| `val.json` | 540 | 180 | `171f54688513df06f0db5b938f1a46258223459a6eeaf24d3029dffd5e32ab29` | Validation & Tuning Set |
| `frozen_test.json` | 540 | 180 | `9bdf7c20408ae8f77a8754e2f2d7b370891a0fea4a68f993f84394bb0a757db3` | **FROZEN TEST SET (SEALED)** |
| `minimal_pairs.json` | 1260 | N/A | `cbff3beeb1e577e9dd1c7102d1171522e39ddf1e9eea23414967ab43ccc8be9a` | Minimal-Pair Counterfactual Benchmark |
| `hard_cases.json` | 10 | 10 | `e0f3a224b72b9cd4d01c50fdd8d4d16a2d3599d24bf3d72bcdd0b57d434ecbd4` | Hard-Cases Stress Benchmark |

## Cryptographic Freeze Seal
The file `frozen_test.json` has been hashed with SHA-256 (`9bdf7c20408ae8f77a8754e2f2d7b370891a0fea4a68f993f84394bb0a757db3`).
Automated regression tests verify this checksum prior to any test-set inference.

## Research Integrity Rules
1. `frozen_test.json` must **NEVER** be used for:
   - Prompt engineering, few-shot prompt selection, or prompt tuning.
   - Classification threshold selection or hyperparameter sweeps.
   - Learned ordinal scale calibration or feature weight fitting.
   - Model checkpoint selection or early stopping.
2. All tuning, threshold selection, and scale calibration must occur strictly on `train.json` and `val.json`.
3. Evaluations on `frozen_test.json` are executed **exactly once** for final publication-grade reporting.
