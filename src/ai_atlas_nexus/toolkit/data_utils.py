import glob
import os

from linkml_runtime.loaders import yaml_loader

from ai_atlas_nexus.ai_risk_ontology.datamodel.ai_risk_ontology import Container
from ai_atlas_nexus.data import get_data_path
from ai_atlas_nexus.toolkit.logging import configure_logger


logger = configure_logger(__name__)


def load_yamls_to_container(base_dir):
    """Function to load the AIAtlasNexus with data

    Args:
        base_dir: str
            (Optional) user defined base directory path

    Returns:
        YAMLRoot instance of the Container class
    """

    # Get system yaml data path
    system_data_path = get_data_path()

    master_yaml_files = []
    for yaml_dir in [system_data_path, base_dir]:
        # Include YAML files from the user defined `base_dir` if exist.
        if yaml_dir is not None:
            master_yaml_files.extend(
                glob.glob(os.path.join(yaml_dir, "**", "*.yaml"), recursive=True)
            )

    yml_items_result = {}
    for yaml_file in master_yaml_files:
        try:
            yml_items = yaml_loader.load_as_dict(source=yaml_file)
            for ontology_class, instances in yml_items.items():
                yml_items_result.setdefault(ontology_class, []).extend(instances)
        except Exception as e:
            logger.info(f"YAML ignored: {yaml_file}. Failed to load. {e}")

    # Helper function to combine entries with the same ID
    def combine_entities(entities):
        """Combine entities with the same ID by merging their attributes."""
        combined = {}
        for entity in entities:
            entity_id = entity["id"]

            if entity_id not in combined:
                combined[entity_id] = {"id": entity_id}

            for key, value in entity.items():
                if key != "id":
                    if key not in combined[entity_id]:
                        combined[entity_id][key] = value
                    else:
                        if combined[entity_id][key] is not None:
                            combined[entity_id][key] = [
                                *combined[entity_id][key],
                                *value,
                            ]
                        else:
                            combined[entity_id][key] = value

        return list(combined.values())

    # Combine entries for entity types that may have mappings split across multiple files
    entity_types_to_combine = ["risks", "capabilities", "aitasks", "adapters"]
    for entity_type in entity_types_to_combine:
        if entity_type in yml_items_result:
            yml_items_result[entity_type] = combine_entities(yml_items_result[entity_type])

    ontology = yaml_loader.load_any(
        source=yml_items_result,
        target_class=Container,
    )

    return ontology
