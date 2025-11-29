# AI Atlas Nexus - Development Guidelines

## Code Style and Conventions

### Python Style

This project follows **PEP 8** with enforcement via **Black** and **isort**.

#### Black Configuration

```python
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 88
```

- **Line length**: 88 characters (Black default)
- **String quotes**: Double quotes preferred
- **Indentation**: 4 spaces (no tabs)

#### Import Organization (isort)

```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
from linkml_runtime import SchemaView
from pydantic import BaseModel
import yaml

# Internal imports
from ai_atlas_nexus.ai_risk_ontology.datamodel.ai_risk_ontology import Risk
from ai_atlas_nexus.blocks.inference.base import InferenceEngine
from ai_atlas_nexus.toolkit.logging import configure_logger
```

**isort settings**:
- `profile = "black"` - Compatible with Black
- `group_by_package = true` - Group imports by package
- `combine_star = true` - Combine `from x import *` statements
- `lines_after_imports = 2` - Two blank lines after imports

#### Pre-commit Hooks

The project uses pre-commit hooks to enforce style:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Hooks configured**:
1. **isort** - Import sorting
2. **Black** - Code formatting
3. **detect-secrets** - Secret scanning
4. **trailing-whitespace** - Remove trailing whitespace
5. **end-of-file-fixer** - Ensure files end with newline

### Type Hints

Use type hints extensively for better IDE support and documentation:

```python
from typing import Dict, List, Optional, Union

def get_risk(
    cls,
    tag: Optional[str] = None,
    id: Optional[str] = None,
    name: Optional[str] = None,
    taxonomy: Optional[str] = None,
) -> Optional[Risk]:
    """Get risk definition from the knowledge graph.

    Args:
        id: The string ID identifying the risk
        tag: The string tag identifying the risk
        name: The string name identifying the risk
        taxonomy: The string label for a taxonomy

    Returns:
        Risk object or None if not found
    """
    # Implementation
```

**Key conventions**:
- Always use `Optional[T]` for nullable parameters
- Use `Union[A, B]` for multiple accepted types
- Use `List[T]`, `Dict[K, V]` for collections
- Return types should be explicit

### Docstrings

Use **Google-style docstrings**:

```python
def identify_risks_from_usecases(
    cls,
    usecases: List[str],
    inference_engine: InferenceEngine,
    taxonomy: Optional[str] = None,
    cot_examples: Optional[Dict[str, List]] = None,
    max_risk: Optional[int] = None,
    zero_shot_only: bool = False,
) -> List[List[Risk]]:
    """Identify potential risks from a usecase description.

    Args:
        usecases: A list of strings describing AI usecases
        inference_engine: An LLM inference engine to infer risks
        taxonomy: The string label for a taxonomy. Defaults to "ibm-risk-atlas"
        cot_examples: Optional few-shot examples for Chain-of-Thought prompting
        max_risk: Maximum number of risks to return per usecase
        zero_shot_only: If True, use zero-shot method ignoring cot_examples

    Returns:
        List of lists of Risk objects, one list per usecase

    Raises:
        TypeError: If usecases is not a list of strings
        ValueError: If taxonomy is not found

    Example:
        ```python
        from ai_atlas_nexus import AIAtlasNexus
        from ai_atlas_nexus.blocks.inference import OllamaInferenceEngine

        ran = AIAtlasNexus()
        engine = OllamaInferenceEngine(...)

        results = ran.identify_risks_from_usecases(
            usecases=["Building a chatbot..."],
            inference_engine=engine,
            taxonomy="ibm-risk-atlas"
        )
        ```
    """
    # Implementation
```

---

## File Organization Patterns

### Module Structure

Each major component follows a consistent pattern:

```
blocks/<component>/
├── __init__.py          # Public exports
├── base.py              # Abstract base class
├── <implementation>.py  # Concrete implementations
└── types.py             # Type definitions (if needed)
```

**Example** (`blocks/inference/`):

```
blocks/inference/
├── __init__.py          # Exports all engines
├── base.py              # InferenceEngine (abstract)
├── ollama.py            # OllamaInferenceEngine
├── wml.py               # WMLInferenceEngine
├── vllm.py              # VLLMInferenceEngine
├── rits.py              # RITSInferenceEngine
├── params.py            # Parameter & credential classes
└── postprocessing.py    # Response processing utilities
```

### `__init__.py` Pattern

Always export public interfaces in `__init__.py`:

