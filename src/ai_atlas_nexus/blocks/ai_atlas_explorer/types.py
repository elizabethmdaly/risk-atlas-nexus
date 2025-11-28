"""
Type definitions for the AI Atlas knowledge graph.

Defines entity types and relationship types used in graph traversal.
"""

from enum import Enum


class GraphEntityType(Enum):
    """Entity types in the AI Risk Atlas knowledge graph."""

    # Risk entities
    RISK = "Risk"
    RISK_GROUP = "RiskGroup"
    RISK_TAXONOMY = "RiskTaxonomy"
    RISK_CONTROL = "RiskControl"
    RISK_INCIDENT = "RiskIncident"
    ACTION = "Action"

    # AI system entities
    AI_SYSTEM = "AiSystem"
    AI_MODEL = "AiModel"
    AI_TASK = "AiTask"
    USE_CASE = "UseCase"

    # Capability entities
    CAPABILITY = "Capability"
    CAPABILITY_GROUP = "CapabilityGroup"
    CAPABILITY_DOMAIN = "CapabilityDomain"
    CAPABILITY_TAXONOMY = "CapabilityTaxonomy"

    # Intrinsic entities
    LLM_INTRINSIC = "LLMIntrinsic"
    ADAPTER = "Adapter"

    # Evaluation entities
    EVALUATION = "Evaluation"
    AI_EVAL_RESULT = "AiEvalResult"
    BENCHMARK = "BenchmarkMetadataCard"

    # Supporting entities
    STAKEHOLDER = "Stakeholder"
    STAKEHOLDER_GROUP = "StakeholderGroup"
    DOCUMENT = "Documentation"
    DATASET = "Dataset"
    PRINCIPLE = "Principle"
    POLICY = "LLMQuestionPolicy"
    RULE = "Rule"
    LICENSE = "License"
    ORGANIZATION = "Organization"


class GraphRelationType(Enum):
    """Relationship types in the knowledge graph."""

    # Risk relationships
    HAS_RELATED_RISK = "hasRelatedRisk"
    HAS_RELATED_ACTION = "hasRelatedAction"
    IS_DETECTED_BY = "isDetectedBy"
    DETECTS_RISK_CONCEPT = "detectsRiskConcept"
    REFERS_TO_RISK = "refersToRisk"

    # Task-capability relationships
    REQUIRES_CAPABILITY = "requiresCapability"
    REQUIRED_BY_TASK = "requiredByTask"

    # Capability-intrinsic relationships
    IMPLEMENTS_CAPABILITY = "implementsCapability"
    IMPLEMENTED_BY_INTRINSIC = "implementedByIntrinsic"
    IMPLEMENTS_CAPABILITY_ADAPTER = "implementsCapability_adapter"
    IMPLEMENTED_BY_ADAPTER = "implementedByAdapter"

    # Capability-benchmark relationships
    EVALUATES_CAPABILITY = "evaluatesCapability"
    EVALUATED_BY_BENCHMARK = "evaluatedByBenchmark"

    # Hierarchy relationships
    IS_PART_OF = "isPartOf"
    HAS_PART = "hasPart"
    BELONGS_TO_DOMAIN = "belongsToDomain"
    IS_DEFINED_BY_TAXONOMY = "isDefinedByTaxonomy"

    # SKOS relationships
    EXACT_MATCH = "exactMatch"
    CLOSE_MATCH = "closeMatch"
    BROAD_MATCH = "broadMatch"
    NARROW_MATCH = "narrowMatch"
    RELATED_MATCH = "relatedMatch"

    # Evaluation relationships
    HAS_EVALUATION = "hasEvaluation"
    EVALUATES_RISK = "evaluatesRisk"
    HAS_RELATED_LLMINTRINSIC = "hasRelatedLLMIntrinsic"

    # Documentation relationships
    HAS_DOCUMENTATION = "hasDocumentation"
    HAS_LICENSE = "hasLicense"

    # AI system relationships
    HAS_AI_TASK = "hasAiTask"
    HAS_STAKEHOLDER = "hasStakeholder"

    # Rule relationships
    HAS_RULE = "hasRule"
