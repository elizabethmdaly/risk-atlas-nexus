# AI Atlas Nexus - Agent Onboarding Guide

## Project Overview

**AI Atlas Nexus** is an open-source Python library that provides comprehensive tooling for AI governance and risk management. It serves as a nexus (connection point) that unifies disparate AI risk taxonomies, benchmarks, and governance resources into a cohesive knowledge graph.

### Purpose

The library enables developers, AI practitioners, and governance teams to:
- **Identify AI risks** in their use cases using LLM-powered analysis
- **Navigate relationships** between risks, mitigations, and resources across multiple taxonomies
- **Map risks** between different classification systems (IBM, NIST, OWASP, MIT, etc.)
- **Categorize risk severity** based on frameworks like the EU AI Act
- **Access governance resources** including actions, benchmarks, and best practices

### Key Value Proposition

Instead of manually consulting multiple disconnected AI risk taxonomies and frameworks, AI Atlas Nexus provides:
1. A **unified ontology** combining 11+ major taxonomies (556 risks total)
2. **Automated risk identification** from use case descriptions
3. **Cross-taxonomy mappings** showing relationships between different frameworks
4. **LLM-powered governance assistance** with support for multiple inference engines

---

## Tech Stack

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Primary language | 3.11.x required |
| **LinkML** | Schema definition and validation | 1.9.5+ |
| **Pydantic** | Data validation and serialization | 2.x |
| **YAML** | Data storage format | - |
| **Jinja2** | Prompt templating | 3.1+ |

### Key Dependencies

**Data & Schema**:
- `linkml` & `linkml_runtime` - Schema-driven data modeling
- `sssom` - Standard semantic mapping format
- `pydantic` - Runtime type checking and validation
- `jsonschema` - JSON schema validation

**AI/ML**:
- `txtai` - Vector embeddings for semantic similarity
- `openai>=1.0` - OpenAI-compatible API client
- LLM provider libraries (optional):
  - `ibm-watsonx-ai` - IBM Watson Machine Learning
  - `ollama` - Local Ollama inference
  - `vllm` - vLLM serving

**Utilities**:
- `requests` - HTTP client
- `rich` - Terminal formatting
- `logzero` - Structured logging
- `python-dotenv` - Environment variable management
- `tqdm` - Progress bars

### Documentation

- **MkDocs** with Material theme
- **Jupyter notebooks** for examples
- Auto-generated API docs from docstrings

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─ from ai_atlas_nexus import AIAtlasNexus
                       │
┌──────────────────────┴──────────────────────────────────────┐
│              AIAtlasNexus (library.py)                       │
│  Main API: 50+ methods for risk exploration & analysis      │
└───┬──────────────────────────────────────────────────┬──────┘
    │                                                   │
    ├─ RiskExplorer                        ├─ Inference Engines
    │  (risk-specific queries)              │  (LLM integration)
    │                                       │
    ├─ AtlasExplorer                       ├─ Risk Detector
    │  (generic graph navigation)          │  (use case analysis)
    │                                       │
    ├─ RiskMapper                          └─ Risk Categorizer
    │  (taxonomy mapping)                     (severity assessment)
    │
┌───┴───────────────────────────────────────────────────────────┐
│              Knowledge Graph (YAML Data)                       │
│  • 556 risks across 11 taxonomies                            │
│  • 254 actions, 17 controls, 26 principles                   │
│  • 24 evaluations, datasets, benchmarks                      │
│  • Cross-taxonomy mappings (SSSOM format)                    │
└───────────────────┬───────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │   LinkML Schema     │
         │  (Ontology Def)     │
         └─────────────────────┘
