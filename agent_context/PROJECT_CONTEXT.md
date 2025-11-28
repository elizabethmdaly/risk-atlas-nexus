# AI Atlas Nexus - Project Context Summary

## What Problem Does This Code Solve?

### The AI Governance Challenge

Organizations building AI systems face a fragmented landscape of AI risk frameworks and governance resources:

**Problem 1: Multiple Disconnected Taxonomies**
- IBM AI Risk Atlas defines 99 risks
- NIST AI RMF defines different categorizations
- OWASP has Top 10 for LLMs
- MIT AI Risk Repository uses yet another taxonomy
- AIR 2024 taxonomy has 314 risks
- Each framework uses different terminology and structures

**Problem 2: Manual Risk Assessment**
- Teams must manually review use cases against risk frameworks
- Time-consuming and error-prone
- Requires deep expertise in each taxonomy
- Difficult to map risks across frameworks

**Problem 3: Scattered Resources**
- Risk definitions separated from mitigation actions
- Benchmarks and evaluations not linked to risks
- No unified view of related governance resources
- Hard to find applicable controls and best practices

### The Solution

**AI Atlas Nexus** provides:

1. **Unified Knowledge Graph**
   - Combines 11+ taxonomies into one coherent ontology
   - 556 risks, 254 actions, 17 controls, 26 principles
   - Cross-taxonomy mappings showing relationships
   - Single query interface for all resources

2. **Automated Risk Identification**
   - LLM-powered analysis of use case descriptions
   - Identifies applicable risks from any taxonomy
   - Chain-of-Thought reasoning for explainability
   - Supports multiple LLM providers

3. **Governance Workflows**
   - Risk severity categorization (EU AI Act compliance)
   - Questionnaire auto-completion
   - Risk mapping between taxonomies
   - AI task and domain identification

4. **Extensible Platform**
   - Easy to add new taxonomies
   - Pluggable LLM providers
   - Community-driven curation
   - Open source (Apache 2.0)

### Real-World Impact

**Before AI Atlas Nexus**:
```
Developer: "I'm building a chatbot. What are the risks?"
→ Manually review IBM Risk Atlas (99 risks)
→ Check NIST AI RMF (separate framework)
→ Look at OWASP Top 10 for LLMs
→ Find overlaps between frameworks manually
→ Search for relevant mitigations separately
→ Time: Hours to days
```

**With AI Atlas Nexus**:
```python
from ai_atlas_nexus import AIAtlasNexus
from ai_atlas_nexus.blocks.inference import OllamaInferenceEngine

ran = AIAtlasNexus()
engine = OllamaInferenceEngine(...)

# Automated risk identification
risks = ran.identify_risks_from_usecases(
    usecases=["Building a customer service chatbot..."],
    inference_engine=engine,
    taxonomy="ibm-risk-atlas"
)

# Get related mitigations
for risk in risks[0]:
    actions = ran.get_related_actions(id=risk.id)
    controls = ran.get_related_risk_controls(id=risk.id)

# Time: Seconds to minutes
```

---

## Who Are the Users and Stakeholders?

### Primary Users

**1. AI/ML Developers**
- **Need**: Quickly identify risks in their AI systems
- **Use**: Risk identification APIs, related actions
- **Value**: Avoid building unsafe systems, comply with governance

**2. AI Governance Teams**
- **Need**: Assess AI systems for compliance (EU AI Act, internal policies)
- **Use**: Risk categorization, severity assessment, questionnaires
- **Value**: Systematic risk management, audit trails

**3. AI Safety Researchers**
- **Need**: Study relationships between risk taxonomies
- **Use**: Cross-taxonomy mappings, knowledge graph navigation
- **Value**: Understanding risk landscape, taxonomy alignment

**4. Product Managers**
- **Need**: Understand risk implications of product features
- **Use**: Use case analysis, risk-to-mitigation workflows
- **Value**: Informed decision-making, stakeholder communication

### Secondary Users

**5. Compliance Officers**
- **Need**: Demonstrate compliance with regulations
- **Use**: EU AI Act categorization, documentation generation
- **Value**: Regulatory compliance, risk documentation

**6. Taxonomy Creators**
- **Need**: Integrate their taxonomy into the ecosystem
- **Use**: Conversion utilities, mapping tools
- **Value**: Broader adoption, community engagement

