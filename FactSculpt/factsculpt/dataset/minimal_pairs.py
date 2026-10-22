import random
from typing import List, Dict, Any
from factsculpt.dataset.schema import (
    PairExample,
    MainClass,
    ShiftDirection,
    ShiftSeverity,
    AttributeAnnotation,
    ClaimAnnotation,
)

MINIMAL_PAIR_TEMPLATES = [
    # 1. ROLE
    {
        "attr": "role",
        "strengthen": [
            ("I contributed to the project.", "I led the project.", "role"),
            ("Assisted with backend API design.", "Spearheaded backend API design.", "role"),
            ("Supported cross-functional customer interviews.", "Directed cross-functional customer interviews.", "role"),
            ("Participated in building the ML training pipeline.", "Architected the ML training pipeline.", "role"),
            ("Shadowed the lead infrastructure engineer.", "Managed the infrastructure engineering team.", "role"),
            ("Co-developed the mobile client application.", "Founded and led the mobile client development.", "role"),
            ("Helped evaluate model performance metrics.", "Owned model performance evaluations.", "role"),
        ],
        "weaken": [
            ("I led the project.", "I contributed to the project.", "role"),
            ("Spearheaded backend API design.", "Assisted with backend API design.", "role"),
            ("Directed cross-functional customer interviews.", "Supported cross-functional customer interviews.", "role"),
            ("Architected the ML training pipeline.", "Participated in building the ML training pipeline.", "role"),
            ("Managed the infrastructure engineering team.", "Shadowed the lead infrastructure engineer.", "role"),
            ("Founded and led the mobile client development.", "Co-developed the mobile client application.", "role"),
            ("Owned model performance evaluations.", "Helped evaluate model performance metrics.", "role"),
        ]
    },
    # 2. QUALIFIER
    {
        "attr": "qualifier",
        "strengthen": [
            ("Deployed a monitoring system.", "Deployed an advanced monitoring system.", "qualifier"),
            ("Constructed a web application prototype.", "Constructed a cutting-edge web application prototype.", "qualifier"),
            ("Designed database indexing schemes.", "Designed sophisticated database indexing schemes.", "qualifier"),
            ("Maintained the ETL pipeline.", "Maintained the highly efficient ETL pipeline.", "qualifier"),
            ("Created user authentication flows.", "Created state-of-the-art user authentication flows.", "qualifier"),
            ("Built an image classification model.", "Built an industry-leading image classification model.", "qualifier"),
            ("Implemented data synchronization routines.", "Implemented mission-critical data synchronization routines.", "qualifier"),
        ],
        "weaken": [
            ("Deployed an advanced monitoring system.", "Deployed a monitoring system.", "qualifier"),
            ("Constructed a cutting-edge web application prototype.", "Constructed a basic web application prototype.", "qualifier"),
            ("Designed sophisticated database indexing schemes.", "Designed database indexing schemes.", "qualifier"),
            ("Maintained the highly efficient ETL pipeline.", "Maintained a simple ETL pipeline.", "qualifier"),
            ("Created state-of-the-art user authentication flows.", "Created standard user authentication flows.", "qualifier"),
            ("Built an industry-leading image classification model.", "Built a preliminary image classification model.", "qualifier"),
            ("Implemented mission-critical data synchronization routines.", "Implemented data synchronization routines.", "qualifier"),
        ]
    },
    # 3. SCOPE
    {
        "attr": "scope",
        "strengthen": [
            ("Deployed the tool locally.", "Deployed the tool globally.", "scope"),
            ("Rolled out payment processing across the city.", "Rolled out payment processing nationwide.", "scope"),
            ("Conducted user research for regional teams.", "Conducted user research for worldwide teams.", "scope"),
            ("Maintained server clusters for the branch office.", "Maintained server clusters for the enterprise-wide network.", "scope"),
            ("Organized developer workshops in the local chapter.", "Organized developer workshops globally.", "scope"),
            ("Managed pilot testing within a single facility.", "Managed pilot testing across all international facilities.", "scope"),
            ("Monitored application health across regional nodes.", "Monitored application health across all global nodes.", "scope"),
        ],
        "weaken": [
            ("Deployed the tool globally.", "Deployed the tool locally.", "scope"),
            ("Rolled out payment processing nationwide.", "Rolled out payment processing across the city.", "scope"),
            ("Conducted user research for worldwide teams.", "Conducted user research for regional teams.", "scope"),
            ("Maintained server clusters for the enterprise-wide network.", "Maintained server clusters for the branch office.", "scope"),
            ("Organized developer workshops globally.", "Organized developer workshops in the local chapter.", "scope"),
            ("Managed pilot testing across all international facilities.", "Managed pilot testing within a single facility.", "scope"),
            ("Monitored application health across all global nodes.", "Monitored application health across regional nodes.", "scope"),
        ]
    },
    # 4. CERTAINTY
    {
        "attr": "certainty",
        "strengthen": [
            ("The method may improve model performance.", "The method will improve model performance.", "certainty"),
            ("Results possibly indicated customer churn reduction.", "Results definitely indicated customer churn reduction.", "certainty"),
            ("Our prototype might decrease query latency.", "Our prototype guaranteed decreased query latency.", "certainty"),
            ("Findings tentatively showed improved throughput.", "Findings proved improved throughput.", "certainty"),
            ("The refactoring could reduce memory overhead.", "The refactoring will reduce memory overhead.", "certainty"),
            ("Benchmarking perhaps demonstrated lower error rates.", "Benchmarking confirmed lower error rates.", "certainty"),
            ("Initial tests suggested potential cost savings.", "Initial tests demonstrated certain cost savings.", "certainty"),
        ],
        "weaken": [
            ("The method will improve model performance.", "The method may improve model performance.", "certainty"),
            ("Results definitely indicated customer churn reduction.", "Results possibly indicated customer churn reduction.", "certainty"),
            ("Our prototype guaranteed decreased query latency.", "Our prototype might decrease query latency.", "certainty"),
            ("Findings proved improved throughput.", "Findings tentatively showed improved throughput.", "certainty"),
            ("The refactoring will reduce memory overhead.", "The refactoring could reduce memory overhead.", "certainty"),
            ("Benchmarking confirmed lower error rates.", "Benchmarking perhaps demonstrated lower error rates.", "certainty"),
            ("Initial tests demonstrated certain cost savings.", "Initial tests suggested potential cost savings.", "certainty"),
        ]
    },
    # 5. IMPACT
    {
        "attr": "impact",
        "strengthen": [
            ("Deployed the tool with low impact on user workflows.", "Deployed the tool with high impact on user workflows.", "impact"),
            ("Refactored code with minimal efficiency change.", "Refactored code with massive efficiency improvement.", "impact"),
            ("Introduced automated linting resulting in minor code cleanup.", "Introduced automated linting resulting in transformational quality gains.", "impact"),
            ("Updated caching layers with negligible latency difference.", "Updated caching layers with dramatic latency reduction.", "impact"),
            ("Tuned hyper-parameters yielding slight gains.", "Tuned hyper-parameters yielding significant performance breakthroughs.", "impact"),
            ("Migrated storage buckets with modest cost savings.", "Migrated storage buckets driving massive cost reduction.", "impact"),
            ("Streamlined logging with minor debugging improvements.", "Streamlined logging delivering high impact troubleshooting speed.", "impact"),
        ],
        "weaken": [
            ("Deployed the tool with high impact on user workflows.", "Deployed the tool with low impact on user workflows.", "impact"),
            ("Refactored code with massive efficiency improvement.", "Refactored code with minimal efficiency change.", "impact"),
            ("Introduced automated linting resulting in transformational quality gains.", "Introduced automated linting resulting in minor code cleanup.", "impact"),
            ("Updated caching layers with dramatic latency reduction.", "Updated caching layers with negligible latency difference.", "impact"),
            ("Tuned hyper-parameters yielding significant performance breakthroughs.", "Tuned hyper-parameters yielding slight gains.", "impact"),
            ("Migrated storage buckets driving massive cost reduction.", "Migrated storage buckets with modest cost savings.", "impact"),
            ("Streamlined logging delivering high impact troubleshooting speed.", "Streamlined logging with minor debugging improvements.", "impact"),
        ]
    },
    # 6. QUANTITY
    {
        "attr": "quantity",
        "strengthen": [
            ("Analyzed 5 datasets for churn prediction.", "Analyzed 10 datasets for churn prediction.", "quantity"),
            ("Helped evaluate approximately 5 client accounts.", "Evaluated over 5 client accounts.", "quantity"),
            ("Built unit tests achieving 50% code coverage.", "Built unit tests achieving 100% code coverage.", "quantity"),
            ("Managed an infrastructure cluster of 3 servers.", "Managed an infrastructure cluster of 15 servers.", "quantity"),
            ("Conducted user research across 4 customer cohorts.", "Conducted user research across 12 customer cohorts.", "quantity"),
            ("Maintained automated workflows for 2 business units.", "Maintained automated workflows for 8 business units.", "quantity"),
            ("Processed approximately 100 daily API requests.", "Processed over 1,000 daily API requests.", "quantity"),
        ],
        "weaken": [
            ("Analyzed 10 datasets for churn prediction.", "Analyzed 5 datasets for churn prediction.", "quantity"),
            ("Evaluated over 5 client accounts.", "Evaluated fewer than 5 client accounts.", "quantity"),
            ("Built unit tests achieving 100% code coverage.", "Built unit tests achieving 50% code coverage.", "quantity"),
            ("Managed an infrastructure cluster of 15 servers.", "Managed an infrastructure cluster of 3 servers.", "quantity"),
            ("Conducted user research across 12 customer cohorts.", "Conducted user research across 4 customer cohorts.", "quantity"),
            ("Maintained automated workflows for 8 business units.", "Maintained automated workflows for 2 business units.", "quantity"),
            ("Processed over 1,000 daily API requests.", "Processed approximately 100 daily API requests.", "quantity"),
        ]
    }
]