```python
# blocks/inference/__init__.py

from .base import InferenceEngine
from .ollama import OllamaInferenceEngine
from .params import TextGenerationInferenceOutput
from .rits import RITSInferenceEngine
from .vllm import VLLMInferenceEngine
from .wml import WMLInferenceEngine

__all__ = [
    "InferenceEngine",
    "OllamaInferenceEngine",
    "WMLInferenceEngine",
    "VLLMInferenceEngine",
    "RITSInferenceEngine",
    "TextGenerationInferenceOutput",
]
```

### Data Files Organization

```
data/
├── knowledge_graph/              # Instance data (YAML)
│   ├── <taxonomy>_data.yaml      # Risks, actions, etc.
│   └── mappings/                 # Cross-taxonomy mappings
│       └── <from>_<to>.tsv       # SSSOM format
├── templates/                    # Prompt templates (JSON)
│   ├── risk_generation_cot.json
│   └── questionnaire_*.json
└── __init__.py                   # Resource loading utilities
```

**Naming conventions**:
- Data files: `<taxonomy_name>_data.yaml`
- Mapping files: `<source_taxonomy>_<target_taxonomy>.tsv`
- Template files: `<purpose>_<method>.json`

---

## Naming Conventions

### Variables and Functions

```python
# snake_case for variables and functions
risk_id = "atlas-toxic-output"
def get_related_risks(id: str) -> List[Risk]:
    pass

# Private functions/methods: prefix with underscore
def _validate_taxonomy(taxonomy: str) -> bool:
    pass

# Constants: UPPER_SNAKE_CASE
RISK_IDENTIFICATION_COT = load_resource("risk_generation_cot.json")
MAX_CONCURRENT_REQUESTS = 10
```

### Classes

```python
# PascalCase for classes
class InferenceEngine:
    pass

class OllamaInferenceEngine(InferenceEngine):
    pass

class RiskDetector:
    pass
```

### Files and Directories

```python
# snake_case for Python files
risk_detector.py
inference_engine.py
data_utils.py

# Directories: snake_case
ai_risk_ontology/
risk_detector/
knowledge_graph/
```

### Entity IDs

IDs in the knowledge graph follow a specific format:

```yaml
# Pattern: <taxonomy>-<entity>-<name>
id: atlas-toxic-output
id: nist-ai-rmf-govern-1-1
id: shieldgemma-hate-speech

# For taxonomies
id: ibm-risk-atlas
id: nist-ai-rmf
id: shieldgemma-taxonomy
```

**Rules**:
- Use lowercase kebab-case
- Prefix with taxonomy identifier
- Be descriptive but concise
- Avoid special characters except hyphens

### Tags

Tags for filtering and search:

```yaml
# Pattern: kebab-case, short keywords
tag: toxic-output
tag: hate-speech
tag: prompt-injection
tag: model-poisoning
```

---

## Testing Approach and Requirements

### Test Organization

```
tests/
├── __init__.py
├── base.py                      # TestCaseBase class
├── ai_atlas_nexus/
│   ├── test_library.py          # Library API tests (40 tests)
│   ├── test_shieldgemma.py      # Integration tests (12 tests)
│   └── toolkit/
│       └── test_error_utils.py  # Utility tests (2 tests)
├── fixtures/                    # Test data
└── common/                      # Shared test utilities
```

### Test Structure

Use `unittest.TestCase` framework with class-based organization:

```python
# tests/ai_atlas_nexus/test_library.py

from tests.base import TestCaseBase
from ai_atlas_nexus import AIAtlasNexus

class TestLibrary(TestCaseBase):
    """Tests for Library"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests"""
        cls.ran_lib = AIAtlasNexus()

    def test_get_all_risks_type(self):
        """Test that get_all_risks returns a list"""
        risks = self.ran_lib.get_all_risks()
        assert isinstance(risks, list)

    def test_get_risk_by_id(self):
        """Test retrieval of specific risk by ID"""
        risk = self.ran_lib.get_risk(id="atlas-toxic-output")
        assert risk is not None
        assert risk.id == "atlas-toxic-output"
        assert hasattr(risk, 'name')
        assert hasattr(risk, 'description')
```

### Test Naming

