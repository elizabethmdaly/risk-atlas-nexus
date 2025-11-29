# AI Atlas Nexus - Agent Context Index

This directory contains comprehensive onboarding documentation for future Claude Code agents working on the AI Atlas Nexus project.

## Quick Navigation

### 📚 For Getting Started

**Start here** → [README.md](README.md)

The README provides:
- Complete project overview
- Architecture diagrams
- Setup instructions (with Python 3.11 requirements)
- How to run tests, build docs, and use the library
- Common development tasks with code examples
- Quick reference for imports and methods

### 📋 For Development

**Code guidelines** → [guidelines.md](guidelines.md)

The guidelines cover:
- Code style (Black, isort, PEP 8)
- Type hints and docstrings (Google-style)
- File organization patterns
- Naming conventions (variables, classes, IDs, tags)
- Testing approach (pytest, 54 tests, >80% coverage)
- Key architectural patterns and decisions
- Common gotchas and debugging tips
- Pre-commit hooks and CI/CD

### 🎯 For Understanding Context

**Project context** → [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)

The context document explains:
- What problem the code solves (AI governance fragmentation)
- Who the users are (developers, governance teams, researchers)
- Main entry points (Python API, notebooks, CLI tools)
- Critical code paths with detailed walkthroughs
- External dependencies (LinkML, LLMs, txtai, SSSOM)
- Project metrics and future directions

---

## Documentation Summary

### README.md

**Purpose**: Complete technical reference

**When to use**:
- First time setting up the project
- Need to understand architecture
- Looking for API examples
- Want to add new features

**Key sections**:
1. Project Overview & Purpose
2. Tech Stack (Python 3.11, LinkML, Pydantic, LLMs)
3. Architecture (layered: data → logic → API)
4. Setup Instructions (step-by-step)
5. Running/Building/Testing
6. Common Development Tasks

**Length**: ~800 lines, comprehensive

---

### guidelines.md

**Purpose**: Development best practices

**When to use**:
- Writing new code
- Reviewing pull requests
- Debugging style issues
- Understanding conventions

**Key sections**:
1. Code Style (Black, isort, type hints)
2. File Organization Patterns
3. Naming Conventions
4. Testing Requirements (pytest, 54 tests)
5. Architectural Patterns (Strategy, Abstract Base Classes)
6. Common Gotchas (Python version, parameter names, etc.)
7. Development Workflow

**Length**: ~600 lines, detailed

---

### PROJECT_CONTEXT.md

**Purpose**: Business and technical context

**When to use**:
- Understanding the "why" behind decisions
- Need user/stakeholder context
- Learning code flow
- Understanding external dependencies

**Key sections**:
1. Problem Being Solved (AI governance)
2. Users & Stakeholders (7 types identified)
3. Entry Points (5 ways to use the system)
4. Critical Paths (5 detailed walkthroughs)
5. External APIs (LinkML, LLMs, txtai, SSSOM)
6. Project Metrics & Future Directions

**Length**: ~700 lines, contextual

---

## Quick Reference Card

### Essential Facts

| Aspect | Detail |
|--------|--------|
| **Language** | Python 3.11.x (required!) |
| **License** | Apache 2.0 |
| **Version** | 1.1.0 |
| **Main Class** | `AIAtlasNexus` |
| **Test Suite** | 65 tests, all passing |
| **Code Style** | Black + isort (auto-formatted) |
| **Schema System** | LinkML (YAML → Python) |
| **Data Format** | YAML (knowledge graph) |
| **LLM Support** | Ollama, WML, vLLM, RITS |

### Key Numbers

- **556 risks** across 11 taxonomies
- **254 actions** for risk mitigation
- **17 risk controls** (detectors)
- **26 AI principles** from various orgs
- **11 AI capabilities** across 5 domains (IBM AI Capabilities Framework)
- **8 AI tasks** with capability mappings
- **48+ Python files** (~16K lines of code)
- **25+ YAML data files**
- **100+ cross-taxonomy mappings**
- **26 task→capability mappings**
- **16 capability→intrinsic mappings**

### Critical Commands

```bash
# Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -e ".[ollama]"

# Test
pytest                              # Run all tests
pytest -v                           # Verbose
pytest --cov=ai_atlas_nexus        # With coverage

# Code Quality
pre-commit run --all-files         # Format & lint
black .                            # Format code
isort .                            # Sort imports

# Build
make compile_pydantic_model        # Regenerate datamodel from schema
make regenerate_documentation      # Build docs
make regenerate_graph_output       # Export knowledge graph
make test                          # Run tests
```

### Most Important Files