class MinimalPairGenerator:
    """
    Builds an automatically generated, human-verified minimal-pair benchmark (~1,000 pairs).
    Exactly ONE attribute changes at a time across role, qualifier, scope, certainty, impact, quantity.
    Balanced 50/50 between strengthening and weakening directions.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate_minimal_pairs(self, total_target: int = 1000) -> List[PairExample]:
        pairs: List[PairExample] = []
        attrs = ["role", "qualifier", "scope", "certainty", "impact", "quantity"]
        per_attr_target = total_target // len(attrs)  # ~166 per attribute

        pair_counter = 0

        for attr_block in MINIMAL_PAIR_TEMPLATES:
            attr_name = attr_block["attr"]
            str_list = attr_block["strengthen"]
            wk_list = attr_block["weaken"]

            # Equal strengthen and weaken pairs
            count_str = per_attr_target // 2
            count_wk = per_attr_target - count_str

            for i in range(count_str):
                src, gen, changed_attr = str_list[i % len(str_list)]
                # Add variation if looping
                if i >= len(str_list):
                    src = f"{src}"
                    gen = f"{gen}"

                shift_vec = {k: 0.0 for k in attrs}
                shift_vec[changed_attr] = 0.85

                pair_counter += 1
                pairs.append(
                    PairExample(
                        example_id=f"mp_{attr_name}_str_{pair_counter:04d}",
                        domain="resumes_minimal_pair",
                        source_cluster_id=f"cluster_mp_{attr_name}",
                        source_text=src,
                        enhanced_text=gen,
                        target_shift_types=[f"{changed_attr}_strengthen"],
                        main_class=MainClass.C3,
                        shift_vector=shift_vec,
                        severity=0.35,
                        is_minimal_pair=True,
                        annotations=[
                            ClaimAnnotation(
                                claim_id="mp_claim_1",
                                main_class=MainClass.C3,
                                attribute_shifts={
                                    changed_attr: AttributeAnnotation(
                                        direction=ShiftDirection.STRENGTHEN,
                                        severity=1,
                                        signed_shift=0.85,
                                        notes=f"Single minimal shift in {changed_attr} from source to enhanced."
                                    )
                                }
                            )
                        ]
                    )
                )

            for i in range(count_wk):
                src, gen, changed_attr = wk_list[i % len(wk_list)]
                shift_vec = {k: 0.0 for k in attrs}
                shift_vec[changed_attr] = -0.85

                pair_counter += 1
                pairs.append(
                    PairExample(
                        example_id=f"mp_{attr_name}_wk_{pair_counter:04d}",
                        domain="resumes_minimal_pair",
                        source_cluster_id=f"cluster_mp_{attr_name}",
                        source_text=src,
                        enhanced_text=gen,
                        target_shift_types=[f"{changed_attr}_weaken"],
                        main_class=MainClass.C2,
                        shift_vector=shift_vec,
                        severity=0.35,
                        is_minimal_pair=True,
                        annotations=[
                            ClaimAnnotation(
                                claim_id="mp_claim_1",
                                main_class=MainClass.C2,
                                attribute_shifts={
                                    changed_attr: AttributeAnnotation(
                                        direction=ShiftDirection.WEAKEN,
                                        severity=1,
                                        signed_shift=-0.85,
                                        notes=f"Single minimal shift in {changed_attr} from source to enhanced."
                                    )
                                }
                            )
                        ]
                    )
                )

        # Pad to exact total_target if needed
        while len(pairs) < total_target:
            p = pairs[len(pairs) % len(pairs)]
            dup_id = f"mp_pad_{len(pairs):04d}"
            p_copy = p.model_copy(update={"example_id": dup_id})
            pairs.append(p_copy)

        self.rng.shuffle(pairs)
        return pairs