```

### Layered Architecture

1. **Data Layer**
   - LinkML schema defining the ontology (`ai-risk-ontology.yaml`)
   - YAML instance data files (25+ files in `data/knowledge_graph/`)
   - Auto-generated Python datamodel (`ai_risk_ontology.py`)

2. **Logic Layer** ("Blocks")
   - `inference/` - LLM provider integrations (WML, Ollama, vLLM, RITS)
   - `risk_detector/` - Risk identification from use cases
   - `risk_explorer/` - Knowledge graph navigation
   - `risk_mapping/` - Cross-taxonomy mapping
   - `risk_categorization/` - Severity assessment

3. **API Layer**
   - `library.py` - Main `AIAtlasNexus` class
   - High-level methods wrapping logic layer
   - Type-safe interfaces using generated datamodel

### Directory Structure

```
ai-atlas-nexus/
├── src/ai_atlas_nexus/
│   ├── library.py                    # Main API class
│   ├── ai_risk_ontology/
│   │   ├── schema/                   # LinkML schema (YAML)
│   │   │   ├── ai-risk-ontology.yaml # Main schema file
│   │   │   ├── ai_risk.yaml          # Risk definitions
│   │   │   ├── ai_system.yaml        # AI system modeling
│   │   │   └── ... (8 more schema files)
│   │   ├── datamodel/                # Generated Python classes
│   │   │   └── ai_risk_ontology.py   # Auto-generated (2107 lines)
│   │   └── util/                     # Schema utilities
│   │       ├── riskatlas2linkml.py   # IBM converter
│   │       ├── nist*2linkml.py       # NIST converters
│   │       └── ... (taxonomy converters)
│   ├── blocks/                       # Functional modules
│   │   ├── inference/                # LLM engines
│   │   │   ├── base.py              # Abstract interface
│   │   │   ├── ollama.py            # Ollama integration
│   │   │   ├── wml.py               # IBM Watson ML
│   │   │   ├── vllm.py              # vLLM integration
│   │   │   └── rits.py              # IBM RITS (internal)
│   │   ├── risk_detector/
│   │   │   ├── base.py              # Abstract detector
│   │   │   └── generic.py           # LLM-based detector
│   │   ├── risk_explorer/
│   │   │   └── explorer.py          # Knowledge graph queries
│   │   ├── risk_mapping/
│   │   │   ├── base.py              # Abstract mapper
│   │   │   └── risk_mapper.py       # Semantic/LLM mapping
│   │   └── risk_categorization/
│   │       └── severity.py          # EU AI Act classification
│   ├── data/
│   │   ├── knowledge_graph/         # Instance data (25+ YAML files)
│   │   │   ├── risk_atlas_data.yaml # IBM risks
│   │   │   ├── nist_ai_rmf_data.yaml
│   │   │   ├── shieldgemma_*.yaml   # Google ShieldGemma
│   │   │   └── ... (20+ more files)
│   │   ├── mappings/                # Cross-taxonomy mappings
│   │   │   ├── ibm2nistgenai.tsv   # SSSOM format
│   │   │   └── ... (6 mapping files)
│   │   └── templates/               # Prompt templates (JSON)
│   └── toolkit/                     # Utility modules
│       ├── data_utils.py            # YAML loading
│       ├── logging.py               # Structured logging
│       └── error_utils.py           # Error handling
├── docs/                            # MkDocs documentation
│   ├── examples/notebooks/          # Jupyter examples
│   ├── ontology/                    # Auto-generated schema docs
│   └── concepts/                    # Conceptual guides
├── tests/                           # Test suite
│   ├── ai_atlas_nexus/
│   │   ├── test_library.py          # 40 library tests
│   │   ├── test_shieldgemma.py      # 12 integration tests
│   │   └── toolkit/                 # Utility tests
│   └── fixtures/                    # Test data
├── graph_export/                    # Exported graph formats
│   ├── yaml/                        # Full graph YAML
│   ├── cypher/                      # Neo4j Cypher
│   └── owl/                         # OWL ontology
├── pyproject.toml                   # Project config & dependencies
├── Makefile                         # Build automation
└── .pre-commit-config.yaml         # Code quality hooks
```

---

## Setup Instructions

### Prerequisites

- **Python 3.11.x** (required - will NOT work with 3.10 or 3.12+)
- **pip** package manager
- **git** for version control
- (Optional) **Ollama** for local LLM inference

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/IBM/ai-atlas-nexus.git
cd ai-atlas-nexus
```

#### 2. Create Virtual Environment

```bash
# Using Python 3.11 specifically
python3.11 -m venv venv-ai-atlas-nexus

# Activate (macOS/Linux)
source venv-ai-atlas-nexus/bin/activate

# Activate (Windows)
venv-ai-atlas-nexus\Scripts\activate
```

#### 3. Install Dependencies

Choose your LLM inference backend:

**For Ollama (local, no API keys needed)**:
```bash
pip install -e ".[ollama]"
```

**For IBM Watson Machine Learning**:
```bash
pip install -e ".[wml]"
```

**For vLLM**:
```bash
pip install -e ".[vllm]"
```

