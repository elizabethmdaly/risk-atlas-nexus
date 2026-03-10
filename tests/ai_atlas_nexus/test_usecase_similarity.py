"""Tests for use case similarity comparison.

Demonstrates the paper's key scenario: two algorithmic hiring use cases
that differ only in locality (New York vs EU) produce substantially
different knowledge graphs despite near-identical text descriptions.
"""

import pytest

from ai_atlas_nexus.blocks.usecase_similarity import (
    FactorSimilarity,
    SimilarityResult,
    UseCaseBuilder,
    UseCaseComparator,
    UseCaseKG,
)


# --- Fixtures: Paper's algorithmic hiring example (Figure 1) ---


@pytest.fixture
def hiring_ny():
    """Algorithmic hiring use case in New York, US (Figure 1a)."""
    builder = UseCaseBuilder()
    return builder.from_factors(
        usecase_id="uc-hiring-ny",
        description="AI algorithm for making hiring decisions",
        domains=["Human Resources"],
        purpose="making hiring decisions",
        capabilities=["Multimodal analysis"],
        ai_subjects=["Job applicants"],
        localities=["New York, US"],
        risk_ids=[
            "atlas-lack-of-model-transparency",
            "atlas-over-or-under-reliance",
            "atlas-discriminatory-actions",
            "atlas-unexplainable-output",
            "atlas-unrepresentative-data",
        ],
        action_ids=["nist-mg-2.7-001"],  # audit_requirements
        task_ids=["aitask:multimodal-analysis"],
    )


@pytest.fixture
def hiring_eu():
    """Algorithmic hiring use case in the EU (Figure 1b)."""
    builder = UseCaseBuilder()
    return builder.from_factors(
        usecase_id="uc-hiring-eu",
        description="AI algorithm for making hiring decisions",
        domains=["Human Resources"],
        purpose="making hiring decisions",
        capabilities=["Multimodal analysis"],
        ai_subjects=["Job applicants"],
        localities=["EU"],
        risk_ids=[
            "atlas-lack-of-model-transparency",
            "atlas-over-or-under-reliance",
            "atlas-discriminatory-actions",
            "atlas-unexplainable-output",
            "atlas-unrepresentative-data",
        ],
        action_ids=["nist-mg-2.7-002"],  # provide_explanation (GDPR-driven)
        task_ids=["aitask:multimodal-analysis"],
    )


@pytest.fixture
def medical_imaging():
    """A completely different use case for contrast."""
    builder = UseCaseBuilder()
    return builder.from_factors(
        usecase_id="uc-medical-imaging",
        description="AI system for medical image diagnosis",
        domains=["Healthcare"],
        purpose="medical diagnosis",
        capabilities=["Image classification"],
        ai_subjects=["Patients"],
        localities=["EU"],
        risk_ids=[
            "atlas-lack-of-model-transparency",
            "atlas-data-bias",
            "atlas-harmful-output",
        ],
        task_ids=["aitask:image-classification"],
    )


# --- Tests ---


class TestUseCaseKG:
    """Test the UseCaseKG data structure."""

    def test_from_factors(self, hiring_ny):
        assert hiring_ny.usecase_id == "uc-hiring-ny"
        assert len(hiring_ny.risk_ids) == 5
        assert hiring_ny.purpose == "making hiring decisions"

    def test_auto_generated_id(self):
        builder = UseCaseBuilder()
        kg = builder.from_factors(description="test")
        assert kg.usecase_id.startswith("uc-")


class TestUseCaseComparator:
    """Test graph-structural similarity comparison."""

    def test_identical_use_cases(self, hiring_ny):
        comparator = UseCaseComparator()
        result = comparator.compare(hiring_ny, hiring_ny)
        assert result.overall_score == 1.0
        assert all(f.score == 1.0 for f in result.factors)

    def test_locality_change_reduces_similarity(self, hiring_ny, hiring_eu):
        """Paper's core scenario: locality change triggers divergence."""
        comparator = UseCaseComparator()
        result = comparator.compare(hiring_ny, hiring_eu)

        # Overall should be high but not 1.0
        assert 0.5 < result.overall_score < 1.0

        # Risks should be identical (same 5 risks)
        risk_factor = result.get_factor("risk_ids")
        assert risk_factor is not None
        assert risk_factor.score == 1.0

        # Locality should be completely different
        locality_factor = result.get_factor("localities")
        assert locality_factor is not None
        assert locality_factor.score == 0.0
        assert "new york, us" in locality_factor.only_in_a
        assert "eu" in locality_factor.only_in_b

        # Actions diverge (different controls due to different policies)
        action_factor = result.get_factor("action_ids")
        assert action_factor is not None
        assert action_factor.score == 0.0

    def test_completely_different_use_cases(self, hiring_ny, medical_imaging):
        """Different domain, purpose, subjects — should have low similarity."""
        comparator = UseCaseComparator()
        result = comparator.compare(hiring_ny, medical_imaging)
        assert result.overall_score < 0.5

    def test_divergent_factors(self, hiring_ny, hiring_eu):
        """Test the divergent_factors helper."""
        comparator = UseCaseComparator()
        result = comparator.compare(hiring_ny, hiring_eu)
        divergent = result.divergent_factors(threshold=0.5)
        factor_names = {f.factor for f in divergent}
        assert "localities" in factor_names
        assert "action_ids" in factor_names
        assert "risk_ids" not in factor_names

    def test_custom_weights(self, hiring_ny, hiring_eu):
        """Test that custom weights change the overall score."""
        # Weight only localities — should be 0.0
        comparator = UseCaseComparator(weights={"localities": 1.0})
        result = comparator.compare(hiring_ny, hiring_eu)
        assert result.overall_score == 0.0

        # Weight only risks — should be 1.0
        comparator = UseCaseComparator(weights={"risk_ids": 1.0})
        result = comparator.compare(hiring_ny, hiring_eu)
        assert result.overall_score == 1.0

    def test_per_factor_decomposition_preserved(self, hiring_ny, hiring_eu):
        """Ensure per-factor scores are always available (Phase 2 readiness)."""
        comparator = UseCaseComparator()
        result = comparator.compare(hiring_ny, hiring_eu)

        expected_factors = {
            "domains",
            "purpose",
            "capabilities",
            "ai_subjects",
            "localities",
            "risk_ids",
            "action_ids",
            "task_ids",
            "stakeholder_ids",
        }
        actual_factors = {f.factor for f in result.factors}
        assert actual_factors == expected_factors

    def test_factor_details_populated(self, hiring_ny, medical_imaging):
        """Test that shared/only_in_a/only_in_b are populated correctly."""
        comparator = UseCaseComparator()
        result = comparator.compare(hiring_ny, medical_imaging)

        risk_factor = result.get_factor("risk_ids")
        assert risk_factor is not None
        # atlas-lack-of-model-transparency is in both
        assert "atlas-lack-of-model-transparency" in risk_factor.shared
        # atlas-discriminatory-actions only in hiring
        assert "atlas-discriminatory-actions" in risk_factor.only_in_a
        # atlas-harmful-output only in medical
        assert "atlas-harmful-output" in risk_factor.only_in_b


class TestSimilarityResult:
    """Test the SimilarityResult data structure."""

    def test_get_factor_returns_none_for_missing(self):
        result = SimilarityResult(overall_score=0.5, factors=[])
        assert result.get_factor("nonexistent") is None

    def test_divergent_factors_empty_when_all_similar(self):
        factors = [FactorSimilarity(factor="test", score=0.9)]
        result = SimilarityResult(overall_score=0.9, factors=factors)
        assert result.divergent_factors(threshold=0.5) == []