**7. Tool Builders**
- **Need**: Build AI governance tools on top of the platform
- **Use**: Python library, knowledge graph, LLM integrations
- **Value**: Rapid development, standardized data

### Stakeholders

**IBM Research**
- Project originated from IBM
- Sponsors ongoing development
- Uses in internal AI governance

**Open Source Community**
- Contributors adding new taxonomies
- Users providing feedback
- Developers extending functionality

**Standards Bodies**
- NIST, OWASP, etc. whose frameworks are integrated
- Potential standardization of cross-taxonomy mappings

**Regulators** (indirect)
- EU AI Act compliance workflows
- Transparent AI governance processes

---

## Main Entry Points

### 1. Python Library API

**Primary entry point** for most users:

```python
from ai_atlas_nexus import AIAtlasNexus

# Initialize library
ran = AIAtlasNexus()

# Entry point: Risk exploration
risk = ran.get_risk(id="atlas-toxic-output")

# Entry point: Risk identification
risks = ran.identify_risks_from_usecases(
    usecases=["Use case description..."],
    inference_engine=engine
)

# Entry point: Graph navigation
related = ran.get_related_risks(id="atlas-toxic-output")
```

**File**: `src/ai_atlas_nexus/library.py`
**Class**: `AIAtlasNexus`
**Methods**: 50+ public methods

### 2. Jupyter Notebooks

**Educational entry point** for learning the library:

**Location**: `docs/examples/notebooks/`

**Key notebooks**:
- `AI_Atlas_Nexus_Quickstart.ipynb` - Overview and basics
- `risk_identification.ipynb` - Risk detection workflows
- `autoassist_questionnaire.ipynb` - Questionnaire automation
- `risk_categorization.ipynb` - Severity assessment
- `ai_tasks_identification.ipynb` - Task detection

### 3. Command-Line Tools (via Makefile)

**Automation entry point** for data regeneration:

```bash
# Regenerate documentation
make regenerate_documentation

# Export knowledge graph
make regenerate_graph_output

# Generate Cypher queries for Neo4j
make regenerate_cypher_code

# Validate schema
make lint_schema
```

### 4. HuggingFace Demo

**Interactive entry point** for non-programmers:

**URL**: https://huggingface.co/spaces/ibm/risk-atlas-nexus

Web interface for:
- Risk identification
- Taxonomy browsing
- Benchmark exploration

### 5. Data Files (for direct access)

**Data entry point** for advanced users:

```bash
# Knowledge graph instance data
src/ai_atlas_nexus/data/knowledge_graph/*.yaml

# Cross-taxonomy mappings
src/ai_atlas_nexus/data/mappings/*.tsv

# LinkML schema
src/ai_atlas_nexus/ai_risk_ontology/schema/ai-risk-ontology.yaml
```

---

## Critical Paths Through the Code

### Critical Path 1: Library Initialization

**User action**: `ran = AIAtlasNexus()`

**Code flow**:
```
1. AIAtlasNexus.__init__()
   └─> src/ai_atlas_nexus/library.py:76

2. load_yamls_to_container(base_dir)
   └─> src/ai_atlas_nexus/toolkit/data_utils.py:18

   a. Get system data path
      └─> src/ai_atlas_nexus/data/knowledge_graph/

   b. Glob all *.yaml files
      └─> ~25 YAML files discovered

   c. For each file:
      - Load with LinkML YAML loader
      - Parse into Container structure
      - Merge risks with same ID

   d. Return Container with:
      - risks: List[Risk] (556 items)
      - actions: List[Action] (254 items)
      - taxonomies: List[RiskTaxonomy] (11 items)
      - ... (10+ more collections)

3. Initialize explorers
   ├─> RiskExplorer(ontology)
   │   └─> src/ai_atlas_nexus/blocks/risk_explorer/explorer.py
   │       - Stores references to all collections
   │       - Prepares for fast in-memory queries
   │
   └─> AtlasExplorer(ontology)
       └─> src/ai_atlas_nexus/blocks/ai_atlas_explorer/atlas_explorer.py
           - Initializes GraphNavigator
           - Sets up pattern-based queries

4. Return initialized AIAtlasNexus instance
```

**Key files**:
- `src/ai_atlas_nexus/library.py`
- `src/ai_atlas_nexus/toolkit/data_utils.py`
- `src/ai_atlas_nexus/blocks/risk_explorer/explorer.py`

---

### Critical Path 2: Risk Identification from Use Case

