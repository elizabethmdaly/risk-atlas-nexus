"""
Named query patterns for common knowledge graph traversals.

Each pattern defines a NavigationConfig template for common use cases.
No LLM parsing is involved - these are simple dictionary lookups.
"""

from typing import Dict, Any
from .types import GraphEntityType, GraphRelationType


# Pattern definitions
QUERY_PATTERNS: Dict[str, Dict[str, Any]] = {
    # ========================================
    # CAPABILITY PATTERNS
    # ========================================
    "capabilities_for_task": {
        "description": "Get all capabilities required by a specific AI task",
        "config": {
            "max_depth": 1,
            "included_relationships": [GraphRelationType.REQUIRES_CAPABILITY],
            "included_entity_types": [GraphEntityType.CAPABILITY],
        },
    },
    "intrinsics_for_capability": {
        "description": "Get all intrinsics/adapters that implement a capability",
        "config": {
            "max_depth": 1,
            "included_relationships": [
                GraphRelationType.IMPLEMENTED_BY_INTRINSIC,
                GraphRelationType.IMPLEMENTED_BY_ADAPTER,
            ],
            "included_entity_types": [
                GraphEntityType.LLM_INTRINSIC,
                GraphEntityType.ADAPTER,
            ],
        },
    },
    "tasks_for_capability": {
        "description": "Get all tasks that require a capability",
        "config": {
            "max_depth": 1,
            "included_relationships": [GraphRelationType.REQUIRED_BY_TASK],
            "included_entity_types": [GraphEntityType.AI_TASK],
        },
    },
    "capability_hierarchy": {
        "description": "Get the full capability hierarchy (domain → groups → capabilities)",
        "config": {
            "max_depth": 2,
            "included_relationships": [
                GraphRelationType.HAS_PART,
                GraphRelationType.IS_PART_OF,
                GraphRelationType.BELONGS_TO_DOMAIN,
            ],
            "included_entity_types": [
                GraphEntityType.CAPABILITY_DOMAIN,
                GraphEntityType.CAPABILITY_GROUP,
                GraphEntityType.CAPABILITY,
            ],
        },
    },
    "end_to_end_task_to_intrinsics": {
        "description": "Complete path: task → capabilities → intrinsics",
        "config": {
            "max_depth": 2,
            "included_relationships": [
                GraphRelationType.REQUIRES_CAPABILITY,
                GraphRelationType.IMPLEMENTED_BY_INTRINSIC,
                GraphRelationType.IMPLEMENTED_BY_ADAPTER,
            ],
            "included_entity_types": [
                GraphEntityType.CAPABILITY,
                GraphEntityType.LLM_INTRINSIC,
                GraphEntityType.ADAPTER,
            ],
        },
    },
    # ========================================
    # RISK PATTERNS
    # ========================================
    "controls_for_risk": {
        "description": "Get all controls that detect a specific risk",
        "config": {
            "max_depth": 1,
            "included_relationships": [GraphRelationType.IS_DETECTED_BY],
            "included_entity_types": [GraphEntityType.RISK_CONTROL],
        },
    },
    "actions_for_risk": {
        "description": "Get all actions for a specific risk",
        "config": {
            "max_depth": 1,
            "included_relationships": [GraphRelationType.HAS_RELATED_ACTION],
            "included_entity_types": [GraphEntityType.ACTION],
        },
    },
    "related_risks": {
        "description": "Get all risks related via SKOS relationships",
        "config": {
            "max_depth": 1,
            "included_relationships": [
                GraphRelationType.EXACT_MATCH,
                GraphRelationType.CLOSE_MATCH,
                GraphRelationType.BROAD_MATCH,
                GraphRelationType.NARROW_MATCH,
                GraphRelationType.RELATED_MATCH,
            ],
            "included_entity_types": [GraphEntityType.RISK],
        },
    },
    "risk_neighborhood": {
        "description": "Comprehensive neighborhood of a risk (controls, actions, related risks)",
        "config": {
            "max_depth": 2,
            "included_relationships": [
                GraphRelationType.IS_DETECTED_BY,
                GraphRelationType.HAS_RELATED_ACTION,
                GraphRelationType.EXACT_MATCH,
                GraphRelationType.CLOSE_MATCH,
                GraphRelationType.BROAD_MATCH,
                GraphRelationType.NARROW_MATCH,
                GraphRelationType.RELATED_MATCH,
            ],
            "included_entity_types": [
                GraphEntityType.RISK_CONTROL,
                GraphEntityType.ACTION,
                GraphEntityType.RISK,
            ],
        },
    },
    # ========================================
    # EVALUATION PATTERNS
    # ========================================
    "intrinsics_for_task": {
        "description": "Get intrinsics related to a task",
        "config": {
            "max_depth": 1,
            "included_relationships": [GraphRelationType.HAS_RELATED_LLMINTRINSIC],
            "included_entity_types": [GraphEntityType.LLM_INTRINSIC],
        },
    },
    # ========================================
    # DOCUMENTATION PATTERNS
    # ========================================
    "documentation_for_entity": {
        "description": "Get all documentation for an entity",
        "config": {
            "max_depth": 1,
            "included_relationships": [GraphRelationType.HAS_DOCUMENTATION],
            "included_entity_types": [GraphEntityType.DOCUMENT],
        },
    },
    # ========================================
    # CROSS-TAXONOMY PATTERNS
    # ========================================
    "skos_matches": {
        "description": "Get all SKOS-matched entities (works for risks, capabilities, etc.)",
        "config": {
            "max_depth": 1,
            "included_relationships": [
                GraphRelationType.EXACT_MATCH,
                GraphRelationType.CLOSE_MATCH,
                GraphRelationType.BROAD_MATCH,
                GraphRelationType.NARROW_MATCH,
                GraphRelationType.RELATED_MATCH,
            ],
        },
    },
}


def get_pattern_config(pattern_name: str) -> Dict[str, Any]:
    """
    Get the configuration for a named pattern.

    Args:
        pattern_name: Name of the pattern (from QUERY_PATTERNS keys)

    Returns:
        Pattern configuration dictionary

    Raises:
        ValueError: If pattern name is not found

    Examples:
        >>> config = get_pattern_config("capabilities_for_task")
        >>> config['max_depth']
        1
    """
    if pattern_name not in QUERY_PATTERNS:
        available = ", ".join(QUERY_PATTERNS.keys())
        raise ValueError(
            f"Unknown pattern: '{pattern_name}'. Available patterns: {available}"
        )
    return QUERY_PATTERNS[pattern_name]["config"]


def list_patterns() -> Dict[str, str]:
    """
    List all available query patterns with their descriptions.

    Returns:
        Dictionary mapping pattern names to descriptions

    Examples:
        >>> patterns = list_patterns()
        >>> print(patterns["capabilities_for_task"])
        Get all capabilities required by a specific AI task
    """
    return {
        name: info["description"]
        for name, info in QUERY_PATTERNS.items()
    }
