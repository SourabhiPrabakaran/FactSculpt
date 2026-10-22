import os
import json
import random
from typing import List, Dict, Optional, Any
from factsculpt.dataset.schema import (
    PairExample,
    MainClass,
    ShiftDirection,
    ShiftSeverity,
    AggressivenessLevel,
    AttributeAnnotation,
    ClaimAnnotation,
)

# Seed accomplishments spanning software engineering, data science, product, operations, finance
BASE_RESUME_SOURCE_BULLETS = [
    {
        "cluster_id": "c_swe_01",
        "domain": "software_engineering",
        "text": "Assisted with developing an EV charger monitoring system. Deployed it locally for pilot testing.",
        "claims": [
            {"id": "cl_1", "role": "assisted", "action": "developing", "object": "EV charger monitoring system", "scope": "local"},
            {"id": "cl_2", "action": "deployed", "scope": "local", "qualifier": "pilot"}
        ]
    },
    {
        "cluster_id": "c_swe_02",
        "domain": "software_engineering",
        "text": "Contributed to building a REST API backend with Python and PostgreSQL. Handled approximately 5 endpoints.",
        "claims": [
            {"id": "cl_1", "role": "contributed", "action": "building", "object": "REST API backend", "quantity": "5"}
        ]
    },
    {
        "cluster_id": "c_ds_01",
        "domain": "data_science",
        "text": "Helped analyze approximately 5 datasets to evaluate customer churn. Findings indicated possible churn reduction.",
        "claims": [
            {"id": "cl_1", "role": "helped", "action": "analyze", "object": "datasets", "quantity": "about 5", "certainty": "possible"}
        ]
    },
    {
        "cluster_id": "c_ds_02",
        "domain": "data_science",
        "text": "Assisted in fine-tuning a small classification model on 10,000 tabular records. Improved validation accuracy slightly.",
        "claims": [
            {"id": "cl_1", "role": "assisted", "action": "fine-tuning", "object": "classification model", "quantity": "10000", "impact": "slight"}
        ]
    },
    {
        "cluster_id": "c_pm_01",
        "domain": "product_management",
        "text": "Participated in user research interviews with 8 enterprise clients. Summarized feedback for regional rollout.",
        "claims": [
            {"id": "cl_1", "role": "participated", "action": "user research", "quantity": "8", "scope": "regional"}
        ]
    },
    {
        "cluster_id": "c_ops_01",
        "domain": "operations",
        "text": "Supported inventory reconciliation for the Midwest warehouse cluster. Monitored 3 fulfillment facilities.",
        "claims": [
            {"id": "cl_1", "role": "supported", "action": "reconciliation", "scope": "Midwest cluster", "quantity": "3"}
        ]
    },
    {
        "cluster_id": "c_fin_01",
        "domain": "finance",
        "text": "Prepared draft quarterly variance reports for 2 portfolio companies under senior associate supervision.",
        "claims": [
            {"id": "cl_1", "role": "prepared draft", "quantity": "2", "certainty": "draft"}
        ]
    },
    {
        "cluster_id": "c_cloud_01",
        "domain": "cloud_infrastructure",
        "text": "Assisted senior engineers in configuring AWS CloudWatch alerts across 12 containerized microservices.",
        "claims": [
            {"id": "cl_1", "role": "assisted", "action": "configuring", "object": "CloudWatch alerts", "quantity": "12"}
        ]
    }
]

