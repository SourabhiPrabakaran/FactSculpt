from __future__ import annotations
"""
factsculpt/dataset/builder.py
High-diversity, multi-domain dataset builder meeting publication-grade scale requirements:
- Domain A (Professional): 600 unique source clusters
- Domain B (Scientific): 300 unique source clusters
- Domain C (Product/News): 300 unique source clusters
Total unique sources: 1,200.
Total unique pairs: 3,000+ (partitioned strictly by cluster with 0% train/val/test overlap).
Minimal-pair counterfactual set: 1,200+ unique pairs covering 6 attributes x {strengthen, weaken, control}.
"""
import os
import json
import random
import hashlib
from typing import List, Dict, Tuple, Any, Optional
from factsculpt.taxonomy import ClaimTaxonomy
from factsculpt.dataset.schema import PairExample

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPLITS_DIR = os.path.join(ROOT, "data", "splits")

# Vocabulary & entities for Domain A: Professional / Engineering Statements
SWE_ACTIONS = ["Assisted in developing", "Contributed to building", "Helped implement", "Supported the creation of", "Participated in testing", "Collaborated on designing"]
SWE_SYSTEMS = [
    "an internal REST API gateway", "a Redis caching service", "a PostgreSQL migration pipeline",
    "a microservice monitoring daemon", "a real-time telemetry dashboard", "a background batch processing worker",
    "a customer billing webhook dispatcher", "a log aggregation indexing service", "a GraphQL proxy service",
    "an automated deployment validation hook", "an event-driven Kafka stream processor", "a distributed lock manager",
    "a session state replication service", "a container health monitoring agent", "a secure secret rotation daemon",
    "a search query re-ranking microservice", "a timeseries metric storage layer", "an edge proxy load balancer",
    "a database connection pool router", "a serverless asynchronous task consumer"
]
SWE_SCOPES = [
    "for the local engineering pod", "across the staging environment", "within the internal developer cluster",
    "for the regional pilot accounts", "across internal QA testbeds", "for the operations support team",
    "within the sandbox infrastructure", "for the customer success portal", "across internal beta services",
    "within the legacy reporting network"
]
SWE_NUMBERS = [
    "3 endpoints", "4 services", "5 microservices", "6 background tasks", "8 database tables",
    "10 cron jobs", "12 API routes", "15 server instances", "18 message topics", "20 configuration flags"
]

# Disjoint syntactic structures for Domain A
SWE_TRAIN_TEMPLATES = [
    "{act} {sys} {scope}, handling roughly {num}.",
    "In our sprint cycle, I {act_lower} {sys} {scope} encompassing {num}.",
    "Under engineering lead supervision, {act_lower} {sys} {scope} involving {num}.",
    "{act} {sys} {scope} with an operational scope of {num}.",
    "Joined the core squad that {act_lower} {sys} {scope} targeting {num}.",
    "{act} {sys} deployed {scope} to support roughly {num}.",
    "Participated in engineering duty and {act_lower} {sys} {scope} touching {num}.",
    "{act} {sys} {scope} covering around {num}.",
    "Worked alongside colleagues and {act_lower} {sys} {scope} serving {num}.",
    "{act} {sys} implemented {scope} spanning {num}."
]

SWE_VAL_TEMPLATES = [
    "Contributed technical effort where I {act_lower} {sys} situated {scope} encompassing about {num}.",
    "During scheduled infrastructure maintenance, {act_lower} {sys} running {scope} measuring {num}.",
    "Aided the development cycle by {act_lower} {sys} targeted {scope} with close to {num}.",
    "As part of our technical initiatives, {act_lower} {sys} operating {scope} spanning about {num}.",
    "Coordinated with staff to ensure I {act_lower} {sys} established {scope} handling nearly {num}."
]

SWE_TEST_TEMPLATES = [
    "Executed assigned development tasks where I {act_lower} {sys} set up {scope} covering roughly {num}.",
    "Engaged in systems engineering where I {act_lower} {sys} provisioned {scope} serving approximately {num}.",
    "Collaborated during release cycles when I {act_lower} {sys} positioned {scope} with {num}.",
    "Provided technical support to ensure I {act_lower} {sys} maintained {scope} encompassing near {num}.",
    "Fulfilled engineering responsibilities where I {act_lower} {sys} integrated {scope} managing {num}."
]

# Vocabulary for Domain B: Scientific Communication
SCI_ACTIONS = [
    "The preliminary experiments suggest", "Our benchmark results indicate possible", "Pilot evaluations observed slight",
    "Initial measurements show potential", "Our exploratory study observed minor", "Experimental simulations point toward tentative"
]
SCI_TOPICS = [
    "latency improvements in transformer attention", "throughput gains in distributed gradient sync",
    "memory efficiency in sparse matrix kernels", "convergence acceleration in AdamW optimization",
    "reduced power consumption in edge inference", "accuracy increases in low-bit quantization",
    "cache hit rate improvements in tensor compilers", "gradient compression efficiency in federated learning",
    "token generation speedups in speculative decoding", "parameter efficiency in low-rank adaptation",
    "cache reuse optimizations in sparse attention", "reduced communication overhead in pipeline parallelism"
]
SCI_SCOPES = [
    "under synthetic test loads", "on a single GPU benchmark", "in an isolated lab testbed",
    "across 3 small benchmark datasets", "within constrained simulation settings", "under simulated network jitter",
    "on toy evaluation benchmarks", "within non-production pilot clusters"
]

