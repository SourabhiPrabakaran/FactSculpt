# Independent six-facet and repair annotation protocol

Status: prepared for a prospective study, not executed human validation. No independent ratings were supplied with the project. Blank forms and these instructions are not gold labels. Guideline examples below are author-created illustrations and must not enter the evaluation set as independent judgments.

## Freeze the task before collecting labels

The source is the authorized context; do not infer extra facts from general knowledge. Annotate the source–rewrite pair, not either text in isolation. Preserve original Unicode text and zero-based character offsets. First align the assertion and identify its subject, action, object, time, domain and population. If those change, record an unsupported/substitution flag rather than forcing a signed strength decision. Distinguish source unreliability from failure of a rewrite to stay within the supplied source.

Use seven nominal labels independently for each facet: **strengthened, weakened, unchanged, not applicable, ambiguous, incomparable, insufficient context**. A missing model profile is an implementation status, not an annotation label. Unknown model vocabulary does not determine the human label. Record source and rewrite spans and a brief evidence-grounded rationale; do not assign magnitudes in [−1,1] without a separate preference study.

| Facet | Decision criterion | Avoid |
|---|---|---|
| Role/agency | Does the rewrite assert greater or lesser responsibility, control or ownership for the same activity? | Treating different job functions as a universal rank |
| Qualifier | Does an added/changed descriptor assert a stronger evidenced capability or quality? | Automatically treating promotional style as a factual strength change; flag style separately |
| Scope | Does the claim cover a wider/narrower population, location, period or set of circumstances? | Ordering unrelated populations or geographies |
| Certainty | Does epistemic or causal commitment increase/decrease for the same proposition? | Confusing statistical uncertainty, recommendation strength and causal strength |
| Impact | Is the claimed consequence or effectiveness stronger/weaker under comparable outcomes and conditions? | Ordering different endpoints without a stated comparison |
| Quantity | Does magnitude or a bound increase/decrease under identical referents, units, denominators and periods? | Assuming a larger number is always a stronger beneficial claim; conflating changed units with changed evidence |

**Unchanged:** comparable assertion and facet force preserved, including an appropriate paraphrase. **Not applicable:** the facet is absent or irrelevant to both assertions. **Ambiguous:** available wording supports multiple interpretations. **Incomparable:** values are clear but no meaningful common order is justified. **Insufficient context:** the supplied evidence cannot resolve the comparison. Preserve these distinctions instead of merging them into zero.

Author-created training illustrations: “may reduce delay” → “will reduce delay” illustrates certainty strengthening; an exact copy illustrates unchanged; two claims with no numeric content illustrate quantity not applicable; “worked as a designer” → “worked as a tester” illustrates potentially incomparable roles; a source fragment with no referent for “these patients” illustrates insufficient context. These examples illustrate the policy only and are not measured results.

Record global unsupportedness, contradiction and claim-identity substitution separately. For a prospective gold task, define mixed only as both strengthened and weakened applicable facets. Keep a separate contradiction flag; do not silently treat contradiction-only cases as mixed. This prospective policy intentionally differs from the current implementation's C5 exception and requires a versioned mapping when evaluated.

## Independent collection and adjudication

Recruit at least two fluent annotators with domain competence for scientific causal language. Obtain rights to share the released text with them before distributing annotation packets. Randomize pair order, hide model outputs, remove generator labels and keep annotator identities separate from ratings. Provide the same source context to all annotators. Run a pilot to revise guidelines; freeze them before the held-out study. Split by independent source and transformation family, not random near-duplicate sentences. Do not choose evaluation pairs based on model correctness.

Annotators work independently. An adjudicator resolves disagreement only after original ratings are locked; retain raw disagreements, adjudication rationale and guideline version. Do not have a single annotator simulate multiple raters. An LLM may assist formatting, but its labels must not be described as independent human ratings.

The machine-readable blank form is `annotation_form.csv`: pair ID, annotator ID, each facet's label/spans/rationale, global flags and context adequacy. Resolve pair IDs against the pinned acquisition data locally; the shareable form contains no raw released text. The held-out study needs natural examples covering multiple facets and mixed/unsupported cases; the existing causal-direction labels do not supply them.

## Agreement and system evaluation

Report raw agreement and nominal Krippendorff alpha per facet across all seven categories, with the valid-rating counts and missingness policy. For comparable ordered decisions only (weakened/unchanged/strengthened), additionally report weighted Cohen kappa for two raters, declaring linear or quadratic weights and the exclusions. Do not compute weighted kappa across ambiguous/incomparable labels. Report agreement before adjudication; adjudicated agreement is not independent reliability.

Evaluate per-facet detection/direction, class support, coverage and abstention errors against adjudicated labels. Report macro and per-class F1 for a prespecified overall taxonomy, explaining any C5 exception. Compare scalar and vector decisions on identical context, splits and backend outputs. Use source-group resampling for intervals when sufficient independent groups exist; never count near-template repeats as independent people or observations. Annotation count and power remain study-design decisions, not completed sample sizes.

## Independent repair study

For a representative held-out subset, present the source, original rewrite and blinded candidate edits in randomized order. Include the actual repair output, unchanged-rewrite control and source-copy control; add a genuine regeneration/prompting baseline only if executed. Source copying is a fidelity anchor, not proof of accomplishing a rewriting objective.

Collect separate judgments of source fidelity, residual exaggeration, unsupported additions, retained intended content, meaning preservation and grammatical fluency. Record error spans; separate correction of an inflated assertion from accidental loss of valid content. Do not show internal `verified_safe` flags. Use two independent raters and adjudication, with label agreement and rating reliability reported separately. Only then estimate quality rates. Successful execution, edit counts, lexical overlap or the detector's own score cannot substitute for these outcomes.