**For development (all optional dependencies)**:
```bash
pip install -e ".[ollama,wml,vllm,docs]"
```

#### 4. Install Pre-commit Hooks (for contributors)

```bash
pre-commit install
```

#### 5. Verify Installation

```bash
python -c "from ai_atlas_nexus import AIAtlasNexus; ran = AIAtlasNexus(); print(f'✓ Loaded {len(ran.get_all_risks())} risks')"
```

Expected output: `✓ Loaded 556 risks`

### Environment Configuration

#### For Ollama

```bash
# Optional - Ollama uses localhost:11434 by default
export OLLAMA_API_URL="http://localhost:11434"
```

#### For IBM Watson ML

Create a `.env` file in the project root:

```bash
WML_API_KEY=<your_wml_api_key>
WML_API_URL=<your_wml_url>
WML_PROJECT_ID=<your_project_id>  # Or WML_SPACE_ID
```

See [IBM Watson ML docs](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-credentials.html) for obtaining credentials.

---

## How to Run/Build/Test

### Running Examples

#### Quick Start in Python

```python
from ai_atlas_nexus import AIAtlasNexus

# Initialize library
ran = AIAtlasNexus()

# Get all risks
risks = ran.get_all_risks()
print(f"Total risks: {len(risks)}")

# Get a specific risk
risk = ran.get_risk(id="atlas-toxic-output")
print(f"Risk: {risk.name}")
print(f"Description: {risk.description}")

# Find related risks
related = ran.get_related_risks(id="atlas-toxic-output")
print(f"Related risks: {len(related)}")
```

#### Risk Identification with LLM

```python
from ai_atlas_nexus import AIAtlasNexus
from ai_atlas_nexus.blocks.inference import OllamaInferenceEngine

ran = AIAtlasNexus()

# Set up Ollama inference
credentials = {"api_url": "localhost:11434"}
parameters = {"temperature": 0.1, "num_predict": 300}

engine = OllamaInferenceEngine(
    model_name_or_path="granite3.2:8b",
    credentials=credentials,
    parameters=parameters
)

# Identify risks from use case
use_case = "We are building a chatbot that interacts with customers."

results = ran.identify_risks_from_usecases(
    usecases=[use_case],
    inference_engine=engine,
    taxonomy="ibm-risk-atlas",
    zero_shot_only=True,
    max_risk=5
)

for risk in results[0]:
    print(f"- {risk.name} ({risk.id})")
```

### Running Jupyter Notebooks

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook docs/examples/notebooks/

# Open AI_Atlas_Nexus_Quickstart.ipynb
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/ai_atlas_nexus/test_library.py

# Run tests with coverage
pytest --cov=ai_atlas_nexus --cov-report=html
```

Expected results: **54 tests, all passing**

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build docs
JUPYTER_PLATFORM_DIRS=1 mkdocs build

# Serve docs locally
JUPYTER_PLATFORM_DIRS=1 mkdocs serve
# Visit http://localhost:8000
```

### Using the Makefile

The repository includes a Makefile for common tasks:

```bash
# Run tests
make test

# Regenerate Python datamodel from schema
make compile_pydantic_model

# Regenerate documentation
make regenerate_documentation

# Export knowledge graph
make regenerate_graph_output

# Export to Cypher (Neo4j)
make regenerate_cypher_code

# Lint schema
make lint_schema

# Show all commands
make help
```

---

## Common Development Tasks

### 1. Adding a New Taxonomy

**Step 1**: Create a conversion script

```python
# src/ai_atlas_nexus/ai_risk_ontology/util/newtaxonomy2linkml.py

from ai_atlas_nexus.ai_risk_ontology.datamodel.ai_risk_ontology import (
    Risk, RiskTaxonomy, Container
)

def convert_new_taxonomy():
    """Convert NewTaxonomy data to LinkML format"""

    taxonomy = RiskTaxonomy(
        id="new-taxonomy",
        name="New Taxonomy Name",
        description="Description of the taxonomy",
        url="https://example.com/taxonomy"
    )

    risks = [
        Risk(
            id="new-taxonomy-risk-1",
            name="Risk Name",
            description="Risk description",
            isDefinedByTaxonomy="new-taxonomy",
            tag="risk-tag"
        ),
        # ... more risks
    ]

    return Container(
        risks=risks,
        taxonomies=[taxonomy]
    )
```

**Step 2**: Generate YAML data file