1. **`src/ai_atlas_nexus/library.py`** - Main API (50+ methods)
2. **`src/ai_atlas_nexus/ai_risk_ontology/schema/ai-risk-ontology.yaml`** - Schema definition
3. **`src/ai_atlas_nexus/ai_risk_ontology/schema/ai_capability.yaml`** - Capabilities taxonomy schema
4. **`src/ai_atlas_nexus/data/knowledge_graph/*.yaml`** - Instance data (25+ files)
5. **`src/ai_atlas_nexus/blocks/ai_atlas_explorer/`** - Generic graph navigation system
6. **`src/ai_atlas_nexus/blocks/inference/`** - LLM integrations
7. **`src/ai_atlas_nexus/blocks/risk_detector/generic.py`** - Risk identification
8. **`tests/ai_atlas_nexus/test_library.py`** - Main test suite (40 tests)
9. **`tests/blocks/ai_atlas_explorer/test_integration.py`** - AtlasExplorer tests (11 tests)

---

## Common Tasks Quick Guide

### 1. Add a New Risk

```yaml
# Edit: src/ai_atlas_nexus/data/knowledge_graph/my_taxonomy_data.yaml
risks:
  - id: my-taxonomy-new-risk
    name: "New Risk Name"
    description: "Detailed description..."
    isDefinedByTaxonomy: my-taxonomy
    tag: new-risk
```

Then:
```python
from ai_atlas_nexus import AIAtlasNexus
ran = AIAtlasNexus()
risk = ran.get_risk(id="my-taxonomy-new-risk")
```

### 2. Test Risk Identification

```python
from ai_atlas_nexus import AIAtlasNexus
from ai_atlas_nexus.blocks.inference import OllamaInferenceEngine

ran = AIAtlasNexus()

engine = OllamaInferenceEngine(
    model_name_or_path="granite3.2:8b",
    credentials={"api_url": "localhost:11434"},
    parameters={"temperature": 0.1, "num_predict": 300}
)

results = ran.identify_risks_from_usecases(
    usecases=["Building a chatbot..."],
    inference_engine=engine,
    taxonomy="ibm-risk-atlas",
    zero_shot_only=True
)

for risk in results[0]:
    print(f"- {risk.name} ({risk.id})")
```

### 3. Modify Schema

```bash
# 1. Edit schema
vim src/ai_atlas_nexus/ai_risk_ontology/schema/ai_risk.yaml

# 2. Regenerate Python datamodel
make compile_pydantic_model

# 3. Run tests
pytest

# 4. Commit changes
git add src/ai_atlas_nexus/ai_risk_ontology/
git commit -m "schema: update risk definition

Signed-off-by: Your Name <email@example.com>"
```

### 4. Add New Taxonomy

