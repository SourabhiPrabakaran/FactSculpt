import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IAAMetricsReport(BaseModel):
    total_examples_evaluated: int
    num_annotators: int
    overall_fleiss_kappa: Optional[float] = None
    overall_krippendorff_alpha: Optional[float] = None
    attribute_kappas: Dict[str, Optional[float]] = Field(default_factory=dict)
    pairwise_cohen_kappas: Dict[str, float] = Field(default_factory=dict)
    disagreements_count: int = 0
    adjudicated_count: int = 0
    status: str = "PENDING_HUMAN_PARTICIPATION"
    notes: str = (
        "IAA measurement infrastructure is active. In accordance with Closed-World Research "
        "Integrity rules, real annotator ratings are recorded when recruitments complete. "
        "No synthetic agreement figures are fabricated."
    )

def compute_cohens_kappa(rater1: List[str], rater2: List[str]) -> float:
    """
    Computes Cohen's Kappa between two raters.
    kappa = (Po - Pe) / (1 - Pe)
    """
    if len(rater1) != len(rater2) or not rater1:
        return 0.0

    n = len(rater1)
    categories = sorted(list(set(rater1) | set(rater2)))
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    num_cats = len(categories)

    if num_cats <= 1:
        return 1.0

    # Build confusion matrix
    matrix = [[0] * num_cats for _ in range(num_cats)]
    for val1, val2 in zip(rater1, rater2):
        matrix[cat_to_idx[val1]][cat_to_idx[val2]] += 1


    # Observed agreement Po
    po = sum(matrix[i][i] for i in range(num_cats)) / n

    # Expected agreement Pe
    row_sums = [sum(matrix[i][j] for j in range(num_cats)) for i in range(num_cats)]
    col_sums = [sum(matrix[i][j] for i in range(num_cats)) for j in range(num_cats)]
    pe = sum((row_sums[i] * col_sums[i]) for i in range(num_cats)) / (n * n)

    if abs(1.0 - pe) < 1e-9:
        return 1.0
    return round((po - pe) / (1.0 - pe), 4)

def compute_fleiss_kappa(ratings_matrix: List[List[int]]) -> float:
    """
    Computes Fleiss' Kappa for m annotators rating N items into k categories.
    ratings_matrix[i][j] = number of annotators who assigned category j to item i.
    """
    if not ratings_matrix or not ratings_matrix[0]:
        return 0.0

    n_items = len(ratings_matrix)
    n_categories = len(ratings_matrix[0])
    n_raters = sum(ratings_matrix[0])

    if n_raters <= 1 or n_items == 0:
        return 0.0

    # p_j: proportion of all assignments made to category j
    total_ratings = n_items * n_raters
    pj = [
        sum(ratings_matrix[i][j] for i in range(n_items)) / total_ratings
        for j in range(n_categories)
    ]

    # P_i: extent to which raters agree on item i
    pi_list = []
    denom = n_raters * (n_raters - 1)
    for i in range(n_items):
        numerator = sum(ratings_matrix[i][j] ** 2 for j in range(n_categories)) - n_raters
        pi_list.append(numerator / denom)

    p_bar = sum(pi_list) / n_items
    pe_bar = sum(p ** 2 for p in pj)

    if abs(1.0 - pe_bar) < 1e-9:
        return 1.0

    return round((p_bar - pe_bar) / (1.0 - pe_bar), 4)

def compute_krippendorffs_alpha(matrix: List[List[int]]) -> float:
    """
    Computes Krippendorff's Alpha for nominal categories.
    matrix[u][c] = number of annotators who assigned category c to unit u.
    """
    if not matrix or not matrix[0]:
        return 0.0

    n_units = len(matrix)
    n_categories = len(matrix[0])

    m_u = [sum(row) for row in matrix]
    valid_units = [u for u in range(n_units) if m_u[u] > 1]
    if not valid_units:
        return 0.0

    denom_do = sum(m_u[u] * (m_u[u] - 1) for u in valid_units)
    if denom_do == 0:
        return 0.0

    num_do = sum(
        (m_u[u] ** 2 - sum(matrix[u][c] ** 2 for c in range(n_categories)))
        for u in valid_units
    )
    do = num_do / denom_do

    n_c = [sum(matrix[u][c] for u in valid_units) for c in range(n_categories)]
    total_ratings = sum(n_c)
    if total_ratings <= 1:
        return 1.0

    denom_de = total_ratings * (total_ratings - 1)
    num_de = (total_ratings ** 2) - sum(c_count ** 2 for c_count in n_c)
    if denom_de == 0 or num_de == 0:
        return 1.0
    de = num_de / denom_de

    if abs(de) < 1e-9:
        return 1.0

    return round(1.0 - (do / de), 4)