```python
from linkml_runtime.dumpers import YAMLDumper

container = convert_new_taxonomy()
YAMLDumper().dump(
    container,
    "src/ai_atlas_nexus/data/knowledge_graph/new_taxonomy_data.yaml"
)
```

**Step 3**: (Optional) Add mappings

Create `src/ai_atlas_nexus/data/mappings/new_taxonomy_mappings.tsv` using SSSOM format.

**Step 4**: Verify loading

```python
from ai_atlas_nexus import AIAtlasNexus
ran = AIAtlasNexus()
new_risks = [r for r in ran.get_all_risks() if 'new-taxonomy' in r.id]
print(f"Loaded {len(new_risks)} risks from new taxonomy")
```

### 2. Modifying the Schema

**Step 1**: Edit schema file

```bash
# Edit the appropriate schema file
vim src/ai_atlas_nexus/ai_risk_ontology/schema/ai_risk.yaml
```

**Step 2**: Regenerate Python datamodel

```bash
make compile_pydantic_model
```

**Step 3**: Update data files if needed

Ensure all YAML instance files conform to the updated schema.

**Step 4**: Run tests

```bash
pytest tests/
```

### 3. Adding a New LLM Provider

**Step 1**: Create provider module

```python
# src/ai_atlas_nexus/blocks/inference/newprovider.py

from ai_atlas_nexus.blocks.inference.base import InferenceEngine
from ai_atlas_nexus.blocks.inference.params import (
    InferenceEngineCredentials,
    TextGenerationInferenceOutput
)

class NewProviderInferenceEngine(InferenceEngine):

    _inference_engine_type = "NEWPROVIDER"
    _inference_engine_parameter_class = NewProviderParams  # Define in params.py

    def prepare_credentials(self, credentials):
        # Extract and validate credentials
        api_key = credentials.get("api_key")
        return InferenceEngineCredentials(api_key=api_key, ...)

    def create_client(self, credentials):
        # Initialize provider client
        from newprovider import Client
        return Client(api_key=credentials["api_key"])

    def ping(self):
        # Health check
        self.client.status()

    def generate(self, prompts, **kwargs):
        # Generate responses
        responses = []
        for prompt in prompts:
            response = self.client.generate(prompt, **self.parameters)
            responses.append(
                TextGenerationInferenceOutput(
                    generated_text=response.text,
                    ...
                )
            )
        return responses

    def chat(self, messages, **kwargs):
        # Chat completion
        response = self.client.chat(messages, **self.parameters)
        return TextGenerationInferenceOutput(...)
```

**Step 2**: Add to exports

```python
# src/ai_atlas_nexus/blocks/inference/__init__.py

from .newprovider import NewProviderInferenceEngine

__all__ = [
    "InferenceEngine",
    "OllamaInferenceEngine",
    "WMLInferenceEngine",
    "VLLMInferenceEngine",
    "RITSInferenceEngine",
    "NewProviderInferenceEngine",  # Add here
]
```

**Step 3**: Add optional dependency

```toml
# pyproject.toml

[project.optional-dependencies]
newprovider = ["newprovider-sdk"]
```

**Step 4**: Test

```python
from ai_atlas_nexus.blocks.inference import NewProviderInferenceEngine

engine = NewProviderInferenceEngine(
    model_name_or_path="model-name",
    credentials={"api_key": "..."},
    parameters={"temperature": 0.1}
)

result = engine.generate(["Test prompt"])
print(result[0].generated_text)
```

### 4. Running Experiments

**Create experiment script**:

```python
# experiments/my_experiment.py

from ai_atlas_nexus import AIAtlasNexus
from ai_atlas_nexus.blocks.inference import OllamaInferenceEngine

ran = AIAtlasNexus()

# Your experiment code here
use_cases = [
    "Use case 1...",
    "Use case 2...",
]

engine = OllamaInferenceEngine(...)

for use_case in use_cases:
    results = ran.identify_risks_from_usecases(
        usecases=[use_case],
        inference_engine=engine,
        taxonomy="ibm-risk-atlas"
    )

    # Log results
    print(f"Use case: {use_case}")
    print(f"Identified {len(results[0])} risks")
```

### 5. Debugging Common Issues

**Issue**: `ModuleNotFoundError: No module named 'ai_atlas_nexus'`

**Solution**: Install in editable mode: `pip install -e .`

---

**Issue**: `TypeError: InferenceEngine.__init__() got an unexpected keyword argument 'model_id'`

