# Convenience script to export a json graph version or IBM AI atlas nexus from the yaml
# in src/ai_atlas_nexus/data/knowledge_graph
from os import makedirs

from ai_atlas_nexus import AIAtlasNexus
from ai_atlas_nexus.ai_risk_ontology.util.json_graph_dumper import JSONGraphDumper
from ai_atlas_nexus.toolkit.logging import configure_logger


logger = configure_logger(__name__)

OUTPUT_DIR = "graph_export/json/"
OUTPUT_FILE = "ai-risk-ontology-sigma.json"
SCHEMA_FILE = "src/ai_atlas_nexus/ai_risk_ontology/schema/ai-risk-ontology.yaml"


if __name__ == "__main__":
    # export IBM AI risk atlas to latex
    ran = AIAtlasNexus()
    container = ran._ontology
    makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_DIR + OUTPUT_FILE, "+tw", encoding="utf-8") as output_file:
        print(JSONGraphDumper(schema_path=SCHEMA_FILE).dumps(container), file=output_file)
        output_file.close()
        logger.info("Graph Json output complete")