```python
# Pattern: test_<method>_<scenario>
def test_get_risk_valid_id(self):
    """Test get_risk with valid ID"""

def test_get_risk_invalid_id(self):
    """Test get_risk with non-existent ID"""

def test_identify_risks_zero_shot(self):
    """Test risk identification with zero-shot prompting"""

def test_identify_risks_few_shot(self):
    """Test risk identification with few-shot examples"""
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbosity
pytest -v

# Run specific test file
pytest tests/ai_atlas_nexus/test_library.py

# Run specific test
pytest tests/ai_atlas_nexus/test_library.py::TestLibrary::test_get_all_risks_type

# With coverage
pytest --cov=ai_atlas_nexus --cov-report=html
```

### Test Coverage Requirements

- **Unit tests**: Cover all public API methods
- **Integration tests**: Test end-to-end workflows (risk identification, mapping, etc.)
- **Edge cases**: Test with empty inputs, invalid IDs, missing data
- **Target coverage**: Maintain >80% code coverage

### Mocking LLM Calls

For tests involving LLM inference, use mock responses:

```python
from unittest.mock import Mock, patch

def test_risk_identification_with_mock_llm(self):
    """Test risk identification with mocked LLM"""

    # Create mock engine
    mock_engine = Mock(spec=InferenceEngine)
    mock_engine.generate.return_value = [
        TextGenerationInferenceOutput(
            generated_text='{"risks": ["toxic-output", "output-bias"]}'
        )
    ]

    # Test with mock
    results = self.ran_lib.identify_risks_from_usecases(
        usecases=["Test use case"],
        inference_engine=mock_engine,
        zero_shot_only=True
    )

    # Verify
    assert len(results) == 1
    assert len(results[0]) > 0
    mock_engine.generate.assert_called_once()
```

---

## Key Architectural Decisions and Patterns

### 1. LinkML for Schema Definition

**Decision**: Use LinkML instead of JSON Schema or Python classes directly

**Rationale**:
- Machine-readable schema enables validation
- Auto-generates Python, JSON-Schema, OWL, etc.
- Community standard for biomedical and scientific domains
- Extensible via imports and mixins

**Impact**:
- Schema changes require regeneration: `make compile_pydantic_model`
- Instance data must be valid YAML conforming to schema
- Type safety at runtime via generated Pydantic models

### 2. YAML for Data Storage

**Decision**: Store knowledge graph as YAML files, not database

**Rationale**:
- Human-readable and editable
- Git-friendly (version control, diffs, merges)
- No external dependencies (database server)
- Fast enough for typical graph sizes (<10K entities)

**Trade-offs**:
- Limited to in-memory operations
- No complex queries (but graph navigation handles most needs)
- May need database for very large graphs (future consideration)

### 3. Abstract Base Classes for Extensibility

**Pattern**: Strategy pattern with abstract base classes

```python
# Abstract interface
class InferenceEngine(ABC):
    @abstractmethod
    def generate(self, prompts): pass

    @abstractmethod
    def create_client(self, credentials): pass

# Concrete implementations
class OllamaInferenceEngine(InferenceEngine):
    def generate(self, prompts):
        # Ollama-specific implementation
        pass
```

**Benefits**:
- Easy to add new providers (LLMs, mappers, detectors)
- Enforces consistent interfaces
- Enables dependency injection and testing

### 4. Separation of RiskExplorer and AtlasExplorer

**Decision**: Maintain two separate navigation systems

**RiskExplorer**: Risk-specific, optimized queries
**AtlasExplorer**: Generic graph navigation

**Rationale**:
- **Backward compatibility**: Existing code uses RiskExplorer
- **Domain optimization**: Risk queries are very common, should be fast
- **Flexibility**: AtlasExplorer handles new entity types (capabilities, tasks)

**When to use each**:
- Use **RiskExplorer** for: risks, actions, controls, taxonomies
- Use **AtlasExplorer** for: capabilities, tasks, intrinsics, generic traversals

### 5. Chain-of-Thought (CoT) Prompting

**Decision**: Support both zero-shot and few-shot (CoT) prompting

**Zero-shot**:
```python
results = ran.identify_risks_from_usecases(
    usecases=[...],
    inference_engine=engine,
    zero_shot_only=True  # Fast, but less accurate
)
```

**Few-shot (CoT)**:
```python
cot_examples = {
    "ibm-risk-atlas": [
        {
            "usecase": "Example use case...",
            "thinking": "Chain of thought reasoning...",
            "risks": ["risk-1", "risk-2"]
        }
    ]
}

results = ran.identify_risks_from_usecases(
    usecases=[...],
    inference_engine=engine,
    cot_examples=cot_examples  # More accurate
)
```