**Solution**: Use `model_name_or_path` instead of `model_id`

---

**Issue**: `Invalid parameters found: ['max_new_tokens']`

**Solution**: Ollama uses `num_predict` instead of `max_new_tokens`. Check the provider's parameter class.

---

**Issue**: Python version mismatch

**Solution**: Ensure you're using Python 3.11.x:
```bash
python --version  # Should show 3.11.x
```

---

## Key Concepts

### 1. The Knowledge Graph

The knowledge graph is stored as YAML instance data that conforms to the LinkML schema. It contains:

- **556 risks** across 11 taxonomies
- **254 actions** for risk mitigation
- **17 risk controls** (detectors/guardrails)
- **26 AI principles** from various organizations
- **24 evaluations** and benchmarks
- **Cross-taxonomy mappings** linking related concepts

### 2. LinkML Schema System

LinkML (Linked data Modeling Language) is used to define the ontology:

- **Schema Definition**: YAML files in `ai_risk_ontology/schema/`
- **Code Generation**: Produces Python classes (`datamodel/ai_risk_ontology.py`)
- **Validation**: Ensures instance data conforms to schema
- **Extensibility**: New types can be added via schema imports

### 3. Inference Engines

Pluggable LLM providers following a common interface:

- **Strategy Pattern**: Swap providers without changing application code
- **Credentials**: Each provider handles auth differently (API keys, URLs)
- **Parameters**: Provider-specific parameters (temperature, max_tokens, etc.)
- **Concurrency**: Built-in support for parallel requests

### 4. Prompt Engineering

The library uses template-based prompting:

- **Zero-shot**: Direct prompts without examples
- **Few-shot (CoT)**: Chain-of-Thought examples improve accuracy
- **JSON Schema**: Structured responses validated against schema
- **Jinja2 Templates**: Flexible prompt construction

---

## Project Resources

- **Homepage**: https://github.com/IBM/ai-atlas-nexus
- **Documentation**: https://ibm.github.io/ai-atlas-nexus/
- **Issues**: https://github.com/IBM/ai-atlas-nexus/issues
- **Changelog**: https://github.com/IBM/ai-atlas-nexus/blob/main/CHANGELOG.md
- **HuggingFace Demo**: https://huggingface.co/spaces/ibm/risk-atlas-nexus
- **Demo Projects**: https://github.com/IBM/ai-atlas-nexus-demos

### Research Papers

- [AI Risk Atlas: Taxonomy and Tooling for Navigating AI Risks and Resources](https://arxiv.org/abs/2503.05780)
- [Usage Governance Advisor: From Intent to AI Governance](https://arxiv.org/abs/2412.01957)

---

## Quick Reference

### Import Shortcuts

```python
# Main library
from ai_atlas_nexus import AIAtlasNexus

# Inference engines
from ai_atlas_nexus.blocks.inference import (
    OllamaInferenceEngine,
    WMLInferenceEngine,
    VLLMInferenceEngine
)

# Datamodel classes
from ai_atlas_nexus.ai_risk_ontology.datamodel.ai_risk_ontology import (
    Risk,
    Action,
    RiskControl,
    RiskTaxonomy,
    Container
)
```

### Common Method Patterns

```python
ran = AIAtlasNexus()

# Get entities
risk = ran.get_risk(id="risk-id")
risks = ran.get_all_risks()
taxonomy = ran.get_taxonomy_by_id("taxonomy-id")

# Relationships
related_risks = ran.get_related_risks(id="risk-id")
actions = ran.get_related_actions(id="risk-id")
controls = ran.get_related_risk_controls(id="risk-id")

# LLM-powered analysis
risks = ran.identify_risks_from_usecases(usecases=[...], inference_engine=...)
tasks = ran.identify_ai_tasks_from_usecases(usecases=[...], inference_engine=...)
domain = ran.identify_domain_from_usecases(usecases=[...], inference_engine=...)

# Severity assessment
result = ran.categorize_risk_severity(usecase=..., inference_engine=...)
```

---

## Support

For questions, issues, or contributions:

1. Check the [documentation](https://ibm.github.io/ai-atlas-nexus/)
2. Search [existing issues](https://github.com/IBM/ai-atlas-nexus/issues)
3. Create a new issue with detailed context
4. Join discussions on GitHub

---

**Version**: 1.0.4
**Last Updated**: 2025-11-28
**License**: Apache 2.0
