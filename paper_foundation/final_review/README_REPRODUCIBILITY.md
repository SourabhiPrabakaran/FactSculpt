# FactSculpt final review reproduction

Run from `<LOCAL_HOME>\Downloads\FactSculpt_minimal`. The supplied audit/research packages are the baseline; new controls do not overwrite their predictions. The source working copy is `audit_workspace/final_review/FactSculpt`, with hashes for all 61 original files. Raw released text, local caches and model binaries are not publication artifacts.

## Commands actually used for this review

```powershell
$factsPython = '<LOCAL_HOME>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $factsPython paper_foundation/final_review/run_controls.py
& $factsPython paper_foundation/final_review/verify_controls.py
& $factsPython paper_foundation/final_review/verify_final.py
```

The first command re-extracts 563 whole-conclusion pairs with regex profiles, recomputes both difference engines, checks all 1,126 vectors against saved originals, evaluates the scalar controls and executes repair on all 563 pairs. It clears the three supported API-key environment variables and blocks external inference calls. The repair cache belongs to the separate working copy; it contains regex fallback profiles under the wrapper's default requested identifier, not LLM outputs. The second command reopens predictions, independently recomputes control metrics, verifies output hashes and creates a blank annotation form. Its 563 identifiers are a narrow pilot frame, not a diverse six-facet benchmark or completed labels.

For a fresh run, use a new project checkout/workspace with these paths absent rather than mixing caches from different experiments. The scripts preserve original source; generated cache/data files live only in the working copy. Runtime: Python 3.12.14; audit imports use the existing `audit_workspace/deps` target, including Pydantic 2.13.5 and NumPy 2.5.4. The neural experiment additionally uses torch 2.14.1+cpu, transformers 4.57.6 and two CPU threads. The complete observed locks are in the earlier audit and research-positioning packages.

## Reconstruct the earlier genuine experiments on a clean machine

Use Python 3.12 and a fresh environment or the documented dedicated targets. Acquisition needs network access; inference is local and fail-closed.

```powershell
& $factsPython -m pip install --target audit_workspace/deps -r paper_foundation/audit/requirements-audit.lock.txt
& $factsPython -m pip install --target audit_workspace/neural_deps --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cpu -r paper_foundation/research_positioning/requirements-neural.lock.txt
& $factsPython paper_foundation/research_positioning/fetch_research_resources.py --model-files
& $factsPython paper_foundation/research_positioning/execute_probe.py
& $factsPython paper_foundation/research_positioning/validate_results.py
```

These latter inference commands were executed in the completed research-positioning stage, not rerun as new results in this final review. Saved-output numerical checks were performed again. Synthetic diagnostics additionally require the reconstructed data and harness described in `paper_foundation/audit/REPRODUCIBILITY_AUDIT.md`; they cannot recover the historical README files or chronology.

## Fixed provenance and protocol

- Author data repository: `copenlu/scientific-exaggeration-detection`, commit `6e535ca60e1e5b09bb2b9b6119637073036660f0`.
- Released training SHA-256: `ee5f42661e28d30271060047cdc7a284885ac6dc4e20cc6d780f21a76a56efd5`.
- Released test SHA-256: `41429cc76860e56b96791be8478c2eb831e19e5d605b529c626b5327f2ed7f0a`.
- Split sizes 100/563. Test labels 96 downplays, 345 same, 122 exaggerates. No shared released source IDs or exact pairs were observed in the completed checks; public pretraining contamination is not excluded.
- Genuine model: `cross-encoder/nli-MiniLM2-L6-H768`, revision `b95119ce93d3e065de6214e38cd4a97b0f2f2c6d`; exact semantic id2label mapping, local safetensors, 512-token limit, forward and reverse entailment. Reported real AUROC uses 122 exaggerates versus 96 downplays only.
- Research-rule active-component threshold: ±0.05. Default severity weights: role .25, qualifier .15, scope .20, certainty .15, impact .15, quantity .10. Ordinal seed pairs remain the hand-authored dictionary in `FactSculpt/factsculpt/scales/ordinal_scaler.py`; initialization 0, learning rate .1, 150 iterations, regularization .01, clipping ±20, four-decimal centering/output rounding.
- Original transfer uses an explicit neutral placeholder to isolate attribute logic, not a genuine model prediction. C1/C2/C3 map to same/downplays/exaggerates and C4/C5 abstain; abstentions are wrong for accuracy and false negatives for class F1.
- New scalar controls apply the fixed weights to signed components with absolute value > .05; score > .05 predicts exaggerates, < −.05 downplays, otherwise same. They were designed after earlier test results were known. No threshold search was performed; no preregistration, significance or representation-utility claim is implied.
- New repair uses original max-3-iteration, .15-severity and .05-positive-shift settings, regex fallback and pseudo-NLI. No independent human or validated automatic quality judge was available. Source copy is an execution/fidelity anchor that discards the rewrite objective, not an empirical quality label.

## Artifacts and blockers

New predictions, digests and summaries are in `paper_foundation/final_review/results/`. Earlier saved predictions, resource hashes, logs, locks and independent checks remain in `paper_foundation/research_positioning/` and `paper_foundation/audit/`. `primary_source_checks.json` records fresh retrieval results, including TLS/HTTP failures; `predecessor_inventory.json` pins the recovered code repository at `4dc566b813879867d9570fdf591704a2358ba691`.

Human facet/repair annotations were not supplied; no agreement or quality scores are manufactured. `ANNOTATION_GUIDELINES.md` and the blank form support prospective collection. The predecessor tree provides annotated splits and LSTM modifications, but no identified BERT-SL checkpoint or complete compatible inference pipeline. A fair reproduction requires recovery or documented reimplementation, compatible label mapping and a frozen matched protocol. Published predecessor performance cannot be substituted for executed predictions.

Historical reconstructed split hashes still differ from README prefixes; 48 tested serializations per main split did not resolve them. Recover original full files/hashes, producing source, configurations and predictions, or retire those old scores permanently. The observed resource hashes authenticate the new files only. Resolve dataset rights and make a versioned, appropriately anonymized public artifact deposit before claiming public reproducibility.