**Benefits**:
- Improved accuracy with examples
- Explainability via reasoning steps
- Customizable per taxonomy

**Trade-offs**:
- Few-shot requires more tokens (slower, costlier)
- Need to maintain example templates

### 6. JSON Schema Validation for LLM Responses

**Decision**: Use JSON schema to constrain LLM outputs

```python
# Define expected response schema
schema = {
    "type": "object",
    "properties": {
        "risks": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["risks"]
}

# LLM generates JSON conforming to schema
response = engine.generate(prompt, json_schema=schema)
```

**Benefits**:
- Reliable structured outputs
- Reduces parsing errors
- Self-documenting response format

---

## Common Gotchas and Things to Be Aware Of

### 1. Python Version Constraint

**Issue**: Project requires Python 3.11.x specifically

```toml
requires-python = ">=3.11, <3.12.5"
```

**Why**: Dependencies (particularly LinkML and Pydantic) have version constraints

**Solution**: Always use Python 3.11.x:
```bash
python3.11 -m venv venv
source venv/bin/activate
python --version  # Should be 3.11.x
```

### 2. InferenceEngine Parameter Names

**Issue**: Different providers use different parameter names

```python
# Ollama uses:
parameters = {"num_predict": 300}  # NOT max_new_tokens

# WML uses:
parameters = {"max_new_tokens": 300}

# vLLM uses:
parameters = {"max_tokens": 300}
```

**Solution**: Check `_inference_engine_parameter_class` for each provider in `params.py`

### 3. Method Signatures Use Keyword Arguments

**Issue**: Many methods require keyword arguments

```python
# WRONG - positional argument
risk = ran.get_risk("atlas-toxic-output")  # Returns None!

# CORRECT - keyword argument
risk = ran.get_risk(id="atlas-toxic-output")
```

**Why**: Methods accept multiple optional filters (id, tag, name, taxonomy)

**Solution**: Always use keyword arguments for clarity

### 4. Risk ID Merging in load_yamls_to_container

**Behavior**: Risks with the same ID are merged across files

```python
# File 1: risk_atlas_data.yaml
risks:
  - id: atlas-toxic-output
    name: "Toxic output"
    description: "..."

# File 2: mappings/ibm2nist.yaml
risks:
  - id: atlas-toxic-output
    relatedMatch:
      - nist-ai-rmf-govern-1-1

# Result: Merged into single Risk object with both fields
```

**Rationale**: Allows mapping files to augment base risk definitions

**Impact**: Be careful not to accidentally duplicate or conflict with existing IDs

### 5. LinkML Schema Changes Require Regeneration

**Issue**: Editing schema files doesn't automatically update Python datamodel

**Workflow**:
```bash
# 1. Edit schema
vim src/ai_atlas_nexus/ai_risk_ontology/schema/ai_risk.yaml

# 2. Regenerate datamodel
make compile_pydantic_model

# 3. Verify changes
git diff src/ai_atlas_nexus/ai_risk_ontology/datamodel/ai_risk_ontology.py

# 4. Update instance data if needed
# Edit YAML files to conform to new schema

# 5. Test
pytest tests/
```

### 6. Credentials via Environment Variables

**Issue**: Some engines default to environment variables if credentials not provided

```python
# If credentials={}, will check env vars
engine = OllamaInferenceEngine(
    model_name_or_path="model",
    credentials={}  # Will use OLLAMA_API_URL from env
)
```

**Solution**: Use `.env` file or explicit credentials:
```python
credentials = {"api_url": "localhost:11434"}
```

### 7. Graph Navigation Depth Limits

**Issue**: Deep graph traversals can be slow or hit recursion limits

```python
# May take a long time
result = ran.navigate_graph(
    start_id="some-id",
    start_type=GraphEntityType.RISK,
    max_depth=10  # Very deep
)
```

**Solution**: Start with smaller depths (1-3) and increase as needed

### 8. Taxonomy Names Must Match Exactly

**Issue**: Taxonomy filtering is case-sensitive and exact match

```python
# WRONG
risks = ran.get_all_risks(taxonomy="IBM Risk Atlas")  # Returns []

# CORRECT
risks = ran.get_all_risks(taxonomy="ibm-risk-atlas")
```

**Solution**: Check `ran.get_all_taxonomies()` for exact taxonomy IDs

### 9. SSSOM Mapping File Format