**User action**: `ran.identify_risks_from_usecases(...)`

**Code flow**:
```
1. AIAtlasNexus.identify_risks_from_usecases()
   └─> src/ai_atlas_nexus/library.py:493

   Validate inputs:
   - usecases: List[str]
   - inference_engine: InferenceEngine
   - taxonomy: str (default "ibm-risk-atlas")
   - zero_shot_only: bool

2. Get risks for taxonomy
   └─> risks = self.get_all_risks(taxonomy=taxonomy)
       - Filters 556 total risks to taxonomy subset
       - Returns List[Risk] for specified taxonomy

3. Create GenericRiskDetector
   └─> src/ai_atlas_nexus/blocks/risk_detector/generic.py:18

   Initialize with:
   - _risks: List[Risk] for taxonomy
   - _examples: CoT examples (if few-shot)
   - inference_engine: LLM provider

4. Call detector.detect(usecases)
   └─> GenericRiskDetector.detect()

   a. Build prompts
      ├─> If zero_shot_only:
      │   └─> ZeroShotPromptBuilder
      │       └─> src/ai_atlas_nexus/blocks/prompt_builder.py:10
      │           - Use RISK_IDENTIFICATION_TEMPLATE
      │           - Inject: risk list, usecase
      │
      └─> Else (few-shot):
          └─> FewShotPromptBuilder
              - Use template with CoT examples
              - Include reasoning steps

   b. Call inference engine
      └─> inference_engine.generate(prompts)

          Example: OllamaInferenceEngine.generate()
          └─> src/ai_atlas_nexus/blocks/inference/ollama.py:62

              - Send to Ollama server
              - Request JSON response with schema
              - Parse response
              - Return TextGenerationInferenceOutput

   c. Post-process responses
      └─> src/ai_atlas_nexus/blocks/inference/postprocessing.py:8
          - Extract risk names from JSON
          - Validate against schema
          - Handle errors/retries

   d. Filter risk objects
      - Match extracted names to Risk objects
      - Return List[Risk] for each usecase

5. Return results
   └─> List[List[Risk]]
       - One list per usecase
       - Each list contains Risk objects
```

**Key files**:
- `src/ai_atlas_nexus/library.py:493` (entry point)
- `src/ai_atlas_nexus/blocks/risk_detector/generic.py` (detection logic)
- `src/ai_atlas_nexus/blocks/prompt_builder.py` (prompt construction)
- `src/ai_atlas_nexus/blocks/inference/ollama.py` (LLM call)
- `src/ai_atlas_nexus/blocks/inference/postprocessing.py` (response handling)

---

### Critical Path 3: Cross-Taxonomy Risk Navigation

**User action**: `ran.get_related_risks(id="atlas-toxic-output")`

**Code flow**:
```
1. AIAtlasNexus.get_related_risks()
   └─> src/ai_atlas_nexus/library.py:270

   Validate inputs:
   - id: Optional[str]
   - tag: Optional[str]
   - taxonomy: Optional[str]

2. Delegate to RiskExplorer
   └─> RiskExplorer.get_related_risks()
       └─> src/ai_atlas_nexus/blocks/risk_explorer/explorer.py:197

       a. Find source risk
          └─> self.get_risk(id=id, tag=tag, taxonomy=taxonomy)
              - Search self._risks list
              - Match on id, tag, or taxonomy
              - Return Risk object

       b. Extract relationship IDs
          └─> Check risk attributes for SKOS relationships:
              - exactMatch: List[str]
              - closeMatch: List[str]
              - broadMatch: List[str]
              - narrowMatch: List[str]
              - relatedMatch: List[str]

              Example Risk object:
              Risk(
                  id="atlas-toxic-output",
                  relatedMatch=[
                      "shieldgemma-hate-speech",
                      "owasp-llm-06-sensitive-info-disclosure"
                  ]
              )

       c. Look up related risks
          └─> For each related_id in relationships:
              - Search self._risks for id == related_id
              - Collect matching Risk objects

       d. Return deduplicated list
          └─> List[Risk] (all related risks)

3. Return results to caller
```

**Key files**:
- `src/ai_atlas_nexus/library.py:270` (public API)
- `src/ai_atlas_nexus/blocks/risk_explorer/explorer.py:197` (relationship logic)

**Data source**:
- Relationships defined in mapping YAML files
- Example: `src/ai_atlas_nexus/data/knowledge_graph/mappings/ibm2owasp_from_tsv_data.yaml`

