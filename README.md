# FactSculpt

FactSculpt is a research prototype for comparing a source claim with a rewrite using six signed facets: role, qualifier, scope, certainty, impact and quantity. It includes rule-based decisions, ordinal term scales and a bounded regex repair pipeline.

## Scope and evidence

The original implementation is under `FactSculpt/`. Additional audit and evaluation work is under `paper_foundation/`. The external evaluation dataset was added during that later work; it was not supplied as part of the original application, created by the project authors, or used to provide six-facet human labels.

This is a prototype release, not a demonstrated state-of-the-art system. CLI, Streamlit and repair use different backend paths. Heuristic pseudo-NLI scores are not genuine neural predictions. Historical README performance and license badges are not validated; the old text is retained only in `docs/HISTORICAL_README_UNVERIFIED.md`.

## Run the browser demonstration

The user-facing browser demonstration is `FactSculpt/web/index.html`. Start a static server from the repository root (Python 3 is sufficient; no Streamlit installation is needed for this interface):

```text
python -m http.server 8080 --bind 127.0.0.1 --directory FactSculpt/web
```

Open http://localhost:8080/index.html . Stop the server with Ctrl+C. You may also open `FactSculpt/web/index.html` directly, but clipboard access can depend on browser permissions. If port 8080 is in use, select a free port and change the URL accordingly. This is a static local server, not a Python inference API.

Paste text or use Upload / drag and drop on either input. File pickers advertise `.txt`, `.md`, `.json`, `.csv`, and `.text`. Non-JSON formats are read as text; CSV is not parsed into a dataset. The page takes the first file per selection/drop, not a batch. A JSON object can populate both fields using `source` / `original` / `premise` and `enhanced` / `rewrite` / `hypothesis`. For arrays, only the first entry is considered and only source/original and enhanced/rewrite aliases are implemented. Invalid or unmatched JSON falls back to plain text. There is no PDF/DOCX parser; renaming a document to `.txt` does not convert it. Read failures display an error. No explicit file-size limit is enforced, so use small text files.

Example paired JSON:

```json
{"source":"The pilot suggests a reduction.","rewrite":"The study proves a universal reduction."}
```

The JavaScript FileReader reads the selected content in the browser. The reviewed code contains no inference fetch/API call; analysis uses presets and keyword heuristics, separately from the Python system. The page requests Google Fonts, so opening it may still make external font requests. Heuristic scores and suggested edits are not calibrated probabilities or independently verified repair-quality measurements. No browser performance or six-facet human-validation claim follows from the upload feature.

## Optional Python application and paper experiments

The original Streamlit application remains a separate Python entry point. If you specifically want that interface, use Python 3.12 and an isolated environment:

```text
python -m pip install -r FactSculpt/requirements.txt
python -m streamlit run FactSculpt/app.py
```

Opening `index.html` does not invoke this pipeline. Application requirements use ranges; paper experiments use recorded locks and the scripts in `REPRODUCE_RELEASE.md`. Neural backends may download third-party models and may have fallback behavior; inspect provenance before interpreting their outputs. Supply any credentials locally through environment variables and never commit them.

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
