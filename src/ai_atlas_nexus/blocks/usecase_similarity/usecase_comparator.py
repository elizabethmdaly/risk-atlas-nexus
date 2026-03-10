"""Graph-structural similarity comparison between two use case knowledge graphs.

Computes per-factor Jaccard similarity across all AIRO factors and
graph-connected entities (risks, actions, tasks, stakeholders). Returns
a decomposed SimilarityResult that preserves per-factor scores for
downstream cascade analysis (Phase 2).

The key insight from the paper: text similarity between use case descriptions
can be misleading (e.g., 0.92 text similarity but 0.31 graph similarity).
This module implements the graph-structural approach.
"""

import logging
from typing import Optional

from .types import FactorSimilarity, SimilarityResult, UseCaseKG

logger = logging.getLogger(__name__)

# Default weights for combining per-factor scores into overall similarity.
# These can be overridden at call time. Weights reflect that graph-connected
# entities (risks, actions) carry more governance signal than string factors.
DEFAULT_WEIGHTS = {
    "domains": 0.15,
    "purpose": 0.10,
    "capabilities": 0.10,
    "ai_subjects": 0.10,
    "localities": 0.15,
    "risk_ids": 0.20,
    "action_ids": 0.10,
    "task_ids": 0.05,
    "stakeholder_ids": 0.05,
}


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets. Returns 1.0 if both are empty."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def _normalize_set(values: list[str]) -> set[str]:
    """Normalize string values for comparison (lowercase, stripped)."""
    return {v.strip().lower() for v in values if v}


def _compare_factor(
    name: str, values_a: list[str], values_b: list[str]
) -> FactorSimilarity:
    """Compare a single factor between two use cases."""
    set_a = _normalize_set(values_a)
    set_b = _normalize_set(values_b)
    score = _jaccard(set_a, set_b)
    return FactorSimilarity(
        factor=name,
        score=score,
        shared=sorted(set_a & set_b),
        only_in_a=sorted(set_a - set_b),
        only_in_b=sorted(set_b - set_a),
    )


class UseCaseComparator:
    """Compares two UseCaseKG instances using graph-structural similarity.

    Usage:
        comparator = UseCaseComparator()
        result = comparator.compare(kg_a, kg_b)
        print(result.overall_score)
        for f in result.divergent_factors(threshold=0.5):
            print(f"  {f.factor}: {f.score:.2f} - only_in_a: {f.only_in_a}")
    """

    def __init__(self, weights: Optional[dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def compare(
        self, kg_a: UseCaseKG, kg_b: UseCaseKG
    ) -> SimilarityResult:
        """Compare two use case knowledge graphs.

        Returns a SimilarityResult with per-factor decomposition. The overall
        score is a weighted combination of factor scores.
        """
        factors = []

        # String-valued AIRO factors
        factors.append(_compare_factor("domains", kg_a.domains, kg_b.domains))

        # Purpose is single-valued — wrap in list for uniform comparison
        purpose_a = [kg_a.purpose] if kg_a.purpose else []
        purpose_b = [kg_b.purpose] if kg_b.purpose else []
        factors.append(_compare_factor("purpose", purpose_a, purpose_b))

        factors.append(
            _compare_factor("capabilities", kg_a.capabilities, kg_b.capabilities)
        )
        factors.append(
            _compare_factor("ai_subjects", kg_a.ai_subjects, kg_b.ai_subjects)
        )
        factors.append(
            _compare_factor("localities", kg_a.localities, kg_b.localities)
        )

        # Graph-connected entity IDs
        factors.append(_compare_factor("risk_ids", kg_a.risk_ids, kg_b.risk_ids))
        factors.append(
            _compare_factor("action_ids", kg_a.action_ids, kg_b.action_ids)
        )
        factors.append(_compare_factor("task_ids", kg_a.task_ids, kg_b.task_ids))
        factors.append(
            _compare_factor(
                "stakeholder_ids", kg_a.stakeholder_ids, kg_b.stakeholder_ids
            )
        )

        # Compute weighted overall score
        total_weight = 0.0
        weighted_sum = 0.0
        for f in factors:
            w = self.weights.get(f.factor, 0.0)
            weighted_sum += f.score * w
            total_weight += w

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0

        result = SimilarityResult(
            overall_score=round(overall, 4),
            factors=factors,
            usecase_a_id=kg_a.usecase_id,
            usecase_b_id=kg_b.usecase_id,
        )

        divergent = result.divergent_factors(threshold=0.5)
        if divergent:
            names = ", ".join(f.factor for f in divergent)
            logger.info(
                "Use cases %s and %s diverge on: %s (overall=%.2f)",
                kg_a.usecase_id,
                kg_b.usecase_id,
                names,
                overall,
            )

        return result