---

### Critical Path 4: Graph Traversal (Generic Navigation)

**User action**: `ran.navigate_graph(start_id, start_type, pattern="...")`

**Code flow**:
```
1. AIAtlasNexus.navigate_graph()
   └─> src/ai_atlas_nexus/library.py:795

   Validate inputs:
   - start_id: str
   - start_type: GraphEntityType
   - pattern: Optional[str]
   - max_depth: int (default 1)
   - included_relationships: List[GraphRelationType]

2. Delegate to AtlasExplorer
   └─> AtlasExplorer.navigate()
       └─> src/ai_atlas_nexus/blocks/ai_atlas_explorer/atlas_explorer.py:163

       a. Get NavigationConfig
          ├─> If pattern specified:
          │   └─> Load from query_patterns.py
          │       └─> src/ai_atlas_nexus/blocks/ai_atlas_explorer/query_patterns.py
          │
          │           Example pattern "capabilities_for_task":
          │           NavigationConfig(
          │               max_depth=2,
          │               included_entity_types=[CAPABILITY],
          │               included_relationships=[REQUIRES_CAPABILITY]
          │           )
          │
          └─> Else:
              └─> Build custom NavigationConfig
                  - Use provided max_depth
                  - Use included_relationships

       b. Call GraphNavigator
          └─> GraphNavigator.traverse()
              └─> src/ai_atlas_nexus/blocks/ai_atlas_explorer/graph_navigator.py:88

              BFS Algorithm:

              - Initialize:
                queue = [(start_id, start_type, 0)]
                visited = set()
                nodes = {}
                edges = []

              - While queue not empty:
                1. Pop (current_id, current_type, depth)
                2. If depth > max_depth: skip
                3. Get entity from ontology
                4. Add to nodes
                5. For each attribute of entity:
                   - If attribute is relationship:
                     - Check if relationship in config
                     - Get related entity
                     - Add edge: (current_id, related_id, relationship)
                     - Add related entity to queue
                6. Mark as visited

              - Return NavigationResult:
                nodes: Dict[str, Any]
                edges: List[Tuple]
                paths: List[List]

3. Return NavigationResult to caller
```

**Key files**:
- `src/ai_atlas_nexus/library.py:795` (public API)
- `src/ai_atlas_nexus/blocks/ai_atlas_explorer/atlas_explorer.py:163` (delegation)
- `src/ai_atlas_nexus/blocks/ai_atlas_explorer/graph_navigator.py:88` (BFS algorithm)
- `src/ai_atlas_nexus/blocks/ai_atlas_explorer/query_patterns.py` (named patterns)
- `src/ai_atlas_nexus/blocks/ai_atlas_explorer/types.py` (enums)

---

### Critical Path 5: Severity Categorization (EU AI Act)

**User action**: `ran.categorize_risk_severity(usecase, inference_engine)`

**Code flow**:
```
1. AIAtlasNexus.categorize_risk_severity()
   └─> src/ai_atlas_nexus/library.py:849

   Input: usecase (str), inference_engine

2. Step 1: Identify domain
   └─> domain = self.identify_domain_from_usecases([usecase], engine)
       - Uses LLM to classify domain
       - Returns domain category

3. Step 2: Generate questionnaire responses
   └─> responses = self.generate_few_shot_risk_questionnaire_output(
           usecases=[usecase],
           domains=[domain],
           inference_engine=engine
       )

       - Uses questionnaire prompt template
       - LLM answers EU AI Act compliance questions
       - Returns structured responses

4. Step 3: Categorize severity
   └─> RiskSeverityCategorizer.categorize()
       └─> src/ai_atlas_nexus/blocks/risk_categorization/severity.py:23

       EU AI Act 5-tier classification:

       - Parse questionnaire responses
       - Check criteria:
         1. Excluded (e.g., military use)
         2. Prohibited (e.g., social scoring)
         3. High-Risk Exception (listed in Annex III)
         4. High Risk (listed uses)
         5. Limited/Low Risk (default)

       - Return classification with reasoning

5. Return RiskCategory result
```

**Key files**:
- `src/ai_atlas_nexus/library.py:849` (orchestration)
- `src/ai_atlas_nexus/blocks/risk_categorization/severity.py` (classification logic)
- `src/ai_atlas_nexus/blocks/prompt_templates.py` (questionnaire prompts)