**Issue**: SSSOM TSV files have strict format requirements

**Required columns**:
- `subject_id`
- `subject_label`
- `predicate_id`
- `object_id`
- `object_label`
- `mapping_justification`
- `confidence`
- `author_id`
- `mapping_date`

**Example**:
```tsv
subject_id	subject_label	predicate_id	object_id	object_label
atlas-toxic-output	Toxic output	skos:relatedMatch	nist-ai-rmf-govern-1-1	GOVERN 1.1
```

**Solution**: Use existing mapping files as templates

### 10. Pre-commit Hooks Can Block Commits

**Issue**: Hooks may fail and prevent commits

```bash
git commit -m "My changes"
# isort.....Failed
# black.....Failed
```

**Solutions**:

**Option 1**: Fix issues automatically
```bash
pre-commit run --all-files  # Auto-fixes many issues
git add -u
git commit -m "My changes"
```

**Option 2**: Skip hooks (not recommended)
```bash
git commit -m "My changes" --no-verify
```

**Option 3**: Install hooks locally
```bash
pip install pre-commit
pre-commit run --all-files  # Run before committing
```

---

## Development Workflow Best Practices

### 1. Creating a New Feature

```bash
# 1. Create branch
git checkout -b feature/my-new-feature

# 2. Make changes
# ... edit code ...

# 3. Run pre-commit hooks
pre-commit run --all-files

# 4. Run tests
pytest

# 5. Commit with sign-off
git add .
git commit -m "feat: add new feature

Signed-off-by: Your Name <your.email@example.com>"

# 6. Push and create PR
git push origin feature/my-new-feature
```

### 2. Testing Changes Locally

```bash
# Install in editable mode
pip install -e ".[ollama]"

# Test in Python REPL
python3
>>> from ai_atlas_nexus import AIAtlasNexus
>>> ran = AIAtlasNexus()
>>> # Test your changes
```

### 3. Updating Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve docs locally
JUPYTER_PLATFORM_DIRS=1 mkdocs serve

# Visit http://localhost:8000

# Build final docs
JUPYTER_PLATFORM_DIRS=1 mkdocs build
```

### 4. Secret Scanning

**Never commit**:
- API keys
- Passwords
- Tokens
- Credentials

**Use**:
- `.env` files (gitignored)
- Environment variables
- Secret managers

**Verify**:
```bash
# Scan for secrets
detect-secrets scan --update .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline
```

---

## Code Review Checklist

When reviewing PRs or submitting code:

- [ ] **Tests pass**: `pytest` runs successfully
- [ ] **Coverage maintained**: New code has tests
- [ ] **Type hints added**: Functions have proper type annotations
- [ ] **Docstrings updated**: Google-style docstrings for public APIs
- [ ] **Pre-commit passes**: `pre-commit run --all-files` succeeds
- [ ] **No secrets committed**: `detect-secrets audit` clean
- [ ] **Schema updated**: If modifying schema, datamodel regenerated
- [ ] **Documentation updated**: README, docs, or examples if needed
- [ ] **Backwards compatible**: Existing APIs unchanged (or deprecated gracefully)
- [ ] **Signed commit**: Commit includes `Signed-off-by` line

---

## Resources for Contributors

### Internal Documentation

- `docs/ontology/` - Auto-generated schema documentation
- `docs/concepts/` - Conceptual guides
- `docs/examples/notebooks/` - Jupyter notebook examples

### External Resources

- **LinkML**: https://linkml.io/linkml/
- **SSSOM**: https://mapping-commons.github.io/sssom/
- **Pydantic**: https://docs.pydantic.dev/
- **MkDocs**: https://www.mkdocs.org/

### Getting Help

1. Check existing documentation
2. Search GitHub issues
3. Ask in PR comments
4. Contact maintainers

---

## Summary

**Key Principles**:

1. **Type safety**: Use type hints and Pydantic models
2. **Testability**: Write tests for new code, maintain coverage
3. **Extensibility**: Follow abstract base class patterns
4. **Documentation**: Keep docs up-to-date with code
5. **Consistency**: Use pre-commit hooks and follow conventions
6. **Schema-first**: Let LinkML schema drive data structure

**When in doubt**:
- Look at existing code for patterns
- Run `pre-commit run --all-files` before committing
- Test changes with `pytest`
- Ask questions early in the PR process

---

**Version**: 1.1.0
**Last Updated**: 2025-11-28