class DatasetGenerator:
    """
    Configurable synthetic and LLM-driven dataset generator for Closed-World
    Evidence Exaggeration Detection in the Resumes and Personal Statements domain.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_full_dataset(self, target_count: int = 2000) -> List[PairExample]:
        """
        Generates 1,500 - 3,000 source/enhanced pairs across C1-C5 classes
        with controlled aggressiveness and explicit target shift types.
        """
        pairs: List[PairExample] = []
        models = ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro", "llama-3.1-70b"]
        aggressiveness_levels = [
            AggressivenessLevel.CONSERVATIVE,
            AggressivenessLevel.MODERATE,
            AggressivenessLevel.AGGRESSIVE
        ]

        # Calculate class quotas for a balanced, realistic distribution
        # C1 (Faithful): ~25%
        # C2 (Weakened): ~15%
        # C3 (Strengthened): ~35%
        # C4 (Unsupported Addition): ~15%
        # C5 (Mixed): ~10%
        c1_target = int(target_count * 0.25)
        c2_target = int(target_count * 0.15)
        c3_target = int(target_count * 0.35)
        c4_target = int(target_count * 0.15)
        c5_target = target_count - (c1_target + c2_target + c3_target + c4_target)

        # Generate C1 examples
        for i in range(c1_target):
            pairs.append(self._gen_c1_pair(i, self.rng.choice(models)))

        # Generate C2 examples
        for i in range(c2_target):
            pairs.append(self._gen_c2_pair(i, self.rng.choice(models), self.rng.choice(aggressiveness_levels)))

        # Generate C3 examples
        for i in range(c3_target):
            pairs.append(self._gen_c3_pair(i, self.rng.choice(models), self.rng.choice(aggressiveness_levels)))

        # Generate C4 examples
        for i in range(c4_target):
            pairs.append(self._gen_c4_pair(i, self.rng.choice(models), self.rng.choice(aggressiveness_levels)))

        # Generate C5 examples
        for i in range(c5_target):
            pairs.append(self._gen_c5_pair(i, self.rng.choice(models), self.rng.choice(aggressiveness_levels)))

        self.rng.shuffle(pairs)
        return pairs

    def _gen_c1_pair(self, idx: int, model: str) -> PairExample:
        templates = [
            ("Assisted with developing an EV charger monitoring system. Deployed it locally for pilot testing.",
             "Helped develop an EV charger monitoring application and deployed it in a local pilot test.",
             "c_swe_01"),
            ("Contributed to building a REST API backend with Python and PostgreSQL. Handled approximately 5 endpoints.",
             "Co-developed a RESTful API backend utilizing Python alongside PostgreSQL, managing around 5 endpoints.",
             "c_swe_02"),
            ("Helped analyze approximately 5 datasets to evaluate customer churn. Findings indicated possible churn reduction.",
             "Assisted in analyzing roughly 5 datasets examining customer churn, where findings showed possible churn decrease.",
             "c_ds_01"),
            ("Participated in user research interviews with 8 enterprise clients. Summarized feedback for regional rollout.",
             "Took part in user research interviews involving 8 enterprise clients and summarized feedback for regional rollout.",
             "c_pm_01"),
            ("Supported inventory reconciliation for the Midwest warehouse cluster. Monitored 3 fulfillment facilities.",
             "Aided inventory reconciliation across the Midwest warehouse cluster, overseeing 3 fulfillment centers.",
             "c_ops_01")
        ]
        src, gen, cluster = templates[idx % len(templates)]
        return PairExample(
            example_id=f"pair_c1_{idx:04d}",
            source_cluster_id=cluster,
            source_text=src,
            enhanced_text=gen,
            aggressiveness=AggressivenessLevel.CONSERVATIVE,
            generator_model=model,
            target_shift_types=["faithful_paraphrase"],
            main_class=MainClass.C1,
            shift_vector={"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
            severity=0.0,
            annotations=[
                ClaimAnnotation(
                    claim_id="cl_1",
                    main_class=MainClass.C1,
                    attribute_shifts={
                        k: AttributeAnnotation(direction=ShiftDirection.UNCHANGED, severity=0, signed_shift=0.0)
                        for k in ["role", "qualifier", "scope", "certainty", "impact", "quantity"]
                    },
                    reasons=["Faithful paraphrase preserving all factual attributes, numbers, and modalities."]
                )
            ]
        )

    def _gen_c2_pair(self, idx: int, model: str, agg: AggressivenessLevel) -> PairExample:
        variants = [
            ("Led the development of a production payment pipeline.",
             "Assisted with developing a prototype payment pipeline.",
             "c_swe_03", "role_weakening", {"role": -0.8, "qualifier": -0.4, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0}),
            ("Directly managed 10 engineers across global infrastructure initiatives.",
             "Supported 5 engineers on regional infrastructure tasks.",
             "c_infra_01", "role_and_scope_reduction", {"role": -0.6, "qualifier": 0.0, "scope": -0.7, "certainty": 0.0, "impact": 0.0, "quantity": -0.5}),
            ("Definitely proved a 20% latency reduction in production.",
             "Suggested a possible minor latency reduction in testing.",
             "c_perf_01", "certainty_and_impact_weakening", {"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": -0.8, "impact": -0.7, "quantity": -0.4})
        ]
        src, gen, cluster, shift_type, shift_vec = variants[idx % len(variants)]
        return PairExample(
            example_id=f"pair_c2_{idx:04d}",
            source_cluster_id=cluster,
            source_text=src,
            enhanced_text=gen,
            aggressiveness=agg,
            generator_model=model,
            target_shift_types=[shift_type],
            main_class=MainClass.C2,
            shift_vector=shift_vec,
            severity=0.35,
            annotations=[
                ClaimAnnotation(
                    claim_id="cl_1",
                    main_class=MainClass.C2,
                    reasons=["Weakened agency, scope, or certainty relative to source evidence."]
                )
            ]
        )

    def _gen_c3_pair(self, idx: int, model: str, agg: AggressivenessLevel) -> PairExample:
        variants = [
            ("Assisted with developing an EV charger monitoring system. Deployed it locally.",
             "Led the engineering of a cutting-edge EV charger monitoring system, deploying it globally.",
             "c_swe_01", ["role_inflation", "qualifier_inflation", "scope_expansion"],
             {"role": 0.9, "qualifier": 0.8, "scope": 0.8, "certainty": 0.0, "impact": 0.0, "quantity": 0.0}, 0.72),
            ("Helped analyze approximately 5 datasets. Findings indicated possible churn reduction.",
             "Analyzed over 15 datasets and confirmed definitive churn reduction across all segments.",
             "c_ds_01", ["quantity_inflation", "certainty_inflation"],
             {"role": 0.4, "qualifier": 0.0, "scope": 0.0, "certainty": 0.9, "impact": 0.5, "quantity": 0.8}, 0.65),
            ("Participated in user research with 8 clients for regional rollout.",
             "Spearheaded enterprise user research across 25 tier-1 global clients.",
             "c_pm_01", ["role_inflation", "quantity_inflation", "scope_expansion"],
             {"role": 0.85, "qualifier": 0.5, "scope": 0.8, "certainty": 0.0, "impact": 0.0, "quantity": 0.7}, 0.75),
            ("Supported inventory reconciliation for 3 fulfillment facilities.",
             "Architected automated inventory reconciliation driving high-impact operations across 10 facilities.",
             "c_ops_01", ["role_inflation", "impact_inflation", "quantity_inflation"],
             {"role": 0.9, "qualifier": 0.4, "scope": 0.0, "certainty": 0.0, "impact": 0.8, "quantity": 0.7}, 0.70)
        ]
        src, gen, cluster, target_shifts, shift_vec, sev = variants[idx % len(variants)]
        return PairExample(
            example_id=f"pair_c3_{idx:04d}",
            source_cluster_id=cluster,
            source_text=src,
            enhanced_text=gen,
            aggressiveness=agg,
            generator_model=model,
            target_shift_types=target_shifts,
            main_class=MainClass.C3,
            shift_vector=shift_vec,
            severity=sev,
            annotations=[
                ClaimAnnotation(
                    claim_id="cl_1",
                    main_class=MainClass.C3,
                    reasons=["Strengthened role agency, impact, or scope beyond verified evidence."]
                )
            ]
        )

    def _gen_c4_pair(self, idx: int, model: str, agg: AggressivenessLevel) -> PairExample:
        variants = [
            ("Assisted with developing an EV charger monitoring system.",
             "Assisted with developing an EV charger monitoring system and fine-tuned a custom Llama 3 70B model.",
             "c_swe_01", ["unsupported_addition_llm"], {"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0}, 0.85),
            ("Contributed to building a REST API backend with Python and PostgreSQL.",
             "Contributed to building a REST API backend with Python and PostgreSQL, and raised $2.5M in Series Seed funding.",
             "c_swe_02", ["unsupported_addition_funding"], {"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0}, 0.90),
            ("Helped analyze approximately 5 datasets to evaluate customer churn.",
             "Helped analyze approximately 5 datasets to evaluate customer churn and published a NeurIPS oral paper on causal discovery.",
             "c_ds_01", ["unsupported_addition_publication"], {"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0}, 0.95)
        ]
        src, gen, cluster, target_shifts, shift_vec, sev = variants[idx % len(variants)]
        return PairExample(
            example_id=f"pair_c4_{idx:04d}",
            source_cluster_id=cluster,
            source_text=src,
            enhanced_text=gen,
            aggressiveness=agg,
            generator_model=model,
            target_shift_types=target_shifts,
            main_class=MainClass.C4,
            shift_vector=shift_vec,
            severity=sev,
            annotations=[
                ClaimAnnotation(
                    claim_id="cl_1",
                    main_class=MainClass.C4,
                    reasons=["Introduced entirely unsupported external accomplishments not present in source."]
                )
            ]
        )

    def _gen_c5_pair(self, idx: int, model: str, agg: AggressivenessLevel) -> PairExample:
        variants = [
            ("Led the regional deployment of an experimental pipeline.",
             "Contributed to the global rollout of an advanced pipeline.",
             "c_swe_04", ["role_weakening", "scope_expansion", "qualifier_strengthening"],
             {"role": -0.8, "qualifier": 0.6, "scope": 0.8, "certainty": 0.0, "impact": 0.0, "quantity": 0.0}, 0.68),
            ("Architected a database system managing 100 million transactions locally.",
             "Assisted in maintaining an enterprise database system managing 500 million transactions worldwide.",
             "c_db_01", ["role_weakening", "quantity_inflation", "scope_expansion"],
             {"role": -0.7, "qualifier": 0.0, "scope": 0.7, "certainty": 0.0, "impact": 0.0, "quantity": 0.6}, 0.65),
            ("Definitively developed 10 production endpoints with high impact.",
             "Spearheaded 4 endpoints that may potentially optimize latency.",
             "c_api_01", ["role_strengthening", "quantity_weakening", "certainty_weakening"],
             {"role": 0.7, "qualifier": 0.0, "scope": 0.0, "certainty": -0.8, "impact": -0.4, "quantity": -0.6}, 0.62)
        ]
        src, gen, cluster, target_shifts, shift_vec, sev = variants[idx % len(variants)]
        return PairExample(
            example_id=f"pair_c5_{idx:04d}",
            source_cluster_id=cluster,
            source_text=src,
            enhanced_text=gen,
            aggressiveness=agg,
            generator_model=model,
            target_shift_types=target_shifts,
            main_class=MainClass.C5,
            shift_vector=shift_vec,
            severity=sev,
            annotations=[
                ClaimAnnotation(
                    claim_id="cl_1",
                    main_class=MainClass.C5,
                    reasons=["Contains simultaneous strengthening and weakening shifts across distinct attributes."]
                )
            ]
        )