---

## External Dependencies and APIs Used

### 1. LinkML Ecosystem

**Purpose**: Schema definition and data validation

**Dependencies**:
- `linkml` - Schema toolkit
- `linkml_runtime` - YAML loading, dumping
- `linkml-runtime.utils` - SchemaView, validators

**How used**:
```python
# Load schema
from linkml_runtime import SchemaView
schema_view = SchemaView("ai-risk-ontology.yaml")

# Load instance data
from linkml_runtime.loaders import yaml_loader
container = yaml_loader.load("risk_atlas_data.yaml", Container)

# Dump to YAML
from linkml_runtime.dumpers import YAMLDumper
YAMLDumper().dump(container, "output.yaml")
```

**Key files using LinkML**:
- `src/ai_atlas_nexus/library.py:69` (schema loading)
- `src/ai_atlas_nexus/toolkit/data_utils.py:33` (YAML loading)
- All conversion utilities in `ai_risk_ontology/util/`

---

### 2. Pydantic

**Purpose**: Runtime data validation and serialization

**Dependency**: `pydantic>=2.0`

**How used**:
- Auto-generated datamodel uses Pydantic BaseModel
- Request/response validation in inference engines
- Parameter validation

```python
from pydantic import BaseModel

class TextGenerationInferenceOutput(BaseModel):
    generated_text: str
    input_text: Optional[str]
    generated_token_count: Optional[int]
```

**Key files**:
- `src/ai_atlas_nexus/ai_risk_ontology/datamodel/ai_risk_ontology.py` (generated models)
- `src/ai_atlas_nexus/blocks/inference/params.py` (parameter models)

---

### 3. SSSOM (Semantic Mapping)

**Purpose**: Standard format for cross-taxonomy mappings

**Dependency**: `sssom`

**Format**: TSV files with required columns
```
subject_id	predicate_id	object_id	confidence	...
```

**How used**:
```python
from sssom_schema import Mapping

# Mappings stored as TSV
# Loaded into YAML during conversion
```

**Key files**:
- `src/ai_atlas_nexus/data/mappings/*.tsv` (mapping files)
- `src/ai_atlas_nexus/blocks/risk_mapping/risk_mapper.py` (mapping generation)

---

### 4. LLM Provider APIs

#### A. Ollama

**Purpose**: Local LLM inference

**Dependency**: `ollama`

**API**: HTTP REST API (localhost:11434)

```python
from ollama import Client

client = Client(host="localhost:11434")
response = client.generate(
    model="granite3.2:8b",
    prompt="...",
    options={"temperature": 0.1}
)
```

**Key file**: `src/ai_atlas_nexus/blocks/inference/ollama.py`

#### B. IBM Watson Machine Learning

**Purpose**: Enterprise LLM inference

**Dependency**: `ibm-watsonx-ai`

**API**: IBM Cloud API

```python
from ibm_watsonx_ai import APIClient

client = APIClient(credentials={
    "apikey": "...",
    "url": "..."
})
```

**Key file**: `src/ai_atlas_nexus/blocks/inference/wml.py`

#### C. vLLM

**Purpose**: High-performance LLM serving

**Dependency**: `vllm`, `xgrammar`

**API**: OpenAI-compatible HTTP API

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="..."
)
```

**Key file**: `src/ai_atlas_nexus/blocks/inference/vllm.py`

---

### 5. txtai (Embeddings)

**Purpose**: Semantic similarity for risk mapping

**Dependency**: `txtai`

**How used**:
```python
from txtai.embeddings import Embeddings

embeddings = Embeddings()
embeddings.index([(i, text) for i, text in enumerate(texts)])

# Find similar
results = embeddings.search("query text", limit=5)
```

**Key file**: `src/ai_atlas_nexus/blocks/risk_mapping/risk_mapper.py:114`

---

### 6. Jinja2 (Templating)

**Purpose**: Prompt template rendering

**Dependency**: `jinja2`

**How used**:
```python
from jinja2 import Template