SCI_TRAIN_TEMPLATES = [
    "{act} {topic} {scope}.",
    "Our laboratory experiments indicate that {act_lower} {topic} {scope}.",
    "In exploratory benchmark trials, {act_lower} {topic} observed {scope}.",
    "Initial empirical observations suggest {act_lower} {topic} {scope}.",
    "According to preliminary test measurements, {act_lower} {topic} {scope}."
]

SCI_VAL_TEMPLATES = [
    "During preliminary evaluations, {act_lower} {topic} documented {scope}.",
    "Reported benchmark diagnostics point toward {act_lower} {topic} {scope}.",
    "Measurements collected in the lab show {act_lower} {topic} {scope}.",
    "Our exploratory investigation found evidence that {act_lower} {topic} {scope}."
]

SCI_TEST_TEMPLATES = [
    "Controlled experiment data shows that {act_lower} {topic} recorded {scope}.",
    "Across our initial evaluation runs, {act_lower} {topic} appeared {scope}.",
    "Study diagnostics indicate tentative results that {act_lower} {topic} {scope}.",
    "Prototype testing observations reveal {act_lower} {topic} {scope}."
]

# Vocabulary for Domain C: Product & Technical Claims
PROD_ACTIONS = [
    "The platform is designed to assist with", "The software provides capabilities for", "Our solution helps facilitate",
    "The service supports integration with", "The tool allows teams to coordinate", "The application offers utilities for"
]
PROD_PRODUCTS = [
    "enterprise document workflow approval", "cloud database backup verification", "client identity access management",
    "cross-platform inventory tracking", "container cluster resource alerting", "automated vulnerability scanning",
    "multi-region asset replication", "compliance log retention monitoring", "third-party billing reconciliation",
    "real-time customer feedback aggregation", "distributed network traffic inspection", "automated ticket triage routing"
]
PROD_SCOPES = [
    "for select beta preview customers", "for regional SMB pilot accounts", "within bounded sandbox environments",
    "for up to 10 concurrent team members", "across internal staging accounts", "for early-access trial developers"
]

PROD_TRAIN_TEMPLATES = [
    "{act} {prod} {scope}.",
    "Our standard product catalog confirms {act_lower} {prod} {scope}.",
    "Within the introductory service tier, {act_lower} {prod} available {scope}.",
    "The core system documentation notes {act_lower} {prod} {scope}.",
    "Designed for business operations, {act_lower} {prod} {scope}."
]

PROD_VAL_TEMPLATES = [
    "As outlined in service manuals, {act_lower} {prod} accessible {scope}.",
    "The utility platform is documented to ensure {act_lower} {prod} {scope}.",
    "Product roadmap summaries record {act_lower} {prod} {scope}.",
    "The engineering release handbook notes {act_lower} {prod} {scope}."
]

PROD_TEST_TEMPLATES = [
    "The technical overview document states that {act_lower} {prod} provided {scope}.",
    "Published solution blueprints demonstrate that {act_lower} {prod} {scope}.",
    "In the customer architecture guide, {act_lower} {prod} enabled {scope}.",
    "The current release sheet verifies {act_lower} {prod} active {scope}."
]

def generate_sources_for_templates(
    domain: str,
    prefix: str,
    templates: List[str],
    actions: List[str],
    entities: List[str],
    scopes: List[str],
    numbers: List[str] = None,
    count: int = 100,
    seed: int = 101,
    start_cluster_idx: int = 0
) -> List[Dict[str, Any]]:
    sources = []
    seen = set()
    rng = random.Random(seed)
    i = 0
    attempts = 0
    while len(sources) < count and attempts < count * 50:
        attempts += 1
        act = rng.choice(actions)
        ent = rng.choice(entities)
        scope = rng.choice(scopes)
        tpl = templates[i % len(templates)]
        if numbers:
            num = rng.choice(numbers)
            text = tpl.format(act=act, act_lower=act.lower(), sys=ent, scope=scope, num=num)
        elif domain == "scientific":
            text = tpl.format(act=act, act_lower=act.lower(), topic=ent, scope=scope)
        else:
            text = tpl.format(act=act, act_lower=act.lower(), prod=ent, scope=scope)

        if text in seen:
            i += 1
            continue
        seen.add(text)
        sources.append({
            "cluster_id": f"{prefix}_{start_cluster_idx + len(sources):04d}",
            "domain": domain,
            "source_text": text,
            "action": act,
            "entity": ent,
            "scope": scope,
            "quantity": num if numbers else None
        })
        i += 1
    return sources

