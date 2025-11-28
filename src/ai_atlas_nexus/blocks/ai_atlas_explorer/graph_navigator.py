"""
Graph Navigator - Generic traversal engine for the knowledge graph.

Provides BFS-based graph traversal with configurable edge and node filtering.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import deque
import hashlib
import json

from .types import GraphEntityType, GraphRelationType


@dataclass
class NavigationConfig:
    """
    Configuration for graph traversal policies.

    Defines filtering rules and traversal behavior for graph navigation.
    """

    # Traversal depth
    max_depth: int = 2

    # Edge filtering policies
    included_relationships: Optional[List[GraphRelationType]] = None
    excluded_relationships: Optional[List[GraphRelationType]] = None

    # Entity type filtering
    included_entity_types: Optional[List[GraphEntityType]] = None
    excluded_entity_types: Optional[List[GraphEntityType]] = None

    # Property-based filtering
    node_property_filters: Optional[Dict[str, Any]] = None
    edge_property_filters: Optional[Dict[str, Any]] = None

    # Traversal behavior
    follow_bidirectional: bool = True
    deduplicate_results: bool = True
    max_results: Optional[int] = None
    cache_enabled: bool = True

    def allows_relationship(self, rel_type: GraphRelationType) -> bool:
        """Check if a relationship type is allowed by this config."""
        if self.excluded_relationships and rel_type in self.excluded_relationships:
            return False
        if self.included_relationships and rel_type not in self.included_relationships:
            return False
        return True

    def allows_entity_type(self, entity_type: GraphEntityType) -> bool:
        """Check if an entity type is allowed by this config."""
        if self.excluded_entity_types and entity_type in self.excluded_entity_types:
            return False
        if self.included_entity_types and entity_type not in self.included_entity_types:
            return False
        return True

    def matches_node_filters(self, node_data: Any) -> bool:
        """Check if a node matches property filters."""
        if not self.node_property_filters:
            return True

        for prop, expected_value in self.node_property_filters.items():
            # Handle both dictionary and object access
            if isinstance(node_data, dict):
                actual_value = node_data.get(prop)
            else:
                actual_value = getattr(node_data, prop, None)

            if actual_value != expected_value:
                return False
        return True

    def get_cache_key(self, start_id: str, start_type: GraphEntityType) -> str:
        """Generate a cache key for this configuration and starting point."""
        config_dict = {
            "start_id": start_id,
            "start_type": start_type.value,
            "max_depth": self.max_depth,
            "included_relationships": [r.value for r in self.included_relationships]
            if self.included_relationships
            else None,
            "excluded_relationships": [r.value for r in self.excluded_relationships]
            if self.excluded_relationships
            else None,
            "included_entity_types": [e.value for e in self.included_entity_types]
            if self.included_entity_types
            else None,
            "excluded_entity_types": [e.value for e in self.excluded_entity_types]
            if self.excluded_entity_types
            else None,
            "node_property_filters": self.node_property_filters,
            "follow_bidirectional": self.follow_bidirectional,
        }
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()


@dataclass
class TraversalNode:
    """
    A node discovered during graph traversal.

    Contains the entity data, metadata about how it was reached,
    and its position in the traversal tree.
    """

    entity_id: str
    entity_type: GraphEntityType
    entity_data: Any
    depth: int
    path: List[GraphRelationType] = field(default_factory=list)
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "depth": self.depth,
            "path": [r.value for r in self.path],
            "parent_id": self.parent_id,
        }


@dataclass
class TraversalResult:
    """
    Results from a graph traversal operation.

    Contains all discovered nodes, relationships, and metadata about the traversal.
    """

    nodes: List[TraversalNode]
    relationships: Dict[str, List[Tuple[GraphRelationType, str]]]
    depth_map: Dict[int, List[str]]
    statistics: Dict[str, Any]

    def get_nodes_at_depth(self, depth: int) -> List[TraversalNode]:
        """Get all nodes at a specific depth."""
        node_ids = self.depth_map.get(depth, [])
        return [n for n in self.nodes if n.entity_id in node_ids]

    def get_nodes_by_type(self, entity_type: GraphEntityType) -> List[TraversalNode]:
        """Get all nodes of a specific entity type."""
        return [n for n in self.nodes if n.entity_type == entity_type]

    def get_node(self, entity_id: str) -> Optional[TraversalNode]:
        """Get a specific node by ID."""
        for node in self.nodes:
            if node.entity_id == entity_id:
                return node
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "relationships": {
                k: [(r.value, t) for r, t in v] for k, v in self.relationships.items()
            },
            "depth_map": self.depth_map,
            "statistics": self.statistics,
        }


class GraphNavigator:
    """
    Generic graph traversal engine.

    Performs BFS traversal from any starting node with configurable
    filtering policies for edges, entity types, and properties.
    """

    def __init__(self, ontology):
        """
        Initialize the navigator.

        Args:
            ontology: The Risk Atlas Nexus ontology object
        """
        self.ontology = ontology
        self.cache: Dict[str, TraversalResult] = {}

        # Index all entity collections by type
        self._entity_collections = {
            GraphEntityType.RISK: ontology.risks or [],
            GraphEntityType.RISK_GROUP: ontology.riskgroups or [],
            GraphEntityType.RISK_TAXONOMY: ontology.taxonomies or [],
            GraphEntityType.RISK_CONTROL: ontology.riskcontrols or [],
            GraphEntityType.RISK_INCIDENT: ontology.riskincidents or [],
            GraphEntityType.ACTION: ontology.actions or [],
            GraphEntityType.AI_TASK: ontology.aitasks or [],
            GraphEntityType.CAPABILITY: ontology.capabilities or [],
            GraphEntityType.CAPABILITY_GROUP: ontology.capabilitygroups or [],
            GraphEntityType.CAPABILITY_DOMAIN: ontology.capabilitydomains or [],
            GraphEntityType.CAPABILITY_TAXONOMY: ontology.capabilitytaxonomies or [],
            GraphEntityType.LLM_INTRINSIC: ontology.llmintrinsics or [],
            GraphEntityType.ADAPTER: ontology.adapters or [],
            GraphEntityType.BENCHMARK: ontology.benchmarkmetadatacards or [],
            GraphEntityType.EVALUATION: ontology.evaluations or [],
            GraphEntityType.AI_EVAL_RESULT: ontology.aievalresults or [],
            GraphEntityType.STAKEHOLDER: ontology.stakeholders or [],
            GraphEntityType.STAKEHOLDER_GROUP: ontology.stakeholdergroups or [],
            GraphEntityType.DOCUMENT: ontology.documents or [],
            GraphEntityType.DATASET: ontology.datasets or [],
            GraphEntityType.PRINCIPLE: ontology.principles or [],
            GraphEntityType.POLICY: ontology.llmquestionpolicies or [],
            GraphEntityType.RULE: ontology.rules or [],
            GraphEntityType.LICENSE: ontology.licenses or [],
            GraphEntityType.ORGANIZATION: ontology.organizations or [],
        }

    def traverse_from_node(
        self,
        start_id: str,
        start_type: GraphEntityType,
        config: NavigationConfig,
    ) -> TraversalResult:
        """
        Traverse the graph from a starting node using BFS.

        Args:
            start_id: The ID of the starting node
            start_type: The type of the starting node
            config: Navigation configuration defining filtering policies

        Returns:
            TraversalResult containing all discovered nodes and relationships
        """
        # Check cache if enabled
        if config.cache_enabled:
            cache_key = config.get_cache_key(start_id, start_type)
            if cache_key in self.cache:
                return self.cache[cache_key]

        # Initialize traversal state
        visited: Set[str] = set()
        nodes: List[TraversalNode] = []
        relationships: Dict[str, List[Tuple[GraphRelationType, str]]] = {}
        depth_map: Dict[int, List[str]] = {}
        queue = deque()

        # Get starting node
        start_node = self._get_node(start_id, start_type)
        if not start_node:
            return self._empty_result()

        # Add start node to queue
        start_traversal_node = TraversalNode(
            entity_id=start_id,
            entity_type=start_type,
            entity_data=start_node,
            depth=0,
            path=[],
            parent_id=None,
        )

        queue.append(start_traversal_node)
        visited.add(start_id)

        # BFS traversal
        while queue and (config.max_results is None or len(nodes) < config.max_results):
            current = queue.popleft()

            # Check if we should include this node
            if config.allows_entity_type(current.entity_type) and config.matches_node_filters(
                current.entity_data
            ):
                nodes.append(current)
                depth_map.setdefault(current.depth, []).append(current.entity_id)

            # Don't explore beyond max depth
            if current.depth >= config.max_depth:
                continue

            # Get outgoing edges
            edges = self._get_edges(current.entity_id, current.entity_type)

            for rel_type, target_id, target_type, target_data in edges:
                # Check if relationship is allowed
                if not config.allows_relationship(rel_type):
                    continue

                # Skip if already visited (deduplication)
                if config.deduplicate_results and target_id in visited:
                    continue

                visited.add(target_id)

                # Record relationship
                relationships.setdefault(current.entity_id, []).append((rel_type, target_id))

                # Create traversal node for target
                target_traversal_node = TraversalNode(
                    entity_id=target_id,
                    entity_type=target_type,
                    entity_data=target_data,
                    depth=current.depth + 1,
                    path=current.path + [rel_type],
                    parent_id=current.entity_id,
                )

                queue.append(target_traversal_node)

        # Build result
        statistics = {
            "nodes_visited": len(visited),
            "nodes_returned": len(nodes),
            "max_depth_reached": max(depth_map.keys()) if depth_map else 0,
            "relationships_traversed": sum(len(v) for v in relationships.values()),
        }

        result = TraversalResult(
            nodes=nodes,
            relationships=relationships,
            depth_map=depth_map,
            statistics=statistics,
        )

        # Cache result if enabled
        if config.cache_enabled:
            cache_key = config.get_cache_key(start_id, start_type)
            self.cache[cache_key] = result

        return result

    def clear_cache(self):
        """Clear the traversal cache."""
        self.cache.clear()

    def _get_node(self, node_id: str, node_type: GraphEntityType) -> Optional[Any]:
        """
        Retrieve a node from the ontology.

        Args:
            node_id: Node ID to retrieve
            node_type: Type of the node

        Returns:
            Node object if found, None otherwise
        """
        collection = self._entity_collections.get(node_type, [])
        for entity in collection:
            if entity.id == node_id:
                return entity
        return None

    def _get_edges(
        self, node_id: str, node_type: GraphEntityType
    ) -> List[Tuple[GraphRelationType, str, GraphEntityType, Any]]:
        """
        Retrieve outgoing edges from a node.

        Returns a list of tuples: (relationship_type, target_id, target_type, target_data)

        This method introspects the LinkML object to find all relationship
        properties and their targets, plus loads relationships from TSV mappings.
        """
        node = self._get_node(node_id, node_type)
        if not node:
            return []

        edges = []

        # 1. Handle TSV mapping relationships (cap2task, cap2intrinsic)
        edges.extend(self._get_mapping_edges(node_id, node_type))

        # 2. Handle LinkML object relationships
        edges.extend(self._get_linkml_edges(node, node_type))

        return edges

    def _get_mapping_edges(
        self, node_id: str, node_type: GraphEntityType
    ) -> List[Tuple[GraphRelationType, str, GraphEntityType, Any]]:
        """Get edges from ontology relationships."""
        edges = []
        node = self._get_node(node_id, node_type)
        if not node:
            return edges

        # Task → Capability mappings
        if node_type == GraphEntityType.AI_TASK:
            # Get capabilities required by this task
            cap_ids = getattr(node, 'requiresCapability', None) or []
            for cap_id in cap_ids:
                cap = self._get_node(cap_id, GraphEntityType.CAPABILITY)
                if cap:
                    edges.append((
                        GraphRelationType.REQUIRES_CAPABILITY,
                        cap_id,
                        GraphEntityType.CAPABILITY,
                        cap
                    ))

        # Capability → Task mappings (inverse)
        if node_type == GraphEntityType.CAPABILITY:
            # Get tasks that require this capability
            task_ids = getattr(node, 'requiredByTask', None) or []
            for task_id in task_ids:
                task = self._get_node(task_id, GraphEntityType.AI_TASK)
                if task:
                    edges.append((
                        GraphRelationType.REQUIRED_BY_TASK,
                        task_id,
                        GraphEntityType.AI_TASK,
                        task
                    ))

            # Get adapters that implement this capability
            adapter_ids = getattr(node, 'implementedByAdapter', None) or []
            for adapter_id in adapter_ids:
                adapter = self._get_node(adapter_id, GraphEntityType.ADAPTER)
                if adapter:
                    edges.append((
                        GraphRelationType.IMPLEMENTED_BY_ADAPTER,
                        adapter_id,
                        GraphEntityType.ADAPTER,
                        adapter
                    ))

            # Get intrinsics that implement this capability
            intrinsic_ids = getattr(node, 'implementedByIntrinsic', None) or []
            for intrinsic_id in intrinsic_ids:
                intrinsic = self._get_node(intrinsic_id, GraphEntityType.LLM_INTRINSIC)
                if intrinsic:
                    edges.append((
                        GraphRelationType.IMPLEMENTED_BY_INTRINSIC,
                        intrinsic_id,
                        GraphEntityType.LLM_INTRINSIC,
                        intrinsic
                    ))

        # Adapter → Capability mappings (inverse)
        if node_type == GraphEntityType.ADAPTER:
            # Get capabilities implemented by this adapter
            cap_ids = getattr(node, 'implementsCapability_adapter', None) or []
            for cap_id in cap_ids:
                cap = self._get_node(cap_id, GraphEntityType.CAPABILITY)
                if cap:
                    edges.append((
                        GraphRelationType.IMPLEMENTS_CAPABILITY,
                        cap_id,
                        GraphEntityType.CAPABILITY,
                        cap
                    ))

        # LLMIntrinsic → Capability mappings (inverse)
        if node_type == GraphEntityType.LLM_INTRINSIC:
            # Get capabilities implemented by this intrinsic
            cap_ids = getattr(node, 'implementsCapability_intrinsic', None) or []
            for cap_id in cap_ids:
                cap = self._get_node(cap_id, GraphEntityType.CAPABILITY)
                if cap:
                    edges.append((
                        GraphRelationType.IMPLEMENTS_CAPABILITY,
                        cap_id,
                        GraphEntityType.CAPABILITY,
                        cap
                    ))

        return edges

    def _get_linkml_edges(
        self, node: Any, node_type: GraphEntityType
    ) -> List[Tuple[GraphRelationType, str, GraphEntityType, Any]]:
        """Get edges from LinkML object relationships."""
        edges = []

        # Helper function to add edges for a relationship
        def add_edges(attr_name: str, rel_type: GraphRelationType, target_type: GraphEntityType):
            if hasattr(node, attr_name):
                attr_value = getattr(node, attr_name)
                if attr_value:
                    # Handle both single values and lists
                    targets = attr_value if isinstance(attr_value, list) else [attr_value]
                    for target_id in targets:
                        if isinstance(target_id, str):
                            target = self._get_node(target_id, target_type)
                            if target:
                                edges.append((rel_type, target_id, target_type, target))

        # Risk relationships
        if node_type == GraphEntityType.RISK:
            add_edges('hasRelatedAction', GraphRelationType.HAS_RELATED_ACTION, GraphEntityType.ACTION)
            add_edges('isDetectedBy', GraphRelationType.IS_DETECTED_BY, GraphEntityType.RISK_CONTROL)

            # SKOS relationships
            add_edges('exactMatch', GraphRelationType.EXACT_MATCH, GraphEntityType.RISK)
            add_edges('closeMatch', GraphRelationType.CLOSE_MATCH, GraphEntityType.RISK)
            add_edges('broadMatch', GraphRelationType.BROAD_MATCH, GraphEntityType.RISK)
            add_edges('narrowMatch', GraphRelationType.NARROW_MATCH, GraphEntityType.RISK)
            add_edges('relatedMatch', GraphRelationType.RELATED_MATCH, GraphEntityType.RISK)

        # Capability relationships
        if node_type == GraphEntityType.CAPABILITY:
            add_edges('isPartOf', GraphRelationType.IS_PART_OF, GraphEntityType.CAPABILITY_GROUP)

            # SKOS relationships for capabilities
            add_edges('exactMatch', GraphRelationType.EXACT_MATCH, GraphEntityType.CAPABILITY)
            add_edges('closeMatch', GraphRelationType.CLOSE_MATCH, GraphEntityType.CAPABILITY)
            add_edges('broadMatch', GraphRelationType.BROAD_MATCH, GraphEntityType.CAPABILITY)
            add_edges('narrowMatch', GraphRelationType.NARROW_MATCH, GraphEntityType.CAPABILITY)
            add_edges('relatedMatch', GraphRelationType.RELATED_MATCH, GraphEntityType.CAPABILITY)

        # Capability Group relationships
        if node_type == GraphEntityType.CAPABILITY_GROUP:
            add_edges('hasPart', GraphRelationType.HAS_PART, GraphEntityType.CAPABILITY)
            add_edges('belongsToDomain', GraphRelationType.BELONGS_TO_DOMAIN, GraphEntityType.CAPABILITY_DOMAIN)

        # Capability Domain relationships
        if node_type == GraphEntityType.CAPABILITY_DOMAIN:
            add_edges('hasPart', GraphRelationType.HAS_PART, GraphEntityType.CAPABILITY_GROUP)

        # Documentation relationships (common to many types)
        add_edges('hasDocumentation', GraphRelationType.HAS_DOCUMENTATION, GraphEntityType.DOCUMENT)
        add_edges('hasLicense', GraphRelationType.HAS_LICENSE, GraphEntityType.LICENSE)

        # AI Task relationships
        if node_type == GraphEntityType.AI_TASK:
            add_edges('hasRelatedLLMIntrinsic', GraphRelationType.HAS_RELATED_LLMINTRINSIC, GraphEntityType.LLM_INTRINSIC)

        # Policy relationships
        if node_type == GraphEntityType.POLICY:
            add_edges('hasRule', GraphRelationType.HAS_RULE, GraphEntityType.RULE)

        return edges

    def _empty_result(self) -> TraversalResult:
        """Create an empty traversal result."""
        return TraversalResult(
            nodes=[],
            relationships={},
            depth_map={},
            statistics={
                "nodes_visited": 0,
                "nodes_returned": 0,
                "max_depth_reached": 0,
                "relationships_traversed": 0,
            },
        )
