# pydeps - Python Module Dependency Visualization

**pydeps** analyzes Python module imports and generates SVG graphs showing dependencies. Perfect for understanding module organization and detecting coupling.

## Overview

pydeps creates three types of dependency visualizations:

1. **High-level Dependencies** (`dependencies.svg`)
   - Simplified view of module relationships
   - Good for overview
   - Fewer connection lines for clarity

2. **Detailed Dependencies** (`dependencies_detailed.svg`)
   - All import relationships shown
   - Shows every `from X import Y`
   - Dense but comprehensive

3. **Clustered Dependencies** (`dependencies_clustered.svg`)
   - Grouped by package
   - Shows inter-package dependencies
   - Good for architecture review

## Installation

```bash
# Install pydeps
pip install pydeps==1.12.8

# Verify installation
pydeps --version
pydeps --help
```

## Quick Start

```bash
# Generate all dependency graphs
bash generate.sh

# View the SVG files
# Open in browser or image viewer:
# - dependencies.svg
# - dependencies_detailed.svg
# - dependencies_clustered.svg
```

## What It Generates

### For EC2-Automator

```
dependencies.svg (High-level)
├── endpoints.py
│   ├─ imports models.py
│   ├─ imports background.py
│   ├─ imports tasks.py
│   └─ imports logging_config.py
│
├── background.py
│   ├─ imports aws/ec2.py
│   ├─ imports aws/ses.py
│   ├─ imports tasks.py
│   └─ imports logging_config.py
│
├── aws/ec2.py
│   ├─ imports config.py
│   └─ imports logging_config.py
│
└── aws/ses.py
    └─ imports logging_config.py
```

### Dependency Patterns

**Linear Dependencies** (good):
```
A → B → C → D
```

**Star Dependencies** (moderate):
```
    A
   /|\
  B C D
```

**Circular Dependencies** (problematic):
```
A ← → B
```

## Advanced Usage

### Customize Depth

```bash
# Show only 1 level deep (max-bacon=1)
pydeps app --max-bacon=1 -o dependencies_shallow.svg

# Show 3 levels (default)
pydeps app --max-bacon=3 -o dependencies_mid.svg

# Show all dependencies (max-bacon=10)
pydeps app --max-bacon=10 -o dependencies_deep.svg
```

### Include Specific Packages

```bash
# Show only external dependencies
pydeps app --external -o dependencies_external.svg

# Show only internal dependencies
pydeps app --no-external -o dependencies_internal.svg
```

### Exclude Certain Modules

```bash
# Exclude test imports
pydeps app --ignore-dirs=tests -o dependencies_no_tests.svg
```

### Highlight Circular Dependencies

```bash
# Show circular dependencies in red
pydeps app --show-cycles -o dependencies_cycles.svg
```

### Format Output

```bash
# PNG instead of SVG (requires Graphviz)
pydeps app --dot -o dependencies.dot
dot -Tpng dependencies.dot -o dependencies.png

# ASCII text
pydeps app --show-deps --print-stats
```

## Interpreting the Output

### Node Types

**Modules**: Boxes representing Python files/packages
```
┌──────────────┐
│  endpoints   │
│     .py      │
└──────────────┘
```

**Packages**: Rounded boxes for directories
```
┌──────────────┐
│    (( aws ))  │
└──────────────┘
```

### Arrow Types

**Single Arrow** → (import direction)
```
A → B  means A imports from B
```

**Bidirectional** ↔ (circular dependency - problem!)
```
A ↔ B  means A and B import each other
```

### Colors

**Blue** - Normal dependencies
**Red** - Circular dependencies (if --show-cycles)
**Gray** - External dependencies (if --external)

## For EC2-Automator

### What It Shows

```
endpoints.py is the API entry point
  ↓
It imports and uses:
  - models.py (validation)
  - tasks.py (task management)
  - background.py (async workers)
  ↓
background.py coordinates provisioning:
  - aws/ec2.py (EC2 management)
  - aws/ses.py (email notifications)
  - tasks.py (status tracking)
  ↓
All modules use:
  - logging_config.py (JSON logging)
  - config.py (constants)
```

### Dependency Quality Analysis

**Good Signs** ✅
- Linear dependency chains
- Minimal circular imports
- Clear separation of concerns
- External dependencies isolated

**Bad Signs** ⚠️
- Circular imports (A → B → A)
- Too many bidirectional arrows
- Tangled web of dependencies
- High coupling between modules

### For EC2-Automator

Current dependency structure is **healthy**:
- endpoints.py is the main entry point
- background.py handles async work
- aws/ package isolated for AWS operations
- logging_config.py used everywhere (expected)
- No circular dependencies

## Comparison with Other Tools

| Feature | pydeps | pyreverse | py2puml | PlantUML |
|---------|--------|-----------|---------|----------|
| Dependency graphs | ✅ | ✅ | ❌ | ❌ |
| Class diagrams | ❌ | ✅ | ✅ | ✅ |
| Circular detection | ✅ | ❌ | ❌ | ❌ |
| SVG output | ✅ | ❌ | ❌ | ✅ |
| Auto-generation | ✅ | ✅ | ✅ | ❌ |

## Workflow Integration

### 1. Regular Architecture Reviews
```bash
# Check dependencies after each milestone
bash uml/pydeps/generate.sh
# Review for circular imports
# Check coupling levels
```

### 2. Refactoring Validation
```bash
# Before refactoring
bash uml/pydeps/generate.sh
cp dependencies.svg dependencies_before.svg

# After refactoring
bash uml/pydeps/generate.sh
# Compare dependencies.svg with dependencies_before.svg
```

### 3. Onboarding
```bash
# Show new developers the module structure
open uml/pydeps/dependencies.svg
# "This is how modules depend on each other"
```

## Troubleshooting

### pydeps not found
```bash
pip install pydeps --upgrade
which pydeps
```

### Empty output
- Check app directory exists and has `__init__.py`
- Verify Python files have proper imports
- Try: `pydeps app --show-deps` for debug output

### SVG rendering issues
- Use modern browser (Chrome, Firefox)
- Try exporting to PNG: `convert dependencies.svg dependencies.png`
- Check Graphviz: `which dot`

### Circular import detection
```bash
# Find circular imports
pydeps app --show-cycles -o cycles.svg
# Then refactor to break cycles
```

## References

- [pydeps GitHub](https://github.com/thebjorn/pydeps)
- [pydeps Documentation](https://github.com/thebjorn/pydeps/wiki)
- [Python Import System](https://docs.python.org/3/reference/import.html)

---

**Tool Type**: Dependency Analyzer
**License**: BSD-3-Clause
**Requires**: Python 3.6+, Graphviz (for SVG)