template = Template(RISK_IDENTIFICATION_TEMPLATE)
prompt = template.render(
    risks=risk_list,
    usecase=usecase,
    examples=cot_examples
)
```

**Key files**:
- `src/ai_atlas_nexus/blocks/prompt_builder.py`
- `src/ai_atlas_nexus/blocks/prompt_templates.py`

---

### 7. External Data Sources

**Taxonomies integrated**:

| Source | URL | Conversion Script |
|--------|-----|-------------------|
| IBM AI Risk Atlas | https://ibm.com/docs/watsonx/ai-risk-atlas | `riskatlas2linkml.py` |
| NIST AI RMF | https://nist.gov/itl/ai-risk-management-framework | `nistactions2linkml.py` |
| OWASP Top 10 LLM | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Manual |
| MIT AI Risk Repository | https://airisk.mit.edu | `mitriskrepo2linkml.py` |
| AIR 2024 | https://airisk.io | `air_2024_risks2linkml.py` |
| AILuminate | Various | Manual |
| Credo UCF | https://credoai.com | `credo2linkml.py` |
| IBM Granite Guardian | IBM Research | Manual |
| Google ShieldGemma | https://arxiv.org/abs/2407.21772 | Manual |

---

## Configuration and Environment Variables

### Environment Variables

**Ollama**:
```bash
OLLAMA_API_URL=http://localhost:11434
```

**IBM Watson ML**:
```bash
WML_API_KEY=<api_key>
WML_API_URL=<url>
WML_PROJECT_ID=<project_id>  # or WML_SPACE_ID
```

**RITS (IBM Internal)**:
```bash
RITS_API_KEY=<api_key>
RITS_API_URL=<url>
```

### Configuration Files

**Pre-commit** (`.pre-commit-config.yaml`):
- Code formatting (Black, isort)
- Secret scanning (detect-secrets)
- Whitespace fixes

**Project config** (`pyproject.toml`):
- Dependencies
- Build configuration
- Tool settings (isort, pytest)

**MkDocs** (`mkdocs.yml`):
- Documentation structure
- Theme configuration
- Plugins

---

## Project Metrics

**Codebase size** (as of v1.0.4):
- Python files: 48
- Lines of code: ~15,000 (excluding generated datamodel)
- Generated datamodel: 2,107 lines
- YAML data files: 25+
- Knowledge graph entities: 556 risks, 254 actions, 17 controls
- Taxonomies integrated: 11
- Tests: 54 (all passing)
- Test coverage: >80%

**Documentation**:
- Auto-generated schema docs: 200+ pages
- Example notebooks: 9
- Conceptual guides: 5+

---

## Success Metrics

**For Users**:
- Time to identify risks: Hours → Minutes
- Taxonomies consulted: 1 → 11+
- Cross-taxonomy insights: Manual → Automated

**For Community**:
- Contributors: 15+
- Stars: 111+
- Forks: 23+
- Issues resolved: Ongoing

**For AI Governance**:
- Taxonomies unified: 11+
- Risks catalogued: 556
- Actions available: 254
- Cross-taxonomy mappings: 100+

---

## Future Directions

**Planned enhancements** (based on project trajectory):

1. **More taxonomies**: Continuous integration of new frameworks
2. **Better mappings**: Improved cross-taxonomy alignment
3. **Richer evaluations**: More benchmarks and datasets linked
4. **UI improvements**: Enhanced HuggingFace demo
5. **Neo4j integration**: Optional graph database backend
6. **Agent capabilities**: Better modeling of AI system capabilities

**Extension opportunities**:
- Custom taxonomy creation tools
- Automated mapping generation
- Risk prediction models
- Compliance report generation
- Integration with AI development platforms

---

## Quick Start for New Agents

**30-Second Overview**:

AI Atlas Nexus is a Python library that helps teams identify and manage AI risks by:
1. Unifying 11+ risk taxonomies into one knowledge graph
2. Using LLMs to automatically identify risks from use case descriptions
3. Providing cross-taxonomy mappings and governance workflows

**5-Minute Getting Started**:

```python
# 1. Install
pip install "ai-atlas-nexus[ollama]"  # When available on PyPI

# 2. Initialize
from ai_atlas_nexus import AIAtlasNexus
ran = AIAtlasNexus()

# 3. Explore
print(f"Loaded {len(ran.get_all_risks())} risks")

# 4. Identify risks
from ai_atlas_nexus.blocks.inference import OllamaInferenceEngine
engine = OllamaInferenceEngine(...)
results = ran.identify_risks_from_usecases(
    usecases=["Your use case..."],
    inference_engine=engine
)

# 5. Navigate
related = ran.get_related_risks(id="atlas-toxic-output")
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-28
**Codebase Version**: 1.0.4