See [README.md - Common Development Tasks #1](README.md#1-adding-a-new-taxonomy) for detailed steps.

Quick summary:
1. Create conversion script in `ai_risk_ontology/util/`
2. Generate YAML data file in `data/knowledge_graph/`
3. (Optional) Add mappings in `data/mappings/`
4. Verify loading with `AIAtlasNexus().get_all_risks()`

### 5. Debug Common Issues

| Issue | Solution | Reference |
|-------|----------|-----------|
| Python version error | Use Python 3.11.x | [guidelines.md - Gotcha #1](guidelines.md#1-python-version-constraint) |
| `model_id` not recognized | Use `model_name_or_path` | [guidelines.md - Gotcha #2](guidelines.md#2-inferenceengine-parameter-names) |
| `get_risk()` returns None | Use keyword arg: `id=...` | [guidelines.md - Gotcha #3](guidelines.md#3-method-signatures-use-keyword-arguments) |
| Pre-commit failing | Run `pre-commit run --all-files` | [guidelines.md - Gotcha #10](guidelines.md#10-pre-commit-hooks-can-block-commits) |

---

## Learning Path

### Level 1: Beginner (Day 1)

1. Read [README.md - Project Overview](README.md#project-overview)
2. Follow [README.md - Setup Instructions](README.md#setup-instructions)
3. Run quick start example from [README.md](README.md#quick-start-in-python)
4. Explore [PROJECT_CONTEXT.md - Main Entry Points](PROJECT_CONTEXT.md#main-entry-points)

**Goal**: Understand what the project does and get it running

### Level 2: Intermediate (Week 1)

1. Read [PROJECT_CONTEXT.md - Critical Paths](PROJECT_CONTEXT.md#critical-paths-through-the-code)
2. Study [README.md - Architecture Overview](README.md#architecture-overview)
3. Review [guidelines.md - File Organization](guidelines.md#file-organization-patterns)
4. Run example notebooks: `docs/examples/notebooks/AI_Atlas_Nexus_Quickstart.ipynb`
5. Run tests: `pytest -v`

**Goal**: Understand code structure and data flow

### Level 3: Advanced (Month 1)

1. Study [guidelines.md - Architectural Patterns](guidelines.md#key-architectural-decisions-and-patterns)
2. Read [PROJECT_CONTEXT.md - External Dependencies](PROJECT_CONTEXT.md#external-dependencies-and-apis-used)
3. Add a simple risk or mapping (following [README.md - Common Tasks](README.md#1-adding-a-new-taxonomy))
4. Write a test for your change
5. Submit a PR following [guidelines.md - Development Workflow](guidelines.md#development-workflow-best-practices)

**Goal**: Contribute meaningfully to the project

---

## Testing & Validation Checklist

Before considering yourself onboarded:

- [ ] Clone repository successfully
- [ ] Create Python 3.11 virtual environment
- [ ] Install dependencies with `pip install -e ".[ollama]"`
- [ ] Run `pytest` - all 65 tests pass
- [ ] Import library: `from ai_atlas_nexus import AIAtlasNexus`
- [ ] Initialize: `ran = AIAtlasNexus()`
- [ ] Get risks: `risks = ran.get_all_risks()` (returns 556 risks)
- [ ] Get capabilities: `from ai_atlas_nexus.blocks.ai_atlas_explorer import AtlasExplorer; explorer = AtlasExplorer(ran._ontology); caps = explorer.get_all_capabilities()` (returns 11 capabilities)
- [ ] Run pre-commit hooks: `pre-commit run --all-files`
- [ ] Build docs: `JUPYTER_PLATFORM_DIRS=1 mkdocs serve`
- [ ] Understand at least 3 critical code paths from PROJECT_CONTEXT.md
- [ ] Know where to find: schema files, data files, tests, docs

---

## External Resources

### Official Documentation

- **Project Site**: https://github.com/IBM/ai-atlas-nexus
- **Full Docs**: https://ibm.github.io/ai-atlas-nexus/
- **Demo**: https://huggingface.co/spaces/ibm/risk-atlas-nexus
- **Demo Projects**: https://github.com/IBM/ai-atlas-nexus-demos

### Papers & Research

- [AI Risk Atlas Paper](https://arxiv.org/abs/2503.05780)
- [Usage Governance Advisor](https://arxiv.org/abs/2412.01957)

### Technology Documentation

- **LinkML**: https://linkml.io/linkml/
- **Pydantic**: https://docs.pydantic.dev/
- **SSSOM**: https://mapping-commons.github.io/sssom/
- **MkDocs**: https://www.mkdocs.org/
- **pytest**: https://docs.pytest.org/

### Community

- **Issues**: https://github.com/IBM/ai-atlas-nexus/issues
- **Discussions**: GitHub Discussions
- **Contributing**: See CONTRIBUTING.md in repo root

---

## Document Maintenance

### Updating This Documentation

When making significant changes to the codebase:

1. **Update README.md** if:
   - Architecture changes
   - New dependencies added
   - Setup process changes
   - New common tasks emerge

2. **Update guidelines.md** if:
   - Code style conventions change
   - New patterns adopted
   - New gotchas discovered
   - Testing approach changes

3. **Update PROJECT_CONTEXT.md** if:
   - Problem statement evolves
   - New user types identified
   - Critical paths change
   - External dependencies updated

4. **Update INDEX.md** (this file) if:
   - New documents added
   - Structure changes
   - Quick reference needs updating

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-28 | Initial agent context documentation created |
| 1.1 | 2025-11-28 | Updated for v1.1.0: Added capabilities taxonomy, AtlasExplorer, 65 tests |

---

## Support & Questions

### For New Agents

If something is unclear in this documentation:

1. Check if answer is in one of the three main docs
2. Search the codebase for examples
3. Look at tests for usage patterns
4. Check GitHub issues for similar questions

### For Maintainers

These docs are living documents. Please update them when:
- Making architectural changes
- Adding new features
- Discovering new patterns
- Learning common mistakes

**Goal**: Every future agent should find these docs sufficient to get started without human intervention.

---

## Quick Start Checklist

Print this and check off as you go:

```
Day 1: Setup
[ ] Read README.md overview
[ ] Clone repository
[ ] Set up Python 3.11 venv
[ ] Install dependencies
[ ] Run tests (should pass 54/54)
[ ] Run quick start example

Day 2-3: Exploration
[ ] Read PROJECT_CONTEXT.md
[ ] Understand the problem being solved
[ ] Know the 5 main entry points
[ ] Walk through 1-2 critical paths in code
[ ] Run Jupyter notebooks

Week 1: Contributing
[ ] Read guidelines.md
[ ] Understand code style requirements
[ ] Know naming conventions
[ ] Run pre-commit hooks
[ ] Add a simple risk (practice)
[ ] Write a test
[ ] Build documentation locally

Week 2+: Advanced
[ ] Understand all critical paths
[ ] Know all architectural patterns
[ ] Contribute a real feature
[ ] Review someone else's PR
[ ] Help another contributor
```

---

**Created**: 2025-11-28
**Updated**: 2025-11-28
**For**: AI Atlas Nexus v1.1.0
**By**: Claude Code Agent
**Purpose**: Comprehensive onboarding for future agents

---

*Navigate: [README](README.md) | [Guidelines](guidelines.md) | [Context](PROJECT_CONTEXT.md)*
