# pyreverse - Automated Python Code Analysis

**pyreverse** is part of the `pylint` package and automatically generates UML diagrams from Python code.

## Overview

pyreverse analyzes your Python codebase and generates:
- **Class Diagrams**: Shows classes, methods, attributes, and relationships
- **Package Diagrams**: Shows module dependencies and package structure
- **DOT Source Files**: Raw diagram definitions for customization

## Installation

```bash
# Install pylint (includes pyreverse)
pip install pylint==3.0.3

# Verify installation
pyreverse --version
```

## Quick Start

```bash
# Generate diagrams
bash generate.sh

# View the generated PNG files
# - classes_diagram.png      (Class relationships)
# - packages_diagram.png     (Module organization)
```

## What It Generates

### classes_diagram.png
Shows all Python classes in the codebase:
- **Pydantic Models**: `LaunchInstanceRequest`, `LaunchInstanceResponse`, `TaskStatus`, etc.
- **Custom Classes**: `JSONFormatter` extending `logging.Formatter`
- **Relationships**: Inheritance arrows show BaseModel hierarchy
- **Attributes**: Shows public/private attributes and types

For EC2-Automator, this displays:
```
BaseModel (from pydantic)
  ├── LaunchInstanceRequest
  ├── LaunchInstanceResponse
  ├── TaskStatus
  ├── TerminateInstanceResponse
  ├── InstanceOption
  └── ErrorResponse

logging.Formatter
  └── JSONFormatter
```

### packages_diagram.png
Shows module structure and import relationships:
```
ec2_automator/
├── main.py (FastAPI app entry)
├── endpoints.py (REST API routes)
├── models.py (Pydantic validation)
├── tasks.py (Task management)
├── background.py (Async workers)
├── logging_config.py (JSON logging)
└── aws/
    ├── ec2.py (EC2 client)
    └── ses.py (Email notifications)
```

Lines show import dependencies.

## Advanced Usage

### Generate Specific Diagram Types

```bash
# Only class diagrams
pyreverse -o png -p myproject app/

# Only package diagrams
pyreverse -o png -k -p myproject_packages app/

# DOT format (for Graphviz)
pyreverse -o dot -p myproject app/
```

### Output Formats

```bash
# PNG (raster)
pyreverse -o png ...

# DOT (Graphviz format - editable)
pyreverse -o dot ...

# PlantUML format
pyreverse -o puml ...

# PS (PostScript)
pyreverse -o ps ...
```

### Filter Specific Modules

```bash
# Generate only for app/aws/ package
pyreverse -o png app/aws/

# Exclude test code
pyreverse -o png --ignore=tests app/
```

## Interpreting the Output

### Class Diagram Symbols

| Symbol | Meaning |
|--------|---------|
| `-` | Private attribute/method |
| `+` | Public attribute/method |
| `#` | Protected attribute/method |
| `^` | Inheritance relationship |
| `→` | Association/dependency |
| `◇` | Composition |
| `◈` | Aggregation |

### Example: EC2-Automator Class Diagram

```
┌──────────────────────────────────────┐
│         BaseModel (pydantic)         │
└──────────────────────────────────────┘
            △
            │
    ┌───────┼───────────────────────────┬─────────────┐
    │       │                           │             │
┌───┴──────┐│┌──────────────────┐┌──────┴──────┐┌─────┴──────┐
│ Instance │││LaunchInstance    ││TaskStatus   ││Terminate  │
│ Option   │││Request           ││             ││Instance   │
└──────────┘││+instance_name: str││+task_id     ││Response   │
           ││+instance_type     ││+status      │└────────────┘
           ││+app_name          ││+instance_id │
           ││+owner             ││+public_ip   │
           │└────────────────────┘│+message     │
           │                      └─────────────┘
           │
     LaunchInstanceResponse
     +task_id: str
     +message: str
```

## Pros and Cons

### Strengths
✅ Zero configuration needed
✅ Industry standard (part of pylint)
✅ Analyzes actual code structure
✅ Multiple output formats
✅ Fast execution
✅ No external dependencies beyond pylint

### Limitations
❌ Only class and package diagrams
❌ Limited customization of output
❌ Better for OOP code (less useful for functional code)
❌ Doesn't show method signatures in detail
❌ No sequence or activity diagrams

## For EC2-Automator

This tool is useful for:
1. **Quick Class Structure Overview** - See all Pydantic models at a glance
2. **Module Organization Understanding** - See how packages relate to each other
3. **Onboarding New Developers** - Provide visual reference for codebase structure
4. **Documentation** - Include diagrams in project README

**Less useful for:**
- Showing async workflows (use PlantUML sequence diagrams)
- Illustrating AWS interactions (use `diagrams` library)
- Documenting state transitions (use activity/state diagrams)

## Troubleshooting

### pyreverse not found
```bash
pip install pylint --upgrade
which pyreverse
```

### Permission denied on generate.sh
```bash
chmod +x generate.sh
```

### Diagrams look empty
- Check that the app directory path is correct
- Ensure Python files contain classes (not just functions)
- Try `pyreverse -h` to debug

### Converting DOT to other formats
```bash
# DOT to PNG (requires Graphviz)
dot -Tpng classes.dot -o classes.png

# DOT to SVG
dot -Tsvg classes.dot -o classes.svg

# DOT to PDF
dot -Tpdf classes.dot -o classes.pdf
```

## Comparison with Other Tools

| Feature | pyreverse | PlantUML | py2puml | pydeps |
|---------|-----------|----------|---------|--------|
| Auto-generation | ✅ | ❌ | ✅ | ✅ |
| Class diagrams | ✅ | ✅ | ✅ | ❌ |
| Package diagrams | ✅ | ❌ | ❌ | ✅ |
| Sequence diagrams | ❌ | ✅ | ❌ | ❌ |
| Manual control | Limited | Extensive | Moderate | Limited |
| Output quality | Good | Excellent | Good | Good |

## Further Reading

- [pylint Documentation](https://pylint.readthedocs.io)
- [pyreverse Guide](https://pylint.readthedocs.io/en/latest/pyreverse.html)
- [PlantUML Comparison](https://plantuml.com)

---

**Tool Type**: Code Analyzer
**License**: GPL-2.0
**Part of**: pylint project
