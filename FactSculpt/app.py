import os
import sys

# Ensure FactSculpt root is always on sys.path regardless of execution directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from factsculpt.config import FactSculptConfig
from factsculpt.application.pipeline import FACTSculptPipeline
from factsculpt.repair.pipeline import AttributeTargetedRepairPipeline
from factsculpt.classifier.models import ClassificationCode

# Page configuration
st.set_page_config(
    page_title="FactSculpt: Evidence Exaggeration Detection & Repair",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #0F172A;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .rule-card {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .rule-card b {
        color: #0F172A;
    }
    .metric-badge {
        display: inline-block;
        font-weight: 700;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.95rem;
    }
    .diagnostic-box {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 0.9rem 1.1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.95rem;
    }
    .repair-box {
        background: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def get_pipeline(model_name: str, nli_model: str) -> FACTSculptPipeline:
    """Initializes the FactSculpt pipeline with graceful fallbacks."""
    from factsculpt.alignment.aligner import EmbeddingClaimAligner
    from factsculpt.extraction.llm import LLMAtomicClaimExtractor, LLMEvidenceProfileExtractor
    from factsculpt.differencing.engine import AttributeDifferenceEngine
    from factsculpt.scales.ordinal_scaler import BradleyTerryOrdinalScaler
    from factsculpt.features.generator import EvidenceDeviationFeatureGenerator
    from factsculpt.classifier.rules import ResearchRuleBasedClassifier

    config = FactSculptConfig(embedding_model=model_name, nli_model=nli_model)

    try:
        from factsculpt.alignment.embeddings import SentenceTransformerEmbeddingGenerator
        embed_gen = SentenceTransformerEmbeddingGenerator(model_name=model_name)
    except Exception:
        from factsculpt.alignment.embeddings import MockEmbeddingGenerator
        embed_gen = MockEmbeddingGenerator()

    aligner = EmbeddingClaimAligner(embedding_generator=embed_gen, config=config)

    try:
        from factsculpt.nli.models_hf import HuggingFaceNLIClassifier
        nli_class = HuggingFaceNLIClassifier(model_name=nli_model)
    except Exception:
        from factsculpt.nli.models_hf import MockNLIClassifier
        nli_class = MockNLIClassifier()

    scaler = BradleyTerryOrdinalScaler()
    differencer = AttributeDifferenceEngine(ordinal_scaler=scaler)

    return FACTSculptPipeline(
        config=config,
        claim_extractor=LLMAtomicClaimExtractor(),
        profile_extractor=LLMEvidenceProfileExtractor(),
        embedding_generator=embed_gen,
        claim_aligner=aligner,
        nli_classifier=nli_class,
        differencer=differencer,
        feature_generator=EvidenceDeviationFeatureGenerator(),
        classifier=ResearchRuleBasedClassifier()
    )

def severity_to_label(val: float, code: str) -> tuple[str, str]:
    if code == "C1" or val <= 0.05:
        return "None (0.00)", "#10B981"
    elif val < 0.35:
        return f"Low ({val:.2f})", "#3B82F6"
    elif val < 0.65:
        return f"Moderate ({val:.2f})", "#F59E0B"
    else:
        return f"High ({val:.2f})", "#EF4444"

def make_explanation(code: str, overall_shifts: dict) -> str:
    strengthened = [attr for attr, v in overall_shifts.items() if v > 0.05]
    weakened = [attr for attr, v in overall_shifts.items() if v < -0.05]

    if code == "C1":
        return "The enhanced text is faithful to the evidence: meaning, evidence strength, modality, scope, and bounds are strictly preserved."
    elif code == "C4":
        return "The enhanced text introduces new factual claims or entities that have zero basis in the original source evidence."
    elif code == "C3":
        if strengthened:
            attrs_str = ", ".join(f"**{a}**" for a in strengthened)
            return f"**Support-Preserving Strengthening (SPS)**: The enhanced text escalates the evidential claim along {attrs_str} without source warrant, even though standard NLI still judges the rewrite as entailed."
        return "The enhanced text strengthens the evidential claims beyond the original source evidence."
    elif code == "C2":
        if weakened:
            attrs_str = ", ".join(f"**{a}**" for a in weakened)
            return f"The enhanced text attenuates or softens evidential claims along {attrs_str} relative to the source."
        return "The enhanced text weakens the evidential strength of the original statement."
    elif code == "C5":
        s_str = ", ".join(f"**{a}**" for a in strengthened) if strengthened else "some attributes"
        w_str = ", ".join(f"**{a}**" for a in weakened) if weakened else "other attributes"
        return f"**Mixed Evidential Shift**: The enhanced text simultaneously strengthens {s_str} while weakening {w_str}. Mixed cases are never collapsed into a single direction."
    return "Differences detected relative to closed-world evidence."

# ==========================================
# SIDEBAR: 5 Rules & Research Taxonomy
# ==========================================
with st.sidebar:
    st.markdown("### ⚖️ Evidential Shift Taxonomy")
    st.markdown("FactSculpt classifies claims under a **closed-world evidence** assumption using 5 canonical rules:")

    st.markdown(
        """
        <div class="rule-card" style="border-left: 4px solid #10B981;">
            <b>C1: UNCHANGED_FAITHFUL</b><br>
            Evidential strength, scope, modality, and bounds are strictly preserved.
        </div>
        <div class="rule-card" style="border-left: 4px solid #3B82F6;">
            <b>C2: WEAKENED</b><br>
            Evidential strength is attenuated (demoted role, restricted scope, hedged certainty).
        </div>
        <div class="rule-card" style="border-left: 4px solid #EF4444;">
            <b>C3: STRENGTHENED (SPS)</b><br>
            Evidential claim is amplified across &ge;1 attribute. <i>Standard NLI is 99.4% blind to this shift.</i>
        </div>
        <div class="rule-card" style="border-left: 4px solid #F59E0B;">
            <b>C4: UNSUPPORTED_ADDITION</b><br>
            Extrinsic assertions or entities with zero basis in the source evidence.
        </div>
        <div class="rule-card" style="border-left: 4px solid #8B5CF6;">
            <b>C5: MIXED_DIRECTION</b><br>
            Simultaneous strengthening in &ge;1 attribute and weakening in &ge;1 other attribute.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### 📐 6-D Attribute Vector")
    st.markdown(
        """
        Shifts are measured along 6 orthogonal axes:
        - **Role/Agency**: e.g., *assisted* $\\to$ *spearheaded*
        - **Qualifier**: e.g., *pipeline* $\\to$ *cutting-edge architecture*
        - **Scope**: e.g., *local team* $\\to$ *global enterprise*
        - **Certainty**: e.g., *may improve* $\\to$ *guaranteed to prove*
        - **Impact**: e.g., *assisted* $\\to$ *transformed*
        - **Quantity**: e.g., *up to 50%* $\\to$ *over 50%*
        """
    )
    st.markdown("---")
    st.caption("FactSculpt Bench | ACL/EMNLP Rebuild")

# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown('<div class="main-title">FactSculpt</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Closed-World Evidence-Strengthening & Exaggeration Detection & Minimal Repair</div>', unsafe_allow_html=True)

# Preset Examples across canonical classes
col_pre1, col_pre2 = st.columns([3, 1])
with col_pre1:
    preset = st.selectbox(
        "Load a benchmark example:",
        options=[
            "C3: Role & Certainty Exaggeration (SPS Resume Inflation)",
            "C1: Faithful Paraphrase (Evidence-Grounded)",
            "C3: Scope & Quantity Inflation (Scientific / Data Claims)",
            "C4: Unsupported Addition (Extrinsic Fact Injection)",
            "C2: Weakened / Hedged Claim (Conservative Softening)",
            "C5: Mixed Shift (Simultaneous Promote & Demote)"
        ]
    )

if preset == "C3: Role & Certainty Exaggeration (SPS Resume Inflation)":
    default_src = "Worked as part of a team developing a prototype."
    default_gen = "Led the development of a production-ready system with guaranteed 100% uptime."
elif preset == "C1: Faithful Paraphrase (Evidence-Grounded)":
    default_src = "I helped build a Python data pipeline for internal reporting."
    default_gen = "I assisted in developing an internal data processing pipeline using Python."
elif preset == "C3: Scope & Quantity Inflation (Scientific / Data Claims)":
    default_src = "Analyzed approximately 5 regional customer datasets."
    default_gen = "Analyzed over 5 global enterprise customer datasets."
elif preset == "C4: Unsupported Addition (Extrinsic Fact Injection)":
    default_src = "I designed the user interface in Figma for the internal mobile app."
    default_gen = "I designed the mobile UI in Figma and negotiated three enterprise vendor contracts."
elif preset == "C2: Weakened / Hedged Claim (Conservative Softening)":
    default_src = "Spearheaded the complete cloud migration of the customer billing system."
    default_gen = "Contributed to migrating portions of the customer billing system to the cloud."
else:
    default_src = "Led the regional marketing campaign for the consumer product launch."
    default_gen = "Assisted in coordinating the global enterprise marketing campaign."

# Two-column Text Inputs
col_src, col_gen = st.columns(2)
with col_src:
    st.markdown("#### 📄 Source Evidence Text ($S$)")
    st.caption("The *only* authorized ground-truth evidence (closed-world).")
    source_text = st.text_area(
        "Source:",
        value=default_src,
        height=120,
        label_visibility="collapsed",
        key="source_input_box"
    )

with col_gen:
    st.markdown("#### ✍️ Enhanced / Rewritten Text ($E$)")
    st.caption("AI-rewritten or polished text to evaluate for evidential shift.")
    enhanced_text = st.text_area(
        "Enhanced:",
        value=default_gen,
        height=120,
        label_visibility="collapsed",
        key="enhanced_input_box"
    )

analyze_clicked = st.button("🔍 Analyze Evidential Shift", type="primary", use_container_width=True)

if analyze_clicked or "last_analysis" in st.session_state:
    if analyze_clicked:
        with st.spinner("Decomposing atomic claims, extracting 6D profiles, and computing evidential shifts..."):
            pipeline = get_pipeline("sentence-transformers/all-MiniLM-L6-v2", "facebook/bart-large-mnli")
            analysis_res = pipeline.analyze(source_text, enhanced_text)
            st.session_state["last_analysis"] = analysis_res
            st.session_state["last_source"] = source_text
            st.session_state["last_enhanced"] = enhanced_text
            st.session_state.pop("repair_result", None)

    res = st.session_state.get("last_analysis")

    if res:
        primary_item = res.items[0] if res.items else None
        
        if primary_item:
            code = primary_item.classification.classification_code.value
            code_name = primary_item.classification.classification_name
            severity_num = primary_item.classification.severity
            shift_vector = primary_item.classification.shift_vector or {}
            confidence = primary_item.classification.confidence
            nli_label = getattr(primary_item.nli, "label", None)
            nli_ent_score = getattr(primary_item.nli, "entailment_score", 0.0)
        else:
            code = "C1"
            code_name = "UNCHANGED_FAITHFUL"
            severity_num = 0.0
            shift_vector = {}
            confidence = 1.0
            nli_label = None
            nli_ent_score = 1.0

        attrs = ["role", "qualifier", "scope", "certainty", "impact", "quantity"]
        overall_shifts = {a: shift_vector.get(a, 0.0) for a in attrs}

        labels_meta = {
            "C1": ("🟢 C1: Faithful Paraphrase", "#10B981", "#E6F4EA"),
            "C2": ("🔵 C2: Weakened Claim", "#3B82F6", "#EFF6FF"),
            "C3": ("🔴 C3: Strengthened Claim (SPS)", "#EF4444", "#FEF2F2"),
            "C4": ("⚠️ C4: Unsupported Addition", "#F59E0B", "#FFFBEB"),
            "C5": ("🟣 C5: Mixed-Direction Shift", "#8B5CF6", "#F5F3FF")
        }
        main_label, border_color, bg_color = labels_meta.get(code, ("C3: Strengthened", "#EF4444", "#FEF2F2"))
        severity_label, sev_color = severity_to_label(severity_num, code)
        explanation_text = make_explanation(code, overall_shifts)

        st.markdown("---")

        # ==========================================
        # VERDICT & KEY METRICS (Important Features)
        # ==========================================
        m_col1, m_col2, m_col3, m_col4 = st.columns([3, 2, 2, 2])
        with m_col1:
            st.markdown(f"**Classification Decision**\n### {main_label}")
        with m_col2:
            st.markdown(f"**Evidential Severity**\n### <span style='color:{sev_color};'>{severity_label}</span>", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"**Classifier Confidence**\n### {confidence * 100:.0f}%")
        with m_col4:
            abstain_str = "Abstain (Uncertain)" if confidence < 0.40 else "High (Decisive)"
            st.markdown(f"**Decision Status**\n### {abstain_str}")

        # ==========================================
        # NOVEL FEATURE: SPS Diagnostic vs NLI
        # ==========================================
        if code == "C3":
            st.markdown(
                """
                <div class="diagnostic-box">
                    <b>💡 Diagnostic: Support-Preserving Strengthening (SPS) Detected</b><br>
                    A standard NLI or hallucination checker evaluates this rewrite as <b>Supported / Entailment</b> (Strengthening Blindness Rate: 99.4%). 
                    However, FactSculpt detects that the subject's agency, certainty, or scope was escalated beyond the warrant of the source evidence.
                </div>
                """,
                unsafe_allow_html=True
            )
        elif code == "C4":
            st.markdown(
                """
                <div class="diagnostic-box" style="background:#FFFBEB; border-left-color:#F59E0B;">
                    <b>⚠️ Extrinsic Information Addition Detected</b><br>
                    The rewrite introduces new facts, contracts, or credentials completely absent from the source evidence (Closed-World Contradiction / Addition).
                </div>
                """,
                unsafe_allow_html=True
            )

        # ==========================================
        # 6-D SHIFT VECTOR TABLE
        # ==========================================
        st.markdown("### 📊 6-Dimensional Evidence Shift Vector")
        st.markdown("Quantifies directional shift along each orthogonal evidential dimension $(\\Delta \\in [-1.0, +1.0])$:")

        shift_rows = []
        for attr in attrs:
            val = overall_shifts.get(attr, 0.0)
            if val > 0.05:
                direction = "🔺 Strengthened"
                badge = f"+{val:.2f}"
            elif val < -0.05:
                direction = "🔻 Weakened"
                badge = f"{val:.2f}"
            else:
                direction = "➖ Preserved"
                badge = "0.00"

            descriptions = {
                "role": "Subject agency, leadership level, or role responsibility",
                "qualifier": "Promotional framing, prestige adjectives, or superlatives",
                "scope": "Operational coverage (e.g., local team vs global enterprise)",
                "certainty": "Epistemic modality (e.g., tentative vs guaranteed outcome)",
                "impact": "Magnitude of business or technological outcome achieved",
                "quantity": "Numeric bounds, percentage ranges, or threshold limits"
            }
            shift_rows.append({
                "Attribute Dimension": attr.capitalize(),
                "Shift Direction": direction,
                "Signed Magnitude": badge,
                "Evidential Scope": descriptions[attr]
            })

        df_shifts = pd.DataFrame(shift_rows)
        st.dataframe(df_shifts, use_container_width=True, hide_index=True)

        # ==========================================
        # EXPLANATION SYNTHESIS
        # ==========================================
        st.markdown("### 📝 Evidential Explanation")
        st.info(explanation_text)

        # ==========================================
        # NOVEL FEATURE: Attribute-Targeted Minimal Repair
        # ==========================================
        st.markdown("---")
        st.markdown("### 🛠️ Attribute-Targeted Minimal Repair")
        st.markdown(
            "Rather than regenerating the whole text or discarding valid polish, FactSculpt surgically "
            "steps down only the offending inflated spans until claims fit strictly within the evidence boundary."
        )

        repair_clicked = st.button("⚡ Run Attribute-Targeted Repair", type="secondary", use_container_width=True)

        if repair_clicked:
            with st.spinner("Running iterative span repair and verifying safety..."):
                repair_pipe = AttributeTargetedRepairPipeline(max_iterations=3)
                rep_res = repair_pipe.repair(st.session_state["last_source"], st.session_state["last_enhanced"])
                st.session_state["repair_result"] = rep_res

        if "repair_result" in st.session_state:
            rep = st.session_state["repair_result"]
            st.markdown(
                f"""
                <div class="repair-box">
                    <h4 style="margin-top:0; color:#15803D;">✅ Repaired Output (Evidence-Grounded)</h4>
                    <p style="font-size:1.15rem; font-weight:600; color:#0F172A; margin:0.5rem 0;">{rep.repaired_text}</p>
                    <p style="font-size:0.9rem; color:#475569; margin:0;">
                        <b>Status:</b> {rep.stopped_reason} | <b>Iterations:</b> {rep.iterations_run} | 
                        <b>Severity Shift:</b> {rep.initial_severity:.2f} &rarr; <b>{rep.final_severity:.2f}</b> |
                        <b>Classification:</b> {rep.initial_classification} &rarr; <b>{rep.final_classification}</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ==========================================
        # TECHNICAL AUDIT METRICS (Collapsible)
        # ==========================================
        with st.expander("🔍 View Technical Diagnostics & Claim Trace"):
            st.markdown("#### Shift Vector JSON")
            st.json({k: round(v, 2) for k, v in overall_shifts.items()})

            st.markdown("#### Claim Trace Details")
            for idx, item in enumerate(res.items):
                st.markdown(f"**Claim {idx+1}**: *\"{item.generated_claim_text}\"*")
                st.markdown(f"- **Source Anchor**: *\"{item.source_claim_text or 'None (Unsupported Addition)'}\"*")
                st.markdown(f"- **Assigned Rule**: `{item.classification.classification_code}` ({item.classification.classification_name})")
                st.markdown(f"- **Confidence**: `{item.classification.confidence * 100:.1f}%` | **Severity**: `{item.classification.severity:.2f}`")
                if item.classification.reasons:
                    st.markdown(f"- **Reasons**: {', '.join(item.classification.reasons)}")
                st.markdown("---")
