"""Builds a star-shaped UseCaseKG from a text description.

Uses the existing AI Atlas Nexus identification methods (risk detection,
task identification, domain identification) to populate the knowledge graph
spokes. The result is a self-contained PKG that can be serialized, versioned,
and compared.

The builder works in two modes:
1. LLM-assisted: Uses an InferenceEngine to identify risks, tasks, and domains
   from the use case description text.
2. Manual: Accepts pre-specified factors for cases where the user has already
   determined the relevant entities.
"""

import logging
import uuid
from typing import Optional

from .types import UseCaseKG

logger = logging.getLogger(__name__)


class UseCaseBuilder:
    """Constructs UseCaseKG instances from text descriptions or manual input.

    Usage (LLM-assisted):
        builder = UseCaseBuilder(nexus=ran_lib)
        kg = builder.from_description(
            description="AI algorithm for making hiring decisions",
            locality=["EU"],
            ai_subjects=["job applicants"],
            inference_engine=engine,
        )

    Usage (manual):
        kg = builder.from_factors(
            description="AI algorithm for making hiring decisions",
            domains=["Human Resources"],
            purpose="making hiring decisions",
            capabilities=["multimodal analysis"],
            ai_subjects=["job applicants"],
            localities=["New York, US"],
            risk_ids=["atlas-lack-of-model-transparency", "atlas-discriminatory-actions"],
        )
    """

    def __init__(self, nexus=None):
        """Initialize the builder.

        Args:
            nexus: An AIAtlasNexus instance for LLM-assisted identification.
                   Not required for manual mode (from_factors).
        """
        self._nexus = nexus

    def from_factors(
        self,
        description: str,
        domains: Optional[list[str]] = None,
        purpose: Optional[str] = None,
        capabilities: Optional[list[str]] = None,
        ai_subjects: Optional[list[str]] = None,
        localities: Optional[list[str]] = None,
        risk_ids: Optional[list[str]] = None,
        action_ids: Optional[list[str]] = None,
        task_ids: Optional[list[str]] = None,
        stakeholder_ids: Optional[list[str]] = None,
        usecase_id: Optional[str] = None,
    ) -> UseCaseKG:
        """Build a UseCaseKG from explicitly provided factors.

        This is the manual mode — no LLM calls, no inference. Use this when
        you already know the relevant entities (e.g., from domain expertise
        or a previous LLM-assisted run).
        """
        return UseCaseKG(
            usecase_id=usecase_id or f"uc-{uuid.uuid4().hex[:8]}",
            description=description,
            domains=domains or [],
            purpose=purpose,
            capabilities=capabilities or [],
            ai_subjects=ai_subjects or [],
            localities=localities or [],
            risk_ids=risk_ids or [],
            action_ids=action_ids or [],
            task_ids=task_ids or [],
            stakeholder_ids=stakeholder_ids or [],
        )

    def from_description(
        self,
        description: str,
        inference_engine=None,
        taxonomy: Optional[str] = None,
        localities: Optional[list[str]] = None,
        ai_subjects: Optional[list[str]] = None,
        purpose: Optional[str] = None,
        usecase_id: Optional[str] = None,
    ) -> UseCaseKG:
        """Build a UseCaseKG by using the LLM to identify risks, tasks, and domains.

        Factors that can't be inferred from text alone (localities, ai_subjects)
        should be provided explicitly. The LLM identifies:
        - risks (via identify_risks_from_usecases)
        - tasks (via identify_ai_tasks_from_usecases)
        - domains (via identify_domain_from_usecases)

        Args:
            description: Free-text description of the use case.
            inference_engine: InferenceEngine for LLM calls. Required.
            taxonomy: Risk taxonomy ID (defaults to "ibm-risk-atlas").
            localities: Geographic jurisdictions (user-provided, not inferred).
            ai_subjects: Who is affected (user-provided, not inferred).
            purpose: Purpose statement (user-provided or extracted from text).
            usecase_id: Optional ID; auto-generated if not provided.
        """
        if self._nexus is None:
            raise ValueError(
                "UseCaseBuilder requires an AIAtlasNexus instance for "
                "LLM-assisted mode. Pass nexus= to the constructor."
            )
        if inference_engine is None:
            raise ValueError(
                "inference_engine is required for from_description(). "
                "Use from_factors() for manual construction."
            )

        uc_id = usecase_id or f"uc-{uuid.uuid4().hex[:8]}"
        logger.info("Building UseCaseKG %s from description", uc_id)

        # Identify risks
        risk_ids = []
        try:
            risk_results = self._nexus.identify_risks_from_usecases(
                usecases=[description],
                inference_engine=inference_engine,
                taxonomy=taxonomy,
            )
            if risk_results and risk_results[0]:
                risk_ids = [r.id for r in risk_results[0]]
                logger.info("Identified %d risks", len(risk_ids))
        except Exception as e:
            logger.warning("Risk identification failed: %s", e)

        # Identify tasks
        task_ids = []
        try:
            task_results = self._nexus.identify_ai_tasks_from_usecases(
                usecases=[description],
                inference_engine=inference_engine,
            )
            if task_results and task_results[0]:
                task_ids = task_results[0]
                logger.info("Identified %d tasks", len(task_ids))
        except Exception as e:
            logger.warning("Task identification failed: %s", e)

        # Identify domains
        domains = []
        try:
            domain_results = self._nexus.identify_domain_from_usecases(
                usecases=[description],
                inference_engine=inference_engine,
            )
            if domain_results and domain_results[0]:
                domains = domain_results[0]
                logger.info("Identified %d domains", len(domains))
        except Exception as e:
            logger.warning("Domain identification failed: %s", e)

        # Traverse risks to find related actions
        action_ids = []
        for rid in risk_ids:
            try:
                actions = self._nexus.get_related_actions(id=rid)
                if actions:
                    action_ids.extend(a.id for a in actions)
            except Exception:
                pass
        action_ids = list(set(action_ids))

        return UseCaseKG(
            usecase_id=uc_id,
            description=description,
            domains=domains,
            purpose=purpose,
            capabilities=[],  # extracted from tasks if needed
            ai_subjects=ai_subjects or [],
            localities=localities or [],
            risk_ids=risk_ids,
            action_ids=action_ids,
            task_ids=task_ids,
            stakeholder_ids=[],
        )
