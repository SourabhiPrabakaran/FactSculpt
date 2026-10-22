from typing import List, Dict, Any
from factsculpt.dataset.schema import (
    PairExample,
    MainClass,
    ShiftDirection,
    ShiftSeverity,
    AttributeAnnotation,
    ClaimAnnotation,
)

HARD_CASE_DEFINITIONS = [
    # 1. Multi-sentence merges with subtle causal linkage
    {
        "id": "hc_01",
        "category": "multi_sentence_merge",
        "source": "Designed a dashboard for server health. Separately, cluster downtime decreased by 15% following hardware maintenance.",
        "enhanced": "Designed a server health dashboard that directly reduced cluster downtime by 15%.",
        "main_class": MainClass.C3,
        "target_shifts": ["causal_link_inflation", "impact_inflation"],
        "shift_vector": {"role": 0.3, "qualifier": 0.0, "scope": 0.0, "certainty": 0.8, "impact": 0.9, "quantity": 0.0},
        "severity": 0.70,
        "notes": "Spurious causal connection forged between independent dashboard and hardware downtime reduction."
    },
    # 2. Claim merging
    {
        "id": "hc_02",
        "category": "claim_merging",
        "source": "Assisted with training a computer vision model. Tested it on 5 benchmark datasets.",
        "enhanced": "Spearheaded the training and testing of an advanced computer vision model across 5 benchmarks.",
        "main_class": MainClass.C3,
        "target_shifts": ["role_inflation", "qualifier_inflation"],
        "shift_vector": {"role": 0.85, "qualifier": 0.75, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
        "severity": 0.65,
        "notes": "Merged training and testing tasks into unified leadership and added 'advanced'."
    },
    # 3. Negation handling
    {
        "id": "hc_03",
        "category": "negation",
        "source": "Did not participate in the core architecture design.",
        "enhanced": "Participated in the core architecture design.",
        "main_class": MainClass.C4,
        "target_shifts": ["direct_negation_inversion"],
        "shift_vector": {"role": 1.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
        "severity": 0.95,
        "notes": "Direct negation inverted to claim unverified involvement."
    },
    # 4. Hedging conversion
    {
        "id": "hc_04",
        "category": "hedging_to_assertion",
        "source": "Initial prototype benchmarking may indicate potential throughput improvements under select workloads.",
        "enhanced": "Our benchmarking proves guaranteed throughput improvements across all workloads.",
        "main_class": MainClass.C3,
        "target_shifts": ["certainty_inflation", "scope_expansion"],
        "shift_vector": {"role": 0.0, "qualifier": 0.0, "scope": 0.8, "certainty": 0.95, "impact": 0.5, "quantity": 0.0},
        "severity": 0.75,
        "notes": "Modal hedging ('may indicate potential') replaced by certainty ('proves guaranteed') and selective scope expanded to all."
    },
    # 5. Numeric inflation: "about 5" -> "over 5"
    {
        "id": "hc_05",
        "category": "numeric_bounds_inflation",
        "source": "Helped analyze approximately 5 datasets.",
        "enhanced": "Analyzed over 5 datasets.",
        "main_class": MainClass.C3,
        "target_shifts": ["quantity_inflation", "role_inflation"],
        "shift_vector": {"role": 0.5, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.75},
        "severity": 0.40,
        "notes": "Strict bounds transition from <= 5 (approx 5) to >= 6 (over 5)."
    },
    # 6. Implicit claims
    {
        "id": "hc_06",
        "category": "implicit_claim_inflation",
        "source": "Worked at a high-growth fintech startup on the payment gateway team.",
        "enhanced": "Engineered the core high-growth payment processing engine for fintech scale.",
        "main_class": MainClass.C3,
        "target_shifts": ["role_inflation", "impact_inflation"],
        "shift_vector": {"role": 0.75, "qualifier": 0.6, "scope": 0.0, "certainty": 0.0, "impact": 0.6, "quantity": 0.0},
        "severity": 0.60,
        "notes": "Passive team membership transmuted into individual ownership of core engine."
    },
    # 7. Qualifier removal as strengthening
    {
        "id": "hc_07",
        "category": "qualifier_removal_strengthening",
        "source": "Constructed a preliminary toy script for monitoring database queries.",
        "enhanced": "Constructed a system for monitoring database queries.",
        "main_class": MainClass.C3,
        "target_shifts": ["qualifier_removal"],
        "shift_vector": {"role": 0.0, "qualifier": 0.8, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
        "severity": 0.50,
        "notes": "Removal of limiting qualifiers ('preliminary toy script') inflates perceived system maturity."
    },
    # 8. Mixed strengthen + weaken
    {
        "id": "hc_08",
        "category": "mixed_strengthen_weaken",
        "source": "Led the local deployment of 10 microservices.",
        "enhanced": "Assisted with the global deployment of 20 microservices.",
        "main_class": MainClass.C5,
        "target_shifts": ["role_weakening", "scope_expansion", "quantity_inflation"],
        "shift_vector": {"role": -0.8, "qualifier": 0.0, "scope": 0.8, "certainty": 0.0, "impact": 0.0, "quantity": 0.6},
        "severity": 0.65,
        "notes": "Simultaneous role demotion (led -> assisted) alongside scope expansion (local -> global) and quantity increase."
    },
    # 9. Multiple simultaneous shifts
    {
        "id": "hc_09",
        "category": "multiple_simultaneous_shifts",
        "source": "Supported regional testing of 3 prototypes with tentative results.",
        "enhanced": "Spearheaded nationwide deployment of 15 advanced systems with proven high-impact results.",
        "main_class": MainClass.C3,
        "target_shifts": ["role", "scope", "quantity", "qualifier", "certainty", "impact"],
        "shift_vector": {"role": 0.9, "qualifier": 0.7, "scope": 0.8, "certainty": 0.9, "impact": 0.85, "quantity": 0.8},
        "severity": 0.88,
        "notes": "All 6 evidential attributes shifted simultaneously in strengthening direction."
    },
    # 10. Indirect claim attribution
    {
        "id": "hc_10",
        "category": "indirect_attribution",
        "source": "Reported to the VP of Engineering who led the acquisition integration.",
        "enhanced": "Partnered on the executive acquisition integration.",
        "main_class": MainClass.C3,
        "target_shifts": ["role_inflation"],
        "shift_vector": {"role": 0.8, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
        "severity": 0.70,
        "notes": "Reporting relationship transformed into executive partnership."
    }
]

class HardCaseSubsetGenerator:
    """
    Constructs the curated hard-case evaluation set containing edge cases:
    multi-sentence merges, negation, hedging, bounds shifts, qualifier removals,
    and mixed-direction shifts.
    """

    def generate_hard_cases(self) -> List[PairExample]:
        hard_cases: List[PairExample] = []
        for defn in HARD_CASE_DEFINITIONS:
            hard_cases.append(
                PairExample(
                    example_id=defn["id"],
                    domain="resumes_hard_cases",
                    source_cluster_id=f"cluster_{defn['category']}",
                    source_text=defn["source"],
                    enhanced_text=defn["enhanced"],
                    target_shift_types=defn["target_shifts"],
                    main_class=defn["main_class"],
                    shift_vector=defn["shift_vector"],
                    severity=defn["severity"],
                    is_hard_case=True,
                    annotations=[
                        ClaimAnnotation(
                            claim_id=f"claim_{defn['id']}",
                            main_class=defn["main_class"],
                            reasons=[defn["notes"]]
                        )
                    ]
                )
            )
        return hard_cases
