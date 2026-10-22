# Reproducing this release

The package preserves the original project-relative layout. It is a small source-and-derived-results release, not an environment or model distribution. Original audit notes describe the historical machine; `<LOCAL_HOME>` redactions are not executable paths. Use your own Python 3.12 interpreter.

1. Create `audit_workspace`, and copy the `FactSculpt` application directory to `audit_workspace/FactSculpt` (omit caches).
2. Install the recorded targets from the repository root:

```powershell
python -m pip install --target audit_workspace/deps -r paper_foundation/audit/requirements-audit.lock.txt
python -m pip install --target audit_workspace/neural_deps --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cpu -r paper_foundation/research_positioning/requirements-neural.lock.txt
python paper_foundation/research_positioning/fetch_research_resources.py --model-files
```

Inspect the acquisition manifest and verify its hashes against the supplied `resource_manifest.json` before inference. Network acquisition and dependency compatibility depend on your platform. The fetch script also requests bibliographic metadata. It must not be used to infer redistribution permission.

3. The real-data transfer, genuine NLI and scalar/repair controls are replayed with:

```powershell
python paper_foundation/research_positioning/execute_probe.py
python paper_foundation/research_positioning/validate_results.py
python paper_foundation/final_review/run_controls.py
python paper_foundation/final_review/verify_controls.py
```

The genuine probe additionally expects reconstructed synthetic inputs; follow `paper_foundation/audit/REPRODUCE.md` and the audit report for that stage before running the probe. Do not equate reconstructed synthetic data with recovered historical artifacts. Use a new copy for reruns to avoid cache mixing. The controls script asserts source-copy hashes and recomputes all 1,126 vectors against saved earlier outputs. Package README edits are intentional documentation changes and do not alter Python source.

Saved results can be inspected without acquiring raw data. The supplied validators may require locally acquired resources or the reconstructed working copy; they are not a turnkey substitute for those inputs. Original document-only validators/build scripts and the Word file are omitted. Full replication on a clean machine was not executed during upload packaging. This stage checked Python syntax, source preservation, archive integrity and candidate credential patterns; it did not rerun experiments or obtain human judgments.

See `paper_foundation/final_review/README_REPRODUCIBILITY.md` for the recorded thresholds, label mapping, training seeds, model pins and exact historical commands. Those notes refer to the larger local review package, portions of which are deliberately not published here. `paper_foundation/final_review/FINAL_REVIEW_REPORT.md` also describes that larger local delivery; its Word/support-archive references do not imply those files are in this release.