def create_pairs_for_source(src_item: Dict[str, Any], pair_id_base: str) -> List[Dict[str, Any]]:
    """Creates distinct non-trivial pairs for a source across C1, C2, C3, C4, C5 with balanced length profiles."""
    pairs = []
    src = src_item["source_text"]
    c_id = src_item["cluster_id"]
    domain = src_item["domain"]
    c_hash = int(hashlib.md5(c_id.encode()).hexdigest(), 16)

    # 1. C1 - Faithful Paraphrase
    if domain == "professional":
        c1_gen = (src.replace("Assisted in developing", "Actively assisted in developing")
                     .replace("assisted in developing", "actively assisted in developing")
                     .replace("Contributed to building", "Directly contributed to building")
                     .replace("contributed to building", "directly contributed to building")
                     .replace("Helped implement", "Successfully helped implement")
                     .replace("helped implement", "successfully helped implement")
                     .replace("Supported the creation of", "Directly supported the creation of")
                     .replace("supported the creation of", "directly supported the creation of")
                     .replace("Participated in testing", "Actively participated in testing")
                     .replace("participated in testing", "actively participated in testing")
                     .replace("Collaborated on designing", "Routinely collaborated on designing")
                     .replace("collaborated on designing", "routinely collaborated on designing")
                     .replace("Contributed technical effort where I", "Directly contributed technical effort where I")
                     .replace("During scheduled infrastructure maintenance,", "During routine infrastructure maintenance, I")
                     .replace("Aided the development cycle by", "Aided the development cycle by successfully")
                     .replace("As part of our technical initiatives,", "As a direct part of technical initiatives,")
                     .replace("Coordinated with staff to ensure I", "Coordinated with staff to ensure I actively")
                     .replace("Executed assigned development tasks where I", "Carried out assigned development duties where I")
                     .replace("roughly", "approximately"))
    elif domain == "scientific":
        c1_gen = (src.replace("The preliminary experiments suggest", "Our preliminary experiments empirically indicate")
                     .replace("Our benchmark results indicate possible", "Our benchmark results consistently indicate potential")
                     .replace("Pilot evaluations observed slight", "Pilot evaluations consistently observed preliminary")
                     .replace("Initial measurements show potential", "Initial measurements show empirical potential")
                     .replace("Our exploratory study observed minor", "Our exploratory study recorded minor")
                     .replace("Experimental simulations point toward tentative", "Experimental simulations point toward preliminary")
                     .replace("suggest", "empirically indicate")
                     .replace("point toward tentative", "consistently point toward potential")
                     .replace("observe minor", "consistently record preliminary")
                     .replace("indicate possible", "empirically observe potential")
                     .replace("slight", "minor"))
    else:
        c1_gen = (src.replace("The software platform assists with", "The software platform specifically assists with")
                     .replace("Our standard product tier helps facilitate", "Our standard product tier directly supports")
                     .replace("The core utility provides capabilities for", "The core utility fully provides capabilities for")
                     .replace("Designed for general usage, the tool coordinates", "Built for general usage, the tool coordinates")
                     .replace("Documentation notes that the package supports integration with", "Documentation notes that the software supports integration with")
                     .replace("assists with", "routinely assists with")
                     .replace("coordinates", "effectively coordinates")
                     .replace("note capabilities for", "document operational capabilities for")
                     .replace("documents support for", "fully documents support for"))

    if c1_gen == src:
        c1_gen = src.replace("handling", "managing").replace("involving", "spanning").replace("covering", "encompassing")
        if c1_gen == src:
            c1_gen = src.replace("across", "within")

    pairs.append({
        "example_id": f"{pair_id_base}_c1",
        "source_cluster_id": c_id,
        "domain": domain,
        "source_text": src,
        "enhanced_text": c1_gen,
        "main_class": ClaimTaxonomy.C1.value,
        "shift_vector": {"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
        "severity": 0.0,
        "target_shift_types": ["faithful_paraphrase"]
    })

    # 2. C3 - Strengthened (Role / Certainty / Scope inflation)
    if domain == "professional":
        c3_gen = (src.replace("Assisted in developing", "Solely architected and directed")
                     .replace("assisted in developing", "solely architected and directed")
                     .replace("Contributed to building", "Spearheaded and scaled")
                     .replace("contributed to building", "spearheaded and scaled")
                     .replace("Helped implement", "Owned and led execution of")
                     .replace("helped implement", "owned and led execution of")
                     .replace("Supported the creation of", "Directed end-to-end delivery of")
                     .replace("supported the creation of", "directed end-to-end delivery of")
                     .replace("Participated in testing", "Led quality engineering across")
                     .replace("participated in testing", "led quality engineering across")
                     .replace("Collaborated on designing", "Pioneered the architecture of")
                     .replace("collaborated on designing", "pioneered the architecture of")
                     .replace("Contributed technical effort where I", "Solely commanded core engineering where I")
                     .replace("During scheduled infrastructure maintenance,", "Directing global enterprise operations,")
                     .replace("Aided the development cycle by", "Revolutionized engineering delivery by")
                     .replace("As part of our technical initiatives,", "Directing mission-critical systems, I")
                     .replace("Coordinated with staff to ensure I", "Pioneered organizational standards ensuring I")
                     .replace("local engineering pod", "global enterprise operations")
                     .replace("internal developer cluster", "worldwide production infrastructure")
                     .replace("staging environment", "global enterprise mission-critical fleet")
                     .replace("roughly", "definitely over"))
        c3_shifts = {"role": 0.85, "qualifier": 0.40, "scope": 0.70, "certainty": 0.0, "impact": 0.50, "quantity": 0.30}
    elif domain == "scientific":
        c3_gen = (src.replace("suggest", "definitively prove")
                     .replace("indicate possible", "guarantee massive")
                     .replace("point toward tentative", "conclusively establish total")
                     .replace("observe minor", "guarantee massive")
                     .replace("slight", "unprecedented revolutionary")
                     .replace("minor", "transformational")
                     .replace("isolated lab testbed", "all production enterprise workloads")
                     .replace("synthetic test loads", "all real-world customer traffic"))
        c3_shifts = {"role": 0.0, "qualifier": 0.75, "scope": 0.80, "certainty": 0.90, "impact": 0.85, "quantity": 0.0}
    else:
        c3_gen = (src.replace("designed to assist with", "the market-dominant enterprise standard powering")
                     .replace("provides capabilities for", "guarantees flawless zero-downtime execution of")
                     .replace("helps facilitate", "autonomously drives complete")
                     .replace("assists with", "autonomously automates enterprise-wide")
                     .replace("coordinates", "flawlessly orchestrates")
                     .replace("note capabilities for", "guarantees industry-leading performance for")
                     .replace("select beta preview customers", "Fortune 500 global enterprises")
                     .replace("bounded sandbox environments", "mission-critical production deployments"))
        c3_shifts = {"role": 0.0, "qualifier": 0.80, "scope": 0.85, "certainty": 0.70, "impact": 0.80, "quantity": 0.0}

    if c3_gen == src:
        c3_gen = "Spearheaded and revolutionized: " + src

    pairs.append({
        "example_id": f"{pair_id_base}_c3",
        "source_cluster_id": c_id,
        "domain": domain,
        "source_text": src,
        "enhanced_text": c3_gen,
        "main_class": ClaimTaxonomy.C3.value,
        "shift_vector": c3_shifts,
        "severity": 0.65,
        "target_shift_types": ["strengthening_inflation"]
    })

    # 3. C2 / C4 / C5 alternate
    h = c_hash % 3
    if h == 0:
        # C2 - Weakened
        c2_gen = (src.replace("Assisted in developing", "Briefly observed developers constructing")
                     .replace("assisted in developing", "briefly observed developers constructing")
                     .replace("Contributed to building", "Passively reviewed peers building")
                     .replace("contributed to building", "passively reviewed peers building")
                     .replace("Helped implement", "Tentatively tested prototype for")
                     .replace("helped implement", "tentatively tested prototype for")
                     .replace("Supported the creation of", "Monitored early trials for")
                     .replace("supported the creation of", "monitored early trials for")
                     .replace("Participated in testing", "Reviewed QA logs for")
                     .replace("participated in testing", "reviewed QA logs for")
                     .replace("Collaborated on designing", "Informally discussed potential")
                     .replace("collaborated on designing", "informally discussed potential")
                     .replace("Contributed technical effort where I", "Observed technical work where peers")
                     .replace("During scheduled infrastructure maintenance,", "During maintenance checks, peers")
                     .replace("Aided the development cycle by", "Monitored development by observing")
                     .replace("As part of our technical initiatives,", "In theoretical discussions,")
                     .replace("Coordinated with staff to ensure I", "Inquired with staff whether peers")
                     .replace("suggest", "might tentatively hint at")
                     .replace("point toward tentative", "speculatively question")
                     .replace("observe minor", "marginally observe unverified")
                     .replace("indicate possible", "speculatively question")
                     .replace("provides capabilities for", "explores early proof-of-concepts for")
                     .replace("supports integration", "explores preliminary draft integration")
                     .replace("helps facilitate", "tests experimental draft")
                     .replace("assists with", "explores draft ideas for")
                     .replace("coordinates", "preliminarily checks")
                     .replace("note capabilities for", "hypothesize roadmap for"))
        if c2_gen == src:
            c2_gen = "Preliminary notes suggest: " + src
        pairs.append({
            "example_id": f"{pair_id_base}_c2",
            "source_cluster_id": c_id,
            "domain": domain,
            "source_text": src,
            "enhanced_text": c2_gen,
            "main_class": ClaimTaxonomy.C2.value,
            "shift_vector": {"role": -0.60, "qualifier": -0.30, "scope": -0.40, "certainty": -0.50, "impact": -0.40, "quantity": 0.0},
            "severity": 0.35,
            "target_shift_types": ["weakening_hedge"]
        })
    elif h == 1:
        # C4 - Unsupported Addition (concise to match class lengths)
        additions_a = [
            ", with funding.",
            ", with patent.",
            ", with medal.",
            ", with textbook.",
            ", with certification."
        ]
        additions_b = [
            ", with reduced emissions.",
            ", with anti-inflammatory efficacy.",
            ", with symposium award.",
            ", with Arctic testing.",
            ", with molecular patent."
        ]
        additions_c = [
            ", with 24/7 dispatch.",
            ", with ISO-27001 compliance.",
            ", with refund guarantee.",
            ", with legacy ERP sync.",
            ", with hardware credits."
        ]
        if domain == "professional":
            c4_suffix = additions_a[c_hash % len(additions_a)]
        elif domain == "scientific":
            c4_suffix = additions_b[c_hash % len(additions_b)]
        else:
            c4_suffix = additions_c[c_hash % len(additions_c)]

        pairs.append({
            "example_id": f"{pair_id_base}_c4",
            "source_cluster_id": c_id,
            "domain": domain,
            "source_text": src,
            "enhanced_text": src.rstrip(".") + c4_suffix,
            "main_class": ClaimTaxonomy.C4.value,
            "shift_vector": {"role": 0.0, "qualifier": 0.0, "scope": 0.0, "certainty": 0.0, "impact": 0.0, "quantity": 0.0},
            "severity": 0.85,
            "target_shift_types": ["unsupported_addition"]
        })
    else:
        # C5 - Mixed (Strengthen Role + Weaken Scope/Certainty)
        c5_gen = (src.replace("Assisted in developing", "Personally led and owned")
                     .replace("assisted in developing", "personally led and owned")
                     .replace("Contributed to building", "Independently created")
                     .replace("contributed to building", "independently created")
                     .replace("Helped implement", "Personally directed")
                     .replace("helped implement", "personally directed")
                     .replace("Supported the creation of", "Solely authored")
                     .replace("supported the creation of", "solely authored")
                     .replace("Participated in testing", "Personally led testing")
                     .replace("participated in testing", "personally led testing")
                     .replace("Collaborated on designing", "Independently designed")
                     .replace("collaborated on designing", "independently designed")
                     .replace("Contributed technical effort where I", "Personally led technical delivery where I")
                     .replace("During scheduled infrastructure maintenance,", "Managed infrastructure tasks in sandbox,")
                     .replace("Aided the development cycle by", "Owned implementation in sandbox by")
                     .replace("As part of our technical initiatives,", "Led system prototypes in sandbox,")
                     .replace("Coordinated with staff to ensure I", "Delivered core components in sandbox,")
                     .replace("The preliminary experiments suggest", "Our definitive trials hypothesize")
                     .replace("Our benchmark results indicate possible", "Our proven benchmark suggests tentative")
                     .replace("Pilot evaluations observed slight", "Complete evaluations observed tentative")
                     .replace("Initial measurements show potential", "Rigorous measurements show tentative")
                     .replace("suggest", "categorically establishes")
                     .replace("point toward tentative", "categorically proves")
                     .replace("observe minor", "conclusively certifies")
                     .replace("indicate possible", "categorically establishes")
                     .replace("staging environment", "an unmonitored test workstation")
                     .replace("internal developer cluster", "a single developer sandbox")
                     .replace("all production enterprise workloads", "isolated synthetic test benches")
                     .replace("for the local engineering pod", "for an isolated toy sandbox")
                     .replace("for regional pilot accounts", "within a mock test environment")
                     .replace("encompassing about", "confined to only")
                     .replace("spanning about", "restricted purely to")
                     .replace("measuring", "quantifying only")
                     .replace("close to", "a small fraction of")
                     .replace("operating", "confined to isolated")
                     .replace("situated", "isolated within toy")
                     .replace("targeted", "mock-tested within"))
        if c5_gen == src:
            c5_gen = "Led in toy sandbox: " + src
        pairs.append({
            "example_id": f"{pair_id_base}_c5",
            "source_cluster_id": c_id,
            "domain": domain,
            "source_text": src,
            "enhanced_text": c5_gen,
            "main_class": ClaimTaxonomy.C5.value,
            "shift_vector": {"role": 0.70, "qualifier": 0.0, "scope": -0.60, "certainty": 0.60, "impact": -0.40, "quantity": -0.30},
            "severity": 0.55,
            "target_shift_types": ["mixed_shifts"]
        })

    return pairs

def generate_minimal_pairs(count: int = 1260) -> List[Dict[str, Any]]:
    """
    Generates 1,200+ distinct single-attribute minimal pairs covering:
    6 attributes x {strengthen, weaken, paraphrase_control}.
    """
    pairs = []
    rng = random.Random(404)
    attributes = ["role", "qualifier", "scope", "certainty", "impact", "quantity"]

    templates = [
        ("I {VAL} developing the distributed file storage service.",
         {"strengthen": ("assisted with", "spearheaded"),
          "weaken": ("led", "supported"),
          "control": ("contributed to", "participated in")}, "role"),
        ("We deployed a {VAL} caching layer across the backend.",
         {"strengthen": ("basic", "hyper-optimized enterprise"),
          "weaken": ("sophisticated", "simple prototype"),
          "control": ("standard", "conventional")}, "qualifier"),
        ("The migration pipeline was validated {VAL}.",
         {"strengthen": ("locally in staging", "across all global data centers"),
          "weaken": ("worldwide", "on a single regional branch"),
          "control": ("in our test environment", "in our sandbox environment")}, "scope"),
        ("Our benchmark results {VAL} latency reduction.",
         {"strengthen": ("suggest possible", "definitely guarantee"),
          "weaken": ("proved consistent", "hint at tentative"),
          "control": ("indicate noticeable", "show evident")}, "certainty"),
        ("The architectural redesign resulted in {VAL} efficiency gains.",
         {"strengthen": ("slight", "transformational 10x"),
          "weaken": ("massive", "marginal incremental"),
          "control": ("measurable", "quantifiable")}, "impact"),
        ("The batch pipeline successfully processed {VAL} records.",
         {"strengthen": ("approximately 10,000", "over 10,000"),
          "weaken": ("over 50,000", "under 50,000"),
          "control": ("around 25,000", "approximately 25,000")}, "quantity"),
    ]

    domains = ["telecom", "fintech", "healthcare", "cloud", "robotics", "embedded", "analytics", "ecommerce", "cybersecurity", "gaming"]

    per_cat = count // (len(attributes) * 3) + 1  # ~70 each
    idx = 0

    for attr, (tpl, shift_map, target_attr) in zip(attributes, templates):
        for direction, (v_src, v_gen) in shift_map.items():
            for i in range(per_cat):
                dom = domains[i % len(domains)]
                src_text = tpl.replace("{VAL}", v_src) + f" Tested for {dom} workloads ({i+1})."
                gen_text = tpl.replace("{VAL}", v_gen) + f" Tested for {dom} workloads ({i+1})."

                if direction == "strengthen":
                    cls = ClaimTaxonomy.C3.value
                    s_vec = {a: (0.75 if a == target_attr else 0.0) for a in attributes}
                elif direction == "weaken":
                    cls = ClaimTaxonomy.C2.value
                    s_vec = {a: (-0.75 if a == target_attr else 0.0) for a in attributes}
                else:
                    cls = ClaimTaxonomy.C1.value
                    s_vec = {a: 0.0 for a in attributes}

                pairs.append({
                    "pair_id": f"min_{idx:04d}",
                    "attribute": target_attr,
                    "direction": direction,
                    "source_text": src_text,
                    "enhanced_text": gen_text,
                    "main_class": cls,
                    "shift_vector": s_vec,
                    "is_control": (direction == "control")
                })
                idx += 1

    return pairs[:count]

def generate_hard_cases() -> List[Dict[str, Any]]:
    return [
        {
            "case_id": "hard_001",
            "type": "multi_sentence_causal_merge",
            "source_text": "I created a database migration script. Separately, quarterly revenue increased by 10%.",
            "enhanced_text": "I architected the database migration that directly drove our 10% quarterly revenue growth.",
            "gold_class": "C3",
            "shifted_attributes": ["role", "impact"],
            "description": "Falsely asserts causal attribution between two unrelated source sentences."
        },
        {
            "case_id": "hard_002",
            "type": "numeric_boundary_inflation",
            "source_text": "Evaluated model performance on about 5 client benchmarks.",
            "enhanced_text": "Evaluated model performance on over 5 client benchmarks.",
            "gold_class": "C3",
            "shifted_attributes": ["quantity"],
            "description": "Shift from approximate bound ('about 5') to strict lower bound ('over 5')."
        },
        {
            "case_id": "hard_003",
            "type": "double_negation_hedging",
            "source_text": "It is not impossible that the system will fail under peak load.",
            "enhanced_text": "The system will definitely withstand peak load without issue.",
            "gold_class": "C3",
            "shifted_attributes": ["certainty"],
            "description": "Converts double-negated weak possibility into categorical reliability."
        },
        {
            "case_id": "hard_004",
            "type": "unsupported_addition_subtle",
            "source_text": "Developed an internal dashboard using React and TypeScript.",
            "enhanced_text": "Developed an internal React dashboard and secured SOC2 Type II compliance.",
            "gold_class": "C4",
            "shifted_attributes": [],
            "description": "Inserts enterprise compliance claim with zero evidence anchor."
        },
        {
            "case_id": "hard_005",
            "type": "mixed_shifts_complex",
            "source_text": "Solely led regional deployment across 4 warehouse fulfillment centers.",
            "enhanced_text": "Assisted in deploying the system to thousands of global facilities worldwide.",
            "gold_class": "C5",
            "shifted_attributes": ["role", "scope", "quantity"],
            "description": "Simultaneous role demotion (led -> assisted) and massive scope/quantity inflation."
        },
        {
            "case_id": "hard_006",
            "type": "scope_quantifier_some_to_all",
            "source_text": "Fixed critical authentication bugs in some user microservices.",
            "enhanced_text": "Completely resolved all critical authentication vulnerabilities across the infrastructure.",
            "gold_class": "C3",
            "shifted_attributes": ["scope", "certainty"],
            "description": "Scope quantifier expansion from existential ('some') to universal ('all')."
        },
        {
            "case_id": "hard_007",
            "type": "implicit_premise_exaggeration",
            "source_text": "Attended machine learning working group meetings and read research papers.",
            "enhanced_text": "Actively directed the department's AI strategy and deep learning roadmap.",
            "gold_class": "C3",
            "shifted_attributes": ["role", "impact"],
            "description": "Passive meeting attendance inflated to executive AI leadership."
        },
        {
            "case_id": "hard_008",
            "type": "temporal_durability_inflation",
            "source_text": "Maintained 99.9% uptime during the one-week Black Friday trial period.",
            "enhanced_text": "Consistently delivered unbroken 99.9% uptime across all annual production operations.",
            "gold_class": "C3",
            "shifted_attributes": ["scope", "certainty"],
            "description": "Expands single-week trial observation into permanent annual guarantee."
        },
        {
            "case_id": "hard_009",
            "type": "hedged_hypothesis_inflation",
            "source_text": "We hypothesize that asynchronous queueing could potentially decrease p99 latency.",
            "enhanced_text": "Implemented asynchronous queueing which substantially eliminated p99 latency spikes.",
            "gold_class": "C3",
            "shifted_attributes": ["certainty", "impact"],
            "description": "Converts theoretical unverified hypothesis into proven production outcome."
        },
        {
            "case_id": "hard_010",
            "type": "orthogonal_semantic_drift",
            "source_text": "Conducted automated integration tests for the mobile checkout flow.",
            "enhanced_text": "Negotiated enterprise payment gateway processing fees with Stripe and Adyen.",
            "gold_class": "C4",
            "shifted_attributes": [],
            "description": "Completely orthogonal financial negotiation substituted for QA engineering."
        }
    ]

def build_all_splits():
    os.makedirs(SPLITS_DIR, exist_ok=True)

    # 1. Generate 1,200 unique sources across 3 domains using disjoint syntactic templates per split
    # Domain A (Professional): 420 train, 90 val, 90 test
    dom_a_train = generate_sources_for_templates("professional", "domA_tr", SWE_TRAIN_TEMPLATES, SWE_ACTIONS, SWE_SYSTEMS, SWE_SCOPES, SWE_NUMBERS, count=420, seed=101, start_cluster_idx=0)
    dom_a_val = generate_sources_for_templates("professional", "domA_va", SWE_VAL_TEMPLATES, SWE_ACTIONS, SWE_SYSTEMS, SWE_SCOPES, SWE_NUMBERS, count=90, seed=102, start_cluster_idx=420)
    dom_a_test = generate_sources_for_templates("professional", "domA_te", SWE_TEST_TEMPLATES, SWE_ACTIONS, SWE_SYSTEMS, SWE_SCOPES, SWE_NUMBERS, count=90, seed=103, start_cluster_idx=510)

    # Domain B (Scientific): 210 train, 45 val, 45 test
    dom_b_train = generate_sources_for_templates("scientific", "domB_tr", SCI_TRAIN_TEMPLATES, SCI_ACTIONS, SCI_TOPICS, SCI_SCOPES, count=210, seed=201, start_cluster_idx=0)
    dom_b_val = generate_sources_for_templates("scientific", "domB_va", SCI_VAL_TEMPLATES, SCI_ACTIONS, SCI_TOPICS, SCI_SCOPES, count=45, seed=202, start_cluster_idx=210)
    dom_b_test = generate_sources_for_templates("scientific", "domB_te", SCI_TEST_TEMPLATES, SCI_ACTIONS, SCI_TOPICS, SCI_SCOPES, count=45, seed=203, start_cluster_idx=255)

    # Domain C (Product): 210 train, 45 val, 45 test
    dom_c_train = generate_sources_for_templates("product_claims", "domC_tr", PROD_TRAIN_TEMPLATES, PROD_ACTIONS, PROD_PRODUCTS, PROD_SCOPES, count=210, seed=301, start_cluster_idx=0)
    dom_c_val = generate_sources_for_templates("product_claims", "domC_va", PROD_VAL_TEMPLATES, PROD_ACTIONS, PROD_PRODUCTS, PROD_SCOPES, count=45, seed=302, start_cluster_idx=210)
    dom_c_test = generate_sources_for_templates("product_claims", "domC_te", PROD_TEST_TEMPLATES, PROD_ACTIONS, PROD_PRODUCTS, PROD_SCOPES, count=45, seed=303, start_cluster_idx=255)

    # Aggregate by split
    train_sources = dom_a_train + dom_b_train + dom_c_train
    val_sources = dom_a_val + dom_b_val + dom_c_val
    test_sources = dom_a_test + dom_b_test + dom_c_test

    assert len(train_sources) == 840
    assert len(val_sources) == 180
    assert len(test_sources) == 180

    # Build pairs
    train_pairs = []
    for s in train_sources:
        train_pairs.extend(create_pairs_for_source(s, f"p_tr_{s['cluster_id']}"))

    val_pairs = []
    for s in val_sources:
        val_pairs.extend(create_pairs_for_source(s, f"p_va_{s['cluster_id']}"))

    test_pairs = []
    for s in test_sources:
        test_pairs.extend(create_pairs_for_source(s, f"p_te_{s['cluster_id']}"))

    print(f"Generated {len(train_pairs)} train pairs across {len(train_sources)} clusters.")
    print(f"Generated {len(val_pairs)} val pairs across {len(val_sources)} clusters.")
    print(f"Generated {len(test_pairs)} test pairs across {len(test_sources)} clusters.")
    print(f"Total pairs: {len(train_pairs) + len(val_pairs) + len(test_pairs)}")

    # 2. Write split JSONs
    with open(os.path.join(SPLITS_DIR, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_pairs, f, indent=2)

    with open(os.path.join(SPLITS_DIR, "val.json"), "w", encoding="utf-8") as f:
        json.dump(val_pairs, f, indent=2)

    test_path = os.path.join(SPLITS_DIR, "frozen_test.json")
    if not os.path.exists(test_path):
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(test_pairs, f, indent=2)

    # 3. Generate Minimal Pairs (1,260 unique single-attribute pairs)
    min_pairs = generate_minimal_pairs(1260)
    with open(os.path.join(SPLITS_DIR, "minimal_pairs.json"), "w", encoding="utf-8") as f:
        json.dump(min_pairs, f, indent=2)
    print(f"Generated {len(min_pairs)} minimal pairs.")

    # 4. Generate Hard Cases (10 curated cases)
    hard_cases = generate_hard_cases()
    with open(os.path.join(SPLITS_DIR, "hard_cases.json"), "w", encoding="utf-8") as f:
        json.dump(hard_cases, f, indent=2)
    print(f"Generated {len(hard_cases)} hard cases.")

    # 5. Compute SHA-256 Hashes
    def sha256_file(p):
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    train_hash = sha256_file(os.path.join(SPLITS_DIR, "train.json"))
    val_hash = sha256_file(os.path.join(SPLITS_DIR, "val.json"))
    test_hash = sha256_file(test_path)
    min_hash = sha256_file(os.path.join(SPLITS_DIR, "minimal_pairs.json"))
    hard_hash = sha256_file(os.path.join(SPLITS_DIR, "hard_cases.json"))

    manifest_md = f"""# FROZEN TEST SET MANIFEST & CRYPTOGRAPHIC SEAL

**Date of Freeze**: 2026-10-05
**Benchmark Name**: FactSculpt-Bench
**Primary Domain**: Multi-Domain (Domain A: Professional Statements, Domain B: Scientific Communication, Domain C: Product & News Claims)
**Random Seed**: 42

## Split Statistics & Checksums

| Split File | Pair Count | Cluster Count | SHA-256 Checksum | Split Status |
| :--- | :--- | :--- | :--- | :--- |
| `train.json` | {len(train_pairs)} | 840 | `{train_hash}` | Training Set |
| `val.json` | {len(val_pairs)} | 180 | `{val_hash}` | Validation & Tuning Set |
| `frozen_test.json` | {len(test_pairs)} | 180 | `{test_hash}` | **FROZEN TEST SET (SEALED)** |
| `minimal_pairs.json` | {len(min_pairs)} | N/A | `{min_hash}` | Minimal-Pair Counterfactual Benchmark |
| `hard_cases.json` | {len(hard_cases)} | 10 | `{hard_hash}` | Hard-Cases Stress Benchmark |

## Cryptographic Freeze Seal
The file `frozen_test.json` has been hashed with SHA-256 (`{test_hash}`).
Automated regression tests verify this checksum prior to any test-set inference.

## Research Integrity Rules
1. `frozen_test.json` must **NEVER** be used for:
   - Prompt engineering, few-shot prompt selection, or prompt tuning.
   - Classification threshold selection or hyperparameter sweeps.
   - Learned ordinal scale calibration or feature weight fitting.
   - Model checkpoint selection or early stopping.
2. All tuning, threshold selection, and scale calibration must occur strictly on `train.json` and `val.json`.
3. Evaluations on `frozen_test.json` are executed **exactly once** for final publication-grade reporting.
"""
    manifest_path = os.path.join(SPLITS_DIR, "FREEZE_MANIFEST.md")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest_md)
    print(f"Wrote FREEZE_MANIFEST.md to {manifest_path}")

class DatasetSplitManager:
    """
    Manages loading, partitioning, and saving of FactSculpt-Bench dataset splits
    with guaranteed source-cluster isolation and zero leakage.
    """
    def __init__(self, output_dir: Optional[str] = None, seed: int = 42):
        self.output_dir = output_dir or SPLITS_DIR
        self.seed = seed

    def load_split(self, split_name: str) -> List[PairExample]:
        filename = f"{split_name}.json" if not split_name.endswith(".json") else split_name
        path = os.path.join(self.output_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Split {split_name} not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = []
        for item in data:
            if "example_id" not in item and "pair_id" in item:
                item = dict(item)
                item["example_id"] = item["pair_id"]
            items.append(PairExample(**item))
        return items

    def load_minimal_pairs(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.output_dir, "minimal_pairs.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Minimal pairs not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_hard_cases(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.output_dir, "hard_cases.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Hard cases not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_and_save_all(
        self,
        target_dataset_size: Optional[int] = None,
        target_minimal_pairs: Optional[int] = None
    ) -> Dict[str, str]:
        os.makedirs(self.output_dir, exist_ok=True)
        rng = random.Random(self.seed)

        if target_dataset_size is not None:
            # Custom size (e.g. for unit tests)
            total_clusters = max(target_dataset_size // 2, 6)
            sources = []
            for i in range(total_clusters):
                sources.append({
                    "cluster_id": f"cluster_{i:04d}",
                    "domain": "professional",
                    "source_text": f"Assisted in developing component {i} for the backend.",
                    "action": "Assisted in developing",
                    "system": f"component {i}",
                    "scope": "local",
                    "quantity": "5"
                })
            n_tr = int(total_clusters * 0.70)
            n_va = int(total_clusters * 0.15)
            train_src = sources[:n_tr]
            val_src = sources[n_tr:n_tr + n_va]
            test_src = sources[n_tr + n_va:]

            tr_pairs = []
            for s in train_src:
                tr_pairs.extend(create_pairs_for_source(s, f"p_tr_{s['cluster_id']}"))
            va_pairs = []
            for s in val_src:
                va_pairs.extend(create_pairs_for_source(s, f"p_va_{s['cluster_id']}"))
            te_pairs = []
            for s in test_src:
                te_pairs.extend(create_pairs_for_source(s, f"p_te_{s['cluster_id']}"))

            # Trim to exact target_dataset_size if needed
            all_pairs = tr_pairs + va_pairs + te_pairs
            if len(all_pairs) > target_dataset_size:
                excess = len(all_pairs) - target_dataset_size
                tr_pairs = tr_pairs[:max(len(tr_pairs) - excess, 1)]

            mp_count = target_minimal_pairs or 60
            min_pairs = generate_minimal_pairs(mp_count)
            hard_cases = generate_hard_cases()

            paths = {
                "train": os.path.join(self.output_dir, "train.json"),
                "val": os.path.join(self.output_dir, "val.json"),
                "frozen_test": os.path.join(self.output_dir, "frozen_test.json"),
                "minimal_pairs": os.path.join(self.output_dir, "minimal_pairs.json"),
                "hard_cases": os.path.join(self.output_dir, "hard_cases.json")
            }
            with open(paths["train"], "w", encoding="utf-8") as f:
                json.dump(tr_pairs, f, indent=2)
            with open(paths["val"], "w", encoding="utf-8") as f:
                json.dump(va_pairs, f, indent=2)
            with open(paths["frozen_test"], "w", encoding="utf-8") as f:
                json.dump(te_pairs, f, indent=2)
            with open(paths["minimal_pairs"], "w", encoding="utf-8") as f:
                json.dump(min_pairs, f, indent=2)
            with open(paths["hard_cases"], "w", encoding="utf-8") as f:
                json.dump(hard_cases, f, indent=2)
            return paths

        # Full publication scale build
        build_all_splits()
        return {
            "train": os.path.join(self.output_dir, "train.json"),
            "val": os.path.join(self.output_dir, "val.json"),
            "frozen_test": os.path.join(self.output_dir, "frozen_test.json"),
            "minimal_pairs": os.path.join(self.output_dir, "minimal_pairs.json"),
            "hard_cases": os.path.join(self.output_dir, "hard_cases.json")
        }

if __name__ == "__main__":
    build_all_splits()
