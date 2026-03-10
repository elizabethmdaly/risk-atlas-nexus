"""Types for use case similarity comparison.

Designed with per-factor decomposition so that Phase 2 can layer cascade
detection and explanation on top without changing the core return types.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FactorSimilarity:
    """Similarity score for a single use case factor.

    Keeping per-factor scores as structured objects (not bare floats) allows
    Phase 2 to add cascade metadata and provenance without breaking the API.
    """

    factor: str
    score: float  # 0.0 to 1.0
    shared: list[str] = field(default_factory=list)
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)


@dataclass
class SimilarityResult:
    """Result of comparing two use case knowledge graphs.

    Returns per-factor decomposition (not just a single score) so that
    downstream consumers can identify which factors diverged and why.
    """

    overall_score: float  # Weighted combination of factor scores
    factors: list[FactorSimilarity] = field(default_factory=list)
    usecase_a_id: Optional[str] = None
    usecase_b_id: Optional[str] = None

    def get_factor(self, name: str) -> Optional[FactorSimilarity]:
        """Retrieve a specific factor's similarity by name."""
        for f in self.factors:
            if f.factor == name:
                return f
        return None

    def divergent_factors(self, threshold: float = 0.5) -> list[FactorSimilarity]:
        """Return factors where similarity is below the given threshold."""
        return [f for f in self.factors if f.score < threshold]


@dataclass
class UseCaseKG:
    """A self-contained star-shaped knowledge graph centered on a use case.

    This is the serializable PKG (Personal Knowledge Graph) representation
    from the paper. Each field holds the IDs (or string values) of entities
    connected to the use case via that factor.

    Designed as a plain data object so it can be:
    - Serialized to YAML/JSON for versioning
    - Compared structurally via UseCaseComparator
    - Extended in Phase 2 with derived_from, stakeholder_role, etc.
    """

    usecase_id: str
    description: str

    # AIRO factors (string-valued, multivalued)
    domains: list[str] = field(default_factory=list)
    purpose: Optional[str] = None
    capabilities: list[str] = field(default_factory=list)
    ai_subjects: list[str] = field(default_factory=list)
    localities: list[str] = field(default_factory=list)

    # Graph-connected entity IDs (references into the ontology)
    risk_ids: list[str] = field(default_factory=list)
    action_ids: list[str] = field(default_factory=list)
    task_ids: list[str] = field(default_factory=list)
    stakeholder_ids: list[str] = field(default_factory=list)
