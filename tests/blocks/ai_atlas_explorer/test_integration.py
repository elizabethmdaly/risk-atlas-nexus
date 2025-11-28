"""
Integration tests for AI Atlas Explorer with real ontology data.

Tests the complete flow: task → capabilities → intrinsics
"""

import pytest
from pathlib import Path

from ai_atlas_nexus.library import AIAtlasNexus
from ai_atlas_nexus.blocks.ai_atlas_explorer import (
    AtlasExplorer,
    GraphEntityType,
    GraphRelationType,
)


@pytest.fixture
def ai_atlas_nexus():
    """Load AI Atlas Nexus ontology."""
    return AIAtlasNexus()


@pytest.fixture
def atlas_explorer(ai_atlas_nexus):
    """Create Atlas Explorer instance."""
    return AtlasExplorer(ai_atlas_nexus._ontology)


class TestCapabilityNavigation:
    """Test capability-related navigation."""

    def test_get_all_capabilities(self, atlas_explorer):
        """Test getting all capabilities."""
        capabilities = atlas_explorer.get_all_capabilities()
        assert isinstance(capabilities, list)
        # Should have at least the 11 capabilities from MVP
        assert len(capabilities) >= 11

    def test_get_capability_by_id(self, atlas_explorer):
        """Test getting a specific capability."""
        cap = atlas_explorer.get_capability(
            id="ibm-cap-reading-comprehension"
        )
        assert cap is not None
        assert cap.name == "Reading Comprehension"

    def test_get_capabilities_for_task(self, atlas_explorer):
        """Test getting capabilities for a task."""
        capabilities = atlas_explorer.get_capabilities_for_task(
            task_id="question-answering"
        )
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

        # Check that we got actual capability objects
        for cap in capabilities:
            assert hasattr(cap, 'name')
            assert hasattr(cap, 'id')

    def test_get_intrinsics_for_capability(self, atlas_explorer):
        """Test getting intrinsics for a capability."""
        intrinsics = atlas_explorer.get_intrinsics_for_capability(
            capability_id="ibm-cap-reading-comprehension"
        )
        assert isinstance(intrinsics, list)
        # Should have intrinsics implementing reading comprehension
        assert len(intrinsics) >= 4  # Based on MVP data

    def test_get_tasks_for_capability(self, atlas_explorer):
        """Test getting tasks that require a capability."""
        tasks = atlas_explorer.get_tasks_for_capability(
            capability_id="ibm-cap-reading-comprehension"
        )
        assert isinstance(tasks, list)
        assert len(tasks) > 0


class TestEndToEndTracing:
    """Test end-to-end tracing functionality."""

    def test_trace_task_to_intrinsics(self, atlas_explorer):
        """Test complete trace from task to intrinsics."""
        result = atlas_explorer.trace_task_to_intrinsics(
            task_id="question-answering"
        )

        # Verify structure
        assert "task" in result
        assert "capabilities" in result
        assert "intrinsics_by_capability" in result
        assert "all_intrinsics" in result

        # Verify task
        assert result["task"] is not None
        assert result["task"].id == "question-answering"

        # Verify capabilities
        assert len(result["capabilities"]) > 0

        # Verify intrinsics
        assert len(result["all_intrinsics"]) > 0

        # Verify mapping
        for cap in result["capabilities"]:
            # Each capability should have some intrinsics (or empty list)
            assert cap.id in result["intrinsics_by_capability"]


class TestGenericNavigation:
    """Test generic navigation patterns."""

    def test_navigate_with_named_pattern(self, atlas_explorer):
        """Test navigation using a named pattern."""
        result = atlas_explorer.navigate(
            "question-answering",
            GraphEntityType.AI_TASK,
            pattern="capabilities_for_task"
        )

        # Verify result structure
        assert hasattr(result, 'nodes')
        assert hasattr(result, 'statistics')

        # Should have found capabilities
        caps = result.get_nodes_by_type(GraphEntityType.CAPABILITY)
        assert len(caps) > 0

    def test_navigate_with_custom_config(self, atlas_explorer):
        """Test navigation with custom configuration."""
        from ai_atlas_nexus.blocks.ai_atlas_explorer import NavigationConfig

        config = NavigationConfig(
            max_depth=1,
            included_relationships=[GraphRelationType.REQUIRES_CAPABILITY],
            included_entity_types=[GraphEntityType.CAPABILITY]
        )

        result = atlas_explorer.navigate(
            "question-answering",
            GraphEntityType.AI_TASK,
            config=config
        )

        # Verify we only got capabilities
        assert all(
            node.entity_type == GraphEntityType.CAPABILITY
            for node in result.nodes
            if node.depth > 0
        )

    def test_navigate_with_kwargs(self, atlas_explorer):
        """Test navigation building config from kwargs."""
        result = atlas_explorer.navigate(
            "question-answering",
            GraphEntityType.AI_TASK,
            max_depth=1,
            included_relationships=[GraphRelationType.REQUIRES_CAPABILITY]
        )

        # Should have found nodes
        assert len(result.nodes) > 0
        assert result.statistics["max_depth_reached"] <= 1


class TestGetRelated:
    """Test generic get_related method."""

    def test_get_related_capabilities(self, atlas_explorer):
        """Test getting related capabilities for a task."""
        # Get a task first
        task = next((t for t in atlas_explorer._tasks if t.id == "question-answering"), None)
        assert task is not None

        # Get related capabilities
        capabilities = atlas_explorer.get_related(
            task,
            GraphRelationType.REQUIRES_CAPABILITY,
            GraphEntityType.CAPABILITY
        )

        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

    def test_get_related_intrinsics(self, atlas_explorer):
        """Test getting related intrinsics for a capability."""
        # Get a capability first
        cap = atlas_explorer.get_capability(id="ibm-cap-reading-comprehension")
        assert cap is not None

        # Get related intrinsics
        intrinsics = atlas_explorer.get_related(
            cap,
            GraphRelationType.IMPLEMENTED_BY_INTRINSIC,
            GraphEntityType.LLM_INTRINSIC
        )

        assert isinstance(intrinsics, list)
        # May be empty if only adapters implement this capability


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
