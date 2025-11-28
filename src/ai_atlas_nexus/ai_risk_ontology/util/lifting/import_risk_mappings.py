# Standard Library
from os import listdir
from os.path import isfile, join
from pathlib import Path

# Third Party
from linkml_runtime.dumpers import YAMLDumper
from pydantic import BaseModel
from sssom.parsers import parse_sssom_table

# Local
from ai_atlas_nexus.ai_risk_ontology import Container, Risk, Capability, AiTask, Adapter
from ai_atlas_nexus.toolkit.logging import configure_logger


MAP_DIR = "src/ai_atlas_nexus/data/mappings/"
DATA_DIR = "src/ai_atlas_nexus/data/knowledge_graph/mappings/"

logger = configure_logger(__name__)


class RiskMap(BaseModel):
    src_risk_id: str
    target_risk_id: str
    relationship: str

    def __init__(self, src_risk_id: str, target_risk_id: str, relationship: str):
        src_id = src_risk_id.split(":")[-1]
        target_id = target_risk_id.split(":")[-1]

        super().__init__(
            src_risk_id=src_id,
            target_risk_id=target_id,
            relationship=relationship,
        )


def process_mapping_from_tsv_to_risk_mapping(file_name):
    tsv_file_name = join(MAP_DIR, file_name)
    mapping_set_df = parse_sssom_table(file_path=tsv_file_name)
    ms = mapping_set_df.to_mapping_set()
    risk_maps = [
        RiskMap(
            **{
                "src_risk_id": item["subject_id"],
                "target_risk_id": item["object_id"],
                "relationship": item["predicate_id"],
            }
        )
        for item in ms.mappings
        if item["predicate_id"] != "noMatch"
    ]
    return risk_maps


def process_mappings_to_risks(risk_maps):
    output_risks = []
    for rm in risk_maps:

        s_id = rm.src_risk_id
        o_id = rm.target_risk_id
        risk = Risk(id=s_id)
        risk_for_inverse = Risk(id=o_id)

        relationship = rm.relationship
        if relationship == "skos:closeMatch":
            risk.closeMatch = [o_id]
            risk_for_inverse.closeMatch = [s_id]
        elif relationship == "skos:exactMatch":
            risk.exactMatch = [o_id]
            risk_for_inverse.exactMatch = [s_id]
        elif relationship == "skos:broadMatch":
            risk.broadMatch = [o_id]
            risk_for_inverse.narrowMatch = [s_id]
        elif relationship == "skos:narrowMatch":
            risk.narrowMatch = [o_id]
            risk_for_inverse.broadMatch = [s_id]
        elif relationship == "skos:relatedMatch":
            risk.relatedMatch = [o_id]
            risk_for_inverse.relatedMatch = [s_id]
        else:
            logger.info("Unparseable predicate_id: %s", relationship)

        output_risks.append(risk)
        output_risks.append(risk_for_inverse)

    return output_risks


def write_to_file(output_risks, output_file):
    with open(output_file, "+tw", encoding="utf-8") as output_file:
        print(YAMLDumper().dumps(Container(risks=output_risks)), file=output_file)
        output_file.close()


def process_capability_task_mappings(file_name):
    """Process capability→task mappings (nexus:requiredByTask)."""
    tsv_file_name = join(MAP_DIR, file_name)
    mapping_set_df = parse_sssom_table(file_path=tsv_file_name)
    ms = mapping_set_df.to_mapping_set()

    capabilities = []
    tasks = []

    for item in ms.mappings:
        if item["predicate_id"] != "nexus:requiredByTask":
            continue

        # Extract IDs (remove namespace prefix)
        cap_id = item["subject_id"].split(":")[-1]
        task_id = item["object_id"].split(":")[-1]

        # Create capability with requiredByTask relationship
        cap = Capability(id=cap_id, requiredByTask=[task_id])
        capabilities.append(cap)

        # Create task with requiresCapability relationship (inverse)
        task = AiTask(id=task_id, requiresCapability=[cap_id])
        tasks.append(task)

    return capabilities, tasks


def process_capability_adapter_mappings(file_name):
    """Process capability→adapter mappings (nexus:implementedByAdapter)."""
    tsv_file_name = join(MAP_DIR, file_name)
    mapping_set_df = parse_sssom_table(file_path=tsv_file_name)
    ms = mapping_set_df.to_mapping_set()

    capabilities = []
    adapters = []

    for item in ms.mappings:
        if item["predicate_id"] != "nexus:implementedByAdapter":
            continue

        # Extract IDs (remove namespace prefix)
        cap_id = item["subject_id"].split(":")[-1]
        adapter_id = item["object_id"].split(":")[-1]

        # Create capability with implementedByAdapter relationship
        cap = Capability(id=cap_id, implementedByAdapter=[adapter_id])
        capabilities.append(cap)

        # Create adapter with implementsCapability_adapter relationship (inverse)
        adapter = Adapter(id=adapter_id, implementsCapability_adapter=[cap_id])
        adapters.append(adapter)

    return capabilities, adapters


def write_capability_mappings_to_file(capabilities, tasks, adapters, output_file):
    """Write capability mappings to YAML file."""
    with open(output_file, "+tw", encoding="utf-8") as f:
        container = Container(
            capabilities=capabilities if capabilities else None,
            aitasks=tasks if tasks else None,
            adapters=adapters if adapters else None
        )
        print(YAMLDumper().dumps(container), file=f)
        f.close()


if __name__ == "__main__":
    logger.info(f"Processing mapping files in : %s", MAP_DIR)
    mapping_files = [
        file_name
        for file_name in listdir(MAP_DIR)
        if (file_name.endswith(".md") == False) and isfile(join(MAP_DIR, file_name))
    ]

    for file_name in mapping_files:
        output_file = DATA_DIR + Path(file_name).stem + "_from_tsv_data.yaml"

        # Handle capability→task mappings
        if "cap2task" in file_name:
            capabilities, tasks = process_capability_task_mappings(file_name)
            logger.info(
                f"Processed capability→task file: %s, %s capabilities, %s tasks",
                file_name,
                len(capabilities),
                len(tasks)
            )
            write_capability_mappings_to_file(capabilities, tasks, [], output_file)

        # Handle capability→adapter mappings
        elif "cap2intrinsic" in file_name:
            capabilities, adapters = process_capability_adapter_mappings(file_name)
            logger.info(
                f"Processed capability→adapter file: %s, %s capabilities, %s adapters",
                file_name,
                len(capabilities),
                len(adapters)
            )
            write_capability_mappings_to_file(capabilities, [], adapters, output_file)

        # Handle risk mappings (existing logic)
        else:
            rs = process_mapping_from_tsv_to_risk_mapping(file_name)
            logger.info(f"Processed risk mapping file: %s, %s valid entries", file_name, len(rs))
            output_risks = process_mappings_to_risks(rs)
            write_to_file(output_risks, output_file)
