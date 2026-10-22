# Reproduce the new audit

Run from `<LOCAL_HOME>\Downloads\FactSculpt_minimal`. These commands reproduce NEW synthetic diagnostics, not the missing historical experiment. Use Python 3.12; the observed version was 3.12.14.

```powershell
$auditPython = '<LOCAL_HOME>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $auditPython -m pip install --target audit_workspace/deps -r paper_foundation/audit/requirements-audit.lock.txt
& $auditPython paper_foundation/audit/discover_and_rebuild.py
& $auditPython paper_foundation/audit/execute.py
& $auditPython paper_foundation/audit/build_metric_registry.py
& $auditPython paper_foundation/audit/finalize_artifacts.py
```

The observed installation requested `scikit-learn scipy pytest` with pip into that target; this lock captures the resolved environment, including Pydantic used from the bundled runtime. A sandbox DNS failure required an approved network retry. Full logs for experiment/test commands are in `logs/`. `execute.py` sets workspace dependency paths and offline flags for child processes and clears supported LLM key variables. No classifier initializer bypass is used after installation.

Expected intentional limitations in a complete audit run: original pytest directory is absent (exit 4); the real NLI harness fails because torch is absent (exit 1). These are logged outcomes, not successful application tests. The separate audit tests pass, synthetic experiments complete, and the offline CLI paths work. `execute.py --only NAME` reruns a single named command without repeating experiments.

The discovery script overwrites only generated reconstruction data in the audit copy, never the original project. It also attempts absent historical runner commands to preserve their failures. `finalize_artifacts.py` labels the newly generated freeze manifest as nonhistorical. If rerunning in another environment, the observed package versions/model outputs may change; preserve the new logs rather than claiming a match without checking hashes and predictions.

## Genuine NLI plan (not completed)

Create a separate research environment with compatible CPU torch and transformers. Resolve and archive exact package versions and actual model weights before benchmarking. The audited BART revision, obtained from official repository metadata, is `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`.

The existing harness defaults to local-only loading and errors on missing dependencies/weights or ambiguous class labels. A representative command, once the correct environment and weights exist, is:

```powershell
& $auditPython paper_foundation/audit/run_genuine_nli.py --data audit_workspace/FactSculpt/data/splits/minimal_pairs.json --output paper_foundation/audit/results/genuine_nli_predictions.jsonl --model facebook/bart-large-mnli --revision d7645e127eaf1aefc7862fd59a17a5aa8558b8ce
```

Use `--allow-download` only when intentionally fetching the pinned revision in an environment with network access. Offline environment flags must be unset for that fetch. The harness records model/revision/backend and source/prediction hashes; no mock replacement is allowed. It outputs three-way NLI probabilities and support diagnostics; it does not invent FactSculpt five-way predictions.

For a full neural/Streamlit evaluation, additionally install and pin the original UI/embedding dependencies, obtain the selected embedding model revision, record extraction/cache provenance, and freeze a genuinely annotated evaluation protocol. The audit dependency lock alone is not a full app environment specification.
