"""
factsculpt/taxonomy.py
Single canonical source of truth for the FactSculpt claim taxonomy across the entire codebase.

Taxonomy:
  C1 = UNCHANGED_FAITHFUL: Evidential strength preserved; claims remain within source scope and certainty.
  C2 = WEAKENED: Evidence downgraded, agency softened, scope contracted, or certainty hedged.
  C3 = STRENGTHENED: Evidence amplified (role agency elevated, qualifier intensified, scope expanded, certainty strengthened, impact increased, or quantity inflated).
  C4 = UNSUPPORTED_ADDITION: Claim contains new factual assertions with zero grounding in source evidence.
  C5 = MIXED: Simultaneous strengthening and weakening across distinct attributes.
"""
from enum import Enum
from typing import Dict

class ClaimTaxonomy(str, Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"

# Canonical research classification names
TAXONOMY_NAMES: Dict[ClaimTaxonomy, str] = {
    ClaimTaxonomy.C1: "UNCHANGED_FAITHFUL",
    ClaimTaxonomy.C2: "WEAKENED",
    ClaimTaxonomy.C3: "STRENGTHENED",
    ClaimTaxonomy.C4: "UNSUPPORTED_ADDITION",
    ClaimTaxonomy.C5: "MIXED",
}

# Alias for backwards compatibility
ClassificationCode = ClaimTaxonomy
RESEARCH_CLASSIFICATION_NAMES = TAXONOMY_NAMES
LEGACY_CLASSIFICATION_NAMES = {
    ClaimTaxonomy.C1: "ENTAILED",
    ClaimTaxonomy.C2: "EXAGGERATED_STRENGTHENED",
    ClaimTaxonomy.C3: "NEUTRAL_UNDER_SPECIFIED",
    ClaimTaxonomy.C4: "WEAKENED_REDUCED",
    ClaimTaxonomy.C5: "CONTRADICTED",
}