class AnnotationAgreementEvaluator:
    """
    Infrastructure for computing Inter-Annotator Agreement (IAA)
    over human annotations. Returns PENDING status when real annotator
    records are not yet submitted.
    """

    def evaluate_agreement(
        self,
        annotator_records: Optional[List[Dict[str, Any]]] = None
    ) -> IAAMetricsReport:
        if not annotator_records or len(annotator_records) < 3:
            return IAAMetricsReport(
                total_examples_evaluated=len(annotator_records) if annotator_records else 0,
                num_annotators=len(annotator_records) if annotator_records else 0,
                overall_fleiss_kappa=None,
                attribute_kappas={
                    "role": None,
                    "qualifier": None,
                    "scope": None,
                    "certainty": None,
                    "impact": None,
                    "quantity": None
                },
                pairwise_cohen_kappas={},
                status="PENDING_HUMAN_PARTICIPATION",
                notes="Real human multi-annotator collection is pending recruitments. Zero data fabricated."
            )

        # Implementation for real records if provided
        # annotator_records: List of dicts per annotator: [{"annotator_id": "A1", "labels": {"ex_1": "C3", ...}}, ...]
        all_example_ids = sorted(list(set.intersection(*[set(r["labels"].keys()) for r in annotator_records])))
        categories = ["C1", "C2", "C3", "C4", "C5"]
        cat_map = {c: i for i, c in enumerate(categories)}

        matrix = []
        for ex_id in all_example_ids:
            row = [0] * len(categories)
            for r in annotator_records:
                lab = r["labels"].get(ex_id, "C1")
                if lab in cat_map:
                    row[cat_map[lab]] += 1
            matrix.append(row)

        overall_kappa = compute_fleiss_kappa(matrix)
        overall_alpha = compute_krippendorffs_alpha(matrix)

        # Pairwise Cohen's kappa
        pairwise = {}
        for i in range(len(annotator_records)):
            for j in range(i + 1, len(annotator_records)):
                a1 = annotator_records[i]["annotator_id"]
                a2 = annotator_records[j]["annotator_id"]
                l1 = [annotator_records[i]["labels"][k] for k in all_example_ids]
                l2 = [annotator_records[j]["labels"][k] for k in all_example_ids]
                k_val = compute_cohens_kappa(l1, l2)
                pairwise[f"{a1}_vs_{a2}"] = k_val

        # Compute per-attribute kappa if attribute labels are provided
        attr_kappas = {}
        attributes = ["role", "qualifier", "scope", "certainty", "impact", "quantity"]
        for attr in attributes:
            has_attr = all(
                "attribute_labels" in r and attr in r.get("attribute_labels", {}).get(ex_id, {})
                for r in annotator_records for ex_id in all_example_ids
            )
            if has_attr:
                attr_matrix = []
                direction_cats = ["-1", "0", "1"]
                dir_map = {"-1": 0, "0": 1, "1": 2}
                for ex_id in all_example_ids:
                    a_row = [0, 0, 0]
                    for r in annotator_records:
                        val = str(r["attribute_labels"][ex_id][attr])
                        if val in dir_map:
                            a_row[dir_map[val]] += 1
                    attr_matrix.append(a_row)
                attr_kappas[attr] = compute_fleiss_kappa(attr_matrix)
            else:
                attr_kappas[attr] = None

        # Disagreement count (items where not all annotators agree)
        disagreements = sum(1 for row in matrix if max(row) < len(annotator_records))

        return IAAMetricsReport(
            total_examples_evaluated=len(all_example_ids),
            num_annotators=len(annotator_records),
            overall_fleiss_kappa=overall_kappa,
            overall_krippendorff_alpha=overall_alpha,
            attribute_kappas=attr_kappas,
            pairwise_cohen_kappas=pairwise,
            disagreements_count=disagreements,
            adjudicated_count=0,
            status="EVALUATED_LIVE_RECORDS"
        )
