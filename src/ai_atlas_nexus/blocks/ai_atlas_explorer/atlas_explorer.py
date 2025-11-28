"""
Atlas Explorer - Main interface for generic knowledge graph navigation.

Provides both generic graph traversal and convenience methods for common query patterns.
"""

from typing import Any, Dict, List, Optional
from collections import defaultdict

from .types import GraphEntityType, GraphRelationType
from .graph_navigator import GraphNavigator, NavigationConfig, TraversalResult
from .query_patterns import get_pattern_config


class AtlasExplorer:
    """
    Generic knowledge graph explorer for Risk Atlas Nexus.

    Provides both generic graph traversal and convenience methods
    for common query patterns.
    """

    def __init__(self, ontology):
        """
        Initialize the explorer.

        Args:
            ontology: The loaded Risk Atlas Nexus ontology
        """
        self.ontology = ontology
        self.navigator = GraphNavigator(ontology)

        # Direct access to collections (like risk_explorer)
        self._capabilities = ontology.capabilities or []
        self._capability_groups = ontology.capabilitygroups or []
        self._capability_domains = ontology.capabilitydomains or []
        self._tasks = ontology.aitasks or []
        self._intrinsics = ontology.llmintrinsics or []
        self._adapters = ontology.adapters or []
        self._benchmarks = ontology.benchmarkmetadatacards or []
        self._risks = ontology.risks or []
        self._actions = ontology.actions or []
        self._risk_controls = ontology.riskcontrols or []
        self._documents = ontology.documents or []

    # ========================================
    # GENERIC NAVIGATION METHODS
    # ========================================

    def navigate(
        self,
        start_id: str,
        start_type: GraphEntityType,
        pattern: Optional[str] = None,
        config: Optional[NavigationConfig] = None,
        **kwargs
    ) -> TraversalResult:
        """
        Generic graph navigation from any starting point.

        Args:
            start_id: Starting entity ID
            start_type: Starting entity type
            pattern: Optional named query pattern (from query_patterns.QUERY_PATTERNS)
            config: Optional NavigationConfig for custom traversal
            **kwargs: Parameters for NavigationConfig if neither pattern nor config provided

        Returns:
            TraversalResult with all discovered nodes and relationships

        Examples:
            # Use a named pattern
            result = explorer.navigate(
                "question-answering",
                GraphEntityType.AI_TASK,
                pattern="capabilities_for_task"
            )

            # Custom configuration
            result = explorer.navigate(
                "ibm-cap-reading-comprehension",
                GraphEntityType.CAPABILITY,
                config=NavigationConfig(
                    max_depth=2,
                    included_relationships=[
                        GraphRelationType.REQUIRED_BY_TASK,
                        GraphRelationType.IMPLEMENTED_BY_INTRINSIC
                    ]
                )
            )

            # Build config from kwargs
            result = explorer.navigate(
                "question-answering",
                GraphEntityType.AI_TASK,
                max_depth=2,
                included_relationships=[GraphRelationType.REQUIRES_CAPABILITY]
            )
        """
        if pattern:
            # Use named pattern
            pattern_config = get_pattern_config(pattern)
            config = NavigationConfig(**pattern_config)
        elif config is None:
            # Build config from kwargs
            config = NavigationConfig(**kwargs)

        return self.navigator.traverse_from_node(start_id, start_type, config)

    def get_related(
        self,
        entity,
        relationship_type: GraphRelationType,
        target_type: Optional[GraphEntityType] = None,
        max_depth: int = 1,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Generic method to get related entities.

        Args:
            entity: Starting entity (object or ID string)
            relationship_type: Type of relationship to follow
            target_type: Optional filter for target entity type
            max_depth: Traversal depth (default 1)
            taxonomy: Optional taxonomy filter

        Returns:
            List of related entities

        Examples:
            # Get capabilities for a task
            caps = explorer.get_related(
                task,
                GraphRelationType.REQUIRES_CAPABILITY,
                GraphEntityType.CAPABILITY
            )

            # Get intrinsics for a capability
            intrinsics = explorer.get_related(
                capability,
                GraphRelationType.IMPLEMENTED_BY_INTRINSIC,
                GraphEntityType.LLM_INTRINSIC
            )
        """
        # Extract ID and type from entity
        if isinstance(entity, str):
            entity_id = entity
            entity_type = self._infer_entity_type(entity_id)
        else:
            entity_id = entity.id
            entity_type = self._get_entity_type(entity)

        # Build config
        config = NavigationConfig(
            max_depth=max_depth,
            included_relationships=[relationship_type],
            included_entity_types=[target_type] if target_type else None,
            node_property_filters={"isDefinedByTaxonomy": taxonomy} if taxonomy else None
        )

        # Execute traversal
        result = self.navigator.traverse_from_node(entity_id, entity_type, config)

        # Extract entities from result
        return [node.entity_data for node in result.nodes if node.depth > 0]

    # ========================================
    # CONVENIENCE METHODS: CAPABILITIES
    # ========================================

    def get_all_capabilities(self, taxonomy: Optional[str] = None) -> List[Any]:
        """Get all capability definitions."""
        capabilities = self._capabilities
        if taxonomy:
            capabilities = [c for c in capabilities if c.isDefinedByTaxonomy == taxonomy]
        return capabilities

    def get_capability(
        self,
        tag: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get a capability by tag, id, or name.

        Args:
            tag: Optional capability tag
            id: Optional capability ID
            name: Optional capability name
            taxonomy: Optional taxonomy filter

        Returns:
            Capability object or None if not found
        """
        capabilities = self._capabilities

        if tag:
            capabilities = [c for c in capabilities if getattr(c, 'tag', None) == tag]
        if id:
            capabilities = [c for c in capabilities if c.id == id]
        if name:
            capabilities = [c for c in capabilities if c.name == name]
        if taxonomy:
            capabilities = [c for c in capabilities if c.isDefinedByTaxonomy == taxonomy]

        return capabilities[0] if capabilities else None

    def get_capabilities_for_task(
        self,
        task=None,
        task_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Get capabilities required by a task.

        Args:
            task: Optional task object
            task_id: Optional task ID
            tag: Optional task tag
            name: Optional task name
            taxonomy: Optional taxonomy filter for results

        Returns:
            List of Capability objects

        Examples:
            # By task object
            caps = explorer.get_capabilities_for_task(task=my_task)

            # By task ID
            caps = explorer.get_capabilities_for_task(task_id="question-answering")
        """
        # Find the task
        if task:
            task_obj = task
        elif task_id:
            task_obj = next((t for t in self._tasks if t.id == task_id), None)
        elif tag:
            task_obj = next((t for t in self._tasks if getattr(t, 'tag', None) == tag), None)
        elif name:
            task_obj = next((t for t in self._tasks if t.name == name), None)
        else:
            return []

        if not task_obj:
            return []

        # Use generic navigation
        result = self.navigate(
            task_obj.id,
            GraphEntityType.AI_TASK,
            pattern="capabilities_for_task"
        )

        # Extract capabilities
        capabilities = [
            node.entity_data
            for node in result.nodes
            if node.entity_type == GraphEntityType.CAPABILITY
        ]

        # Apply taxonomy filter
        if taxonomy:
            capabilities = [c for c in capabilities if c.isDefinedByTaxonomy == taxonomy]

        return capabilities

    def get_intrinsics_for_capability(
        self,
        capability=None,
        capability_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None,
        include_adapters: bool = True
    ) -> List[Any]:
        """
        Get intrinsics/adapters that implement a capability.

        Args:
            capability: Optional capability object
            capability_id: Optional capability ID
            tag: Optional capability tag
            name: Optional capability name
            taxonomy: Optional taxonomy filter for results
            include_adapters: Whether to include adapters (default True)

        Returns:
            List of LLMIntrinsic and/or Adapter objects

        Examples:
            # By capability object
            intrinsics = explorer.get_intrinsics_for_capability(capability=cap)

            # By capability ID
            intrinsics = explorer.get_intrinsics_for_capability(
                capability_id="ibm-cap-reading-comprehension"
            )

            # LLMIntrinsics only (exclude adapters)
            intrinsics = explorer.get_intrinsics_for_capability(
                capability_id="ibm-cap-reading-comprehension",
                include_adapters=False
            )
        """
        # Find the capability
        if capability:
            cap_obj = capability
        elif capability_id:
            cap_obj = next((c for c in self._capabilities if c.id == capability_id), None)
        elif tag:
            cap_obj = next((c for c in self._capabilities if getattr(c, 'tag', None) == tag), None)
        elif name:
            cap_obj = next((c for c in self._capabilities if c.name == name), None)
        else:
            return []

        if not cap_obj:
            return []

        # Use generic navigation
        result = self.navigate(
            cap_obj.id,
            GraphEntityType.CAPABILITY,
            pattern="intrinsics_for_capability"
        )

        # Extract intrinsics and adapters
        intrinsics = []
        for node in result.nodes:
            if node.entity_type == GraphEntityType.LLM_INTRINSIC:
                intrinsics.append(node.entity_data)
            elif include_adapters and node.entity_type == GraphEntityType.ADAPTER:
                intrinsics.append(node.entity_data)

        # Apply taxonomy filter
        if taxonomy:
            intrinsics = [i for i in intrinsics if getattr(i, 'isDefinedByTaxonomy', None) == taxonomy]

        return intrinsics

    def get_tasks_for_capability(
        self,
        capability=None,
        capability_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Get tasks that require a capability.

        Args:
            capability: Optional capability object
            capability_id: Optional capability ID
            tag: Optional capability tag
            name: Optional capability name
            taxonomy: Optional taxonomy filter for results

        Returns:
            List of AiTask objects
        """
        # Find the capability
        if capability:
            cap_obj = capability
        elif capability_id:
            cap_obj = next((c for c in self._capabilities if c.id == capability_id), None)
        elif tag:
            cap_obj = next((c for c in self._capabilities if getattr(c, 'tag', None) == tag), None)
        elif name:
            cap_obj = next((c for c in self._capabilities if c.name == name), None)
        else:
            return []

        if not cap_obj:
            return []

        # Use generic navigation
        result = self.navigate(
            cap_obj.id,
            GraphEntityType.CAPABILITY,
            pattern="tasks_for_capability"
        )

        # Extract tasks
        tasks = [
            node.entity_data
            for node in result.nodes
            if node.entity_type == GraphEntityType.AI_TASK
        ]

        # Apply taxonomy filter
        if taxonomy:
            tasks = [t for t in tasks if getattr(t, 'isDefinedByTaxonomy', None) == taxonomy]

        return tasks

    # ========================================
    # CONVENIENCE METHODS: END-TO-END PATHS
    # ========================================

    def trace_task_to_intrinsics(
        self,
        task=None,
        task_id: Optional[str] = None,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trace from task → capabilities → intrinsics in one call.

        Returns:
            Dictionary with:
                - task: Task object
                - capabilities: List of required capabilities
                - intrinsics_by_capability: Dict mapping capability IDs to intrinsics
                - all_intrinsics: Flat list of all intrinsics

        Examples:
            result = explorer.trace_task_to_intrinsics(task_id="question-answering")
            print(f"Task: {result['task'].name}")
            print(f"Requires {len(result['capabilities'])} capabilities")
            print(f"Implemented by {len(result['all_intrinsics'])} intrinsics")
        """
        # Find the task
        if task:
            task_obj = task
        elif task_id:
            task_obj = next((t for t in self._tasks if t.id == task_id), None)
        elif tag:
            task_obj = next((t for t in self._tasks if getattr(t, 'tag', None) == tag), None)
        else:
            return {}

        if not task_obj:
            return {}

        # Use generic navigation with depth 2
        result = self.navigate(
            task_obj.id,
            GraphEntityType.AI_TASK,
            pattern="end_to_end_task_to_intrinsics"
        )

        # Parse result into structured format
        capabilities = []
        intrinsics_by_capability = {}
        all_intrinsics = []

        for node in result.nodes:
            if node.entity_type == GraphEntityType.CAPABILITY and node.depth == 1:
                capabilities.append(node.entity_data)
                intrinsics_by_capability[node.entity_data.id] = []

        for node in result.nodes:
            if node.entity_type in [GraphEntityType.LLM_INTRINSIC, GraphEntityType.ADAPTER]:
                if node.depth == 2 and node.parent_id:
                    # Find parent capability
                    if node.parent_id in intrinsics_by_capability:
                        intrinsics_by_capability[node.parent_id].append(node.entity_data)
                    all_intrinsics.append(node.entity_data)

        return {
            "task": task_obj,
            "capabilities": capabilities,
            "intrinsics_by_capability": intrinsics_by_capability,
            "all_intrinsics": all_intrinsics
        }

    # ========================================
    # UTILITY METHODS
    # ========================================

    def _infer_entity_type(self, entity_id: str) -> GraphEntityType:
        """
        Infer entity type from ID prefix or by searching collections.

        Args:
            entity_id: Entity ID

        Returns:
            Inferred GraphEntityType
        """
        # Try common ID prefixes
        if entity_id.startswith("ibm-cap-"):
            return GraphEntityType.CAPABILITY
        elif entity_id.startswith("aitask:"):
            return GraphEntityType.AI_TASK
        elif entity_id.startswith("ibm-risk-"):
            return GraphEntityType.RISK

        # Search through collections
        for entity_type, collection in self.navigator._entity_collections.items():
            if any(e.id == entity_id for e in collection):
                return entity_type

        # Default fallback
        return GraphEntityType.CAPABILITY

    def _get_entity_type(self, entity: Any) -> GraphEntityType:
        """
        Get entity type from object class name.

        Args:
            entity: Entity object

        Returns:
            GraphEntityType
        """
        class_name = entity.__class__.__name__

        # Map class names to entity types
        type_map = {
            "Risk": GraphEntityType.RISK,
            "RiskGroup": GraphEntityType.RISK_GROUP,
            "Action": GraphEntityType.ACTION,
            "RiskControl": GraphEntityType.RISK_CONTROL,
            "Capability": GraphEntityType.CAPABILITY,
            "CapabilityGroup": GraphEntityType.CAPABILITY_GROUP,
            "CapabilityDomain": GraphEntityType.CAPABILITY_DOMAIN,
            "AiTask": GraphEntityType.AI_TASK,
            "LLMIntrinsic": GraphEntityType.LLM_INTRINSIC,
            "Adapter": GraphEntityType.ADAPTER,
        }

        return type_map.get(class_name, GraphEntityType.CAPABILITY)

    # ========================================
    # CONVENIENCE METHODS: RISKS
    # ========================================

    def get_all_risks(self, taxonomy: Optional[str] = None) -> List[Any]:
        """Get all risk definitions, optionally filtered by taxonomy."""
        risks = self._risks
        if taxonomy:
            risks = [r for r in risks if getattr(r, 'isDefinedByTaxonomy', None) == taxonomy]
        return risks

    def get_risk(
        self,
        tag: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get a risk by tag, id, or name.

        Args:
            tag: Optional risk tag
            id: Optional risk ID
            name: Optional risk name
            taxonomy: Optional taxonomy filter

        Returns:
            Risk object or None if not found
        """
        risks = self._risks

        if tag:
            risks = [r for r in risks if getattr(r, 'tag', None) == tag]
        if id:
            risks = [r for r in risks if r.id == id]
        if name:
            risks = [r for r in risks if r.name == name]
        if taxonomy:
            risks = [r for r in risks if getattr(r, 'isDefinedByTaxonomy', None) == taxonomy]

        return risks[0] if risks else None

    def get_related_risks(
        self,
        risk=None,
        risk_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Get risks related via SKOS relationships.

        Args:
            risk: Optional risk object
            risk_id: Optional risk ID
            tag: Optional risk tag
            name: Optional risk name
            taxonomy: Optional taxonomy filter for results

        Returns:
            List of related Risk objects
        """
        # Find the risk
        if risk:
            risk_obj = risk
        elif risk_id:
            risk_obj = next((r for r in self._risks if r.id == risk_id), None)
        elif tag:
            risk_obj = next((r for r in self._risks if getattr(r, 'tag', None) == tag), None)
        elif name:
            risk_obj = next((r for r in self._risks if r.name == name), None)
        else:
            return []

        if not risk_obj:
            return []

        # Use generic navigation to find related risks
        result = self.navigate(
            risk_obj.id,
            GraphEntityType.RISK,
            pattern="related_risks"
        )

        # Extract related risks
        related = [
            node.entity_data
            for node in result.nodes
            if node.entity_type == GraphEntityType.RISK and node.depth > 0
        ]

        # Apply taxonomy filter
        if taxonomy:
            related = [r for r in related if getattr(r, 'isDefinedByTaxonomy', None) == taxonomy]

        return related

    def get_controls_for_risk(
        self,
        risk=None,
        risk_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Get risk controls for a specific risk.

        Args:
            risk: Optional risk object
            risk_id: Optional risk ID
            tag: Optional risk tag
            name: Optional risk name
            taxonomy: Optional taxonomy filter for results

        Returns:
            List of RiskControl objects
        """
        # Find the risk
        if risk:
            risk_obj = risk
        elif risk_id:
            risk_obj = next((r for r in self._risks if r.id == risk_id), None)
        elif tag:
            risk_obj = next((r for r in self._risks if getattr(r, 'tag', None) == tag), None)
        elif name:
            risk_obj = next((r for r in self._risks if r.name == name), None)
        else:
            return []

        if not risk_obj:
            return []

        # Use generic navigation
        result = self.navigate(
            risk_obj.id,
            GraphEntityType.RISK,
            pattern="controls_for_risk"
        )

        # Extract controls
        controls = [
            node.entity_data
            for node in result.nodes
            if node.entity_type == GraphEntityType.RISK_CONTROL
        ]

        # Apply taxonomy filter
        if taxonomy:
            controls = [c for c in controls if getattr(c, 'isDefinedByTaxonomy', None) == taxonomy]

        return controls

    def get_actions_for_risk(
        self,
        risk=None,
        risk_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Get actions for a specific risk.

        Args:
            risk: Optional risk object
            risk_id: Optional risk ID
            tag: Optional risk tag
            name: Optional risk name
            taxonomy: Optional taxonomy filter for results

        Returns:
            List of Action objects
        """
        # Find the risk
        if risk:
            risk_obj = risk
        elif risk_id:
            risk_obj = next((r for r in self._risks if r.id == risk_id), None)
        elif tag:
            risk_obj = next((r for r in self._risks if getattr(r, 'tag', None) == tag), None)
        elif name:
            risk_obj = next((r for r in self._risks if r.name == name), None)
        else:
            return []

        if not risk_obj:
            return []

        # Use generic navigation
        result = self.navigate(
            risk_obj.id,
            GraphEntityType.RISK,
            pattern="actions_for_risk"
        )

        # Extract actions
        actions = [
            node.entity_data
            for node in result.nodes
            if node.entity_type == GraphEntityType.ACTION
        ]

        # Apply taxonomy filter
        if taxonomy:
            actions = [a for a in actions if getattr(a, 'isDefinedByTaxonomy', None) == taxonomy]

        return actions

    # ========================================
    # CONVENIENCE METHODS: BENCHMARKS & EVALUATIONS
    # ========================================

    def get_all_benchmarks(self, taxonomy: Optional[str] = None) -> List[Any]:
        """Get all benchmark metadata cards, optionally filtered by taxonomy."""
        benchmarks = self._benchmarks
        if taxonomy:
            benchmarks = [b for b in benchmarks if getattr(b, 'isDefinedByTaxonomy', None) == taxonomy]
        return benchmarks

    def get_benchmark(self, id: str) -> Optional[Any]:
        """Get a specific benchmark by ID."""
        return next((b for b in self._benchmarks if b.id == id), None)

    # ========================================
    # CONVENIENCE METHODS: TASKS
    # ========================================

    def get_all_tasks(self, taxonomy: Optional[str] = None) -> List[Any]:
        """Get all AI task definitions, optionally filtered by taxonomy."""
        tasks = self._tasks
        if taxonomy:
            tasks = [t for t in tasks if getattr(t, 'isDefinedByTaxonomy', None) == taxonomy]
        return tasks

    def get_task(
        self,
        tag: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get a task by tag, id, or name.

        Args:
            tag: Optional task tag
            id: Optional task ID
            name: Optional task name
            taxonomy: Optional taxonomy filter

        Returns:
            AiTask object or None if not found
        """
        tasks = self._tasks

        if tag:
            tasks = [t for t in tasks if getattr(t, 'tag', None) == tag]
        if id:
            tasks = [t for t in tasks if t.id == id]
        if name:
            tasks = [t for t in tasks if t.name == name]
        if taxonomy:
            tasks = [t for t in tasks if getattr(t, 'isDefinedByTaxonomy', None) == taxonomy]

        return tasks[0] if tasks else None

    def get_intrinsics_for_task(
        self,
        task=None,
        task_id: Optional[str] = None,
        tag: Optional[str] = None,
        name: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[Any]:
        """
        Get intrinsics related to a task.

        Args:
            task: Optional task object
            task_id: Optional task ID
            tag: Optional task tag
            name: Optional task name
            taxonomy: Optional taxonomy filter for results

        Returns:
            List of LLMIntrinsic objects
        """
        # Find the task
        if task:
            task_obj = task
        elif task_id:
            task_obj = next((t for t in self._tasks if t.id == task_id), None)
        elif tag:
            task_obj = next((t for t in self._tasks if getattr(t, 'tag', None) == tag), None)
        elif name:
            task_obj = next((t for t in self._tasks if t.name == name), None)
        else:
            return []

        if not task_obj:
            return []

        # Use generic navigation
        result = self.navigate(
            task_obj.id,
            GraphEntityType.AI_TASK,
            pattern="intrinsics_for_task"
        )

        # Extract intrinsics
        intrinsics = [
            node.entity_data
            for node in result.nodes
            if node.entity_type == GraphEntityType.LLM_INTRINSIC
        ]

        # Apply taxonomy filter
        if taxonomy:
            intrinsics = [i for i in intrinsics if getattr(i, 'isDefinedByTaxonomy', None) == taxonomy]

        return intrinsics
