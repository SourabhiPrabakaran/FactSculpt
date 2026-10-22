# FactSculpt

FactSculpt is a research prototype for comparing a source claim with a rewrite using six signed facets: role, qualifier, scope, certainty, impact and quantity. It includes rule-based decisions, ordinal term scales and a bounded regex repair pipeline.

## Scope and evidence

The original implementation is under `FactSculpt/`. Additional audit and evaluation work is under `paper_foundation/`. The external evaluation dataset was added during that later work; it was not supplied as part of the original application, created by the project authors, or used to provide six-facet human labels.

This is a prototype release, not a demonstrated state-of-the-art system. CLI, Streamlit and repair use different backend paths. Heuristic pseudo-NLI scores are not genuine neural predictions. Historical README performance and license badges are not validated; the old text is retained only in `docs/HISTORICAL_README_UNVERIFIED.md`.

## Run the application

Use Python 3.12 and a fresh virtual environment. Install `FactSculpt/requirements.txt`, then from this repository root run:

```text
python -m pip install -r FactSculpt/requirements.txt
python -m streamlit run FactSculpt/app.py
```

Application requirements use ranges; paper experiments use the separate recorded locks. Neural backends may download third-party models. Review configuration and backend provenance before interpreting outputs. Credentials, if needed, must be supplied locally through environment variables and never committed.

## Verified component evaluation

The external scientific-exaggeration release by Wright and Augenstein supplies 100 training pairs and 563 test pairs (96 downplays, 345 same, 122 exaggerates). Source: https://github.com/copenlu/scientific-exaggeration-detection at commit `6e535ca60e1e5b09bb2b9b6119637073036660f0`. Raw text is not bundled because redistribution rights remain unresolved; download instructions and hashes are provided.

| Transfer method | Macro-F1 | Accuracy | Coverage |
|---|---:|---:|---:|
| Majority | .2533 | .6128 | 1.0000 |
| Regex hand-coded vector adapter | .2930 | .4796 | .9734 |
| Regex seed-ordinal vector adapter | .3612 | .4707 | .9485 |
| Exploratory scalar hand-coded control | .3077 | .5400 | 1.0000 |
| Exploratory scalar ordinal control | .3724 | .4920 | 1.0000 |

Scalar controls were chosen after inspecting earlier results, and have a different coverage policy. These point estimates do not establish vector utility or general superiority. Repair completed 563 executions and changed 32 outputs; this is not a repair-quality measurement. Synthetic diagnostic labels are generator labels, not independent human ground truth. No independent annotators were available at final review.

## Reproduction and artifacts

Start with `REPRODUCE_RELEASE.md`. Original replay scripts and saved numerical outputs retain their project-relative layout. The full audit and final review provide qualifications and missing evidence. Four editable SVG diagrams and their PNG exports are under `paper_foundation/figures/`.

No trained weights, external raw dataset text, environment folders, credentials or local caches are bundled. The Word manuscript is maintained separately. This release is not an accepted publication and does not claim to reproduce the closest predecessor.

## Rights and citation

See `RIGHTS_AND_ATTRIBUTION.md`. No new open-source license is asserted: the original MIT badge had no corresponding recovered license grant. Confirm ownership and obtain teammate/supervisor agreement before choosing a license. Cite the upstream dataset independently. After uploading, cite this repository's actual release and immutable commit in the manuscript; no repository URL is invented here.
