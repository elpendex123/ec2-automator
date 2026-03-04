# UML Diagram Generation for EC2-Automator

A comprehensive suite of 6 professional UML/diagram generation tools integrated into the EC2-Automator project. Each tool provides unique perspectives on the codebase architecture, dependencies, and workflows.

## Quick Start

### Install All Dependencies

```bash
# Install UML tools
pip install -r requirements-dev.txt

# Install system dependencies (Bodhi Linux)
sudo apt-get install default-jre plantuml graphviz
```

### Generate All Diagrams

```bash
# Run the master generation script
bash uml/jenkins/generate_all_diagrams.sh
```

Or generate diagrams from individual tools:

```bash
cd uml/pyreverse && bash generate.sh
cd uml/plantuml && bash generate.sh
cd uml/py2puml && bash generate.sh
cd uml/pydeps && bash generate.sh
cd uml/diagrams && python generate_architecture.py
```

---

## Tool Comparison Matrix

| Tool | Type | Auto-Gen | Diagram Types | Output Format | Best For | Location |
|------|------|----------|---------------|---------------|----------|----------|
| **pyreverse** | Analyzer | ✅ | Class, Package | PNG, DOT | Quick code analysis | `pyreverse/` |
| **PlantUML** | Manual | ❌ | ALL (7 types) | PNG, SVG | Workflows & architecture | `plantuml/` |
| **py2puml** | Auto-Gen | ✅ | Class | PUML, PNG, SVG | Code-to-UML sync | `py2puml/` |
| **pydeps** | Analyzer | ✅ | Dependency | SVG | Import analysis | `pydeps/` |
| **diagrams** | Code-Gen | ⚠️ | Component, Deploy | PNG | AWS architecture | `diagrams/` |
| **Mermaid** | Manual | ❌ | Multiple | Markdown | GitHub integration | `mermaid/` |

---

## Tool Details & Use Cases

### 1. pyreverse (Part of pylint)
**Best for: Quick class and module overview**

Automatically analyzes Python code to generate UML class and package diagrams.

**Generates:**
- Class diagram showing Pydantic models, inheritance, and relationships
- Package diagram showing module dependencies
- DOT source files for further customization

**Strengths:**
- Zero configuration
- Industry standard (part of pylint ecosystem)
- Quick overview of class hierarchy
- Supports multiple output formats

**Limitations:**
- Only class and package diagrams
- Better for OOP-heavy code (limited Pydantic model relationships)

**Usage:**
```bash
cd uml/pyreverse
bash generate.sh
```

**Output files:**
- `classes_ec2_automator.png` - Pydantic models and JSONFormatter
- `packages_ec2_automator_packages.png` - Module structure
- `classes_ec2_automator_dot.dot` - Editable diagram source

---

### 2. PlantUML
**Best for: Complete architecture documentation**

Professional text-based UML supporting all diagram types. Perfect for documenting workflows, sequences, and deployment architectures.

**Generates:**
- Sequence diagrams (async instance launch flow)
- Activity diagrams (background task processing)
- Component diagrams (module organization)
- Deployment diagrams (AWS infrastructure)
- Class diagrams (Pydantic models)
- State diagrams (task status transitions)
- Use case diagrams (system functionality)

**Strengths:**
- Text-based (version control friendly)
- All UML diagram types supported
- Professional documentation standard
- Exportable to PNG, SVG, ASCII, HTML
- AWS library support for cloud architecture
- C4 model support for system design

**Limitations:**
- Manual creation required
- Requires Java runtime
- Steeper learning curve

**Usage:**
```bash
cd uml/plantuml
bash generate.sh  # Converts all .puml files to PNG/SVG
```

**Output files:**
- `sequence_launch.png` - Async instance launch workflow
- `activity_background.png` - Background task processing
- `component_architecture.png` - Component relationships
- `deployment_aws.png` - AWS deployment topology
- `class_models.png` - Pydantic model hierarchy

Plus `.svg` versions for scalability.

---

### 3. py2puml
**Best for: Auto-generated Python class diagrams**

Automatically converts Python code to PlantUML class diagrams. Keeps diagrams in sync with code changes.

**Generates:**
- Class diagram from Python module structure
- PlantUML source (.puml) file
- PNG and SVG renders

**Strengths:**
- Fully automated from Python code
- Useful for Pydantic models
- PlantUML source can be manually edited
- Low maintenance

**Limitations:**
- Class diagrams only
- Limited customization control
- Best for documenting data models

**Usage:**
```bash
cd uml/py2puml
bash generate.sh
```

**Output files:**
- `app.puml` - Auto-generated PlantUML source
- `app.png` - Class diagram
- `app.svg` - Scalable version

---

### 4. pydeps
**Best for: Dependency and import analysis**

Visualizes module dependencies and import relationships. Excellent for identifying coupling and circular dependencies.

**Generates:**
- High-level module dependency graphs
- Detailed import relationship graphs
- Clustered dependency visualization

**Strengths:**
- Shows import relationships clearly
- Detects circular dependencies
- Professional dependency visualization
- SVG output (scalable and interactive)

**Limitations:**
- Dependency graphs only
- Not suitable for workflow documentation

**Usage:**
```bash
cd uml/pydeps
bash generate.sh
```

**Output files:**
- `dependencies.svg` - High-level module dependencies
- `dependencies_detailed.svg` - All import relationships
- `dependencies_clustered.svg` - Grouped by package

---

### 5. diagrams (mingrammer/diagrams)
**Best for: AWS architecture and deployment diagrams**

Python code generates professional cloud architecture diagrams. Uses AWS, GCP, Azure, and on-premises icons.

**Generates:**
- EC2 Automator architecture diagram
- Instance launch deployment flow diagram

**Strengths:**
- Python code defines architecture (infrastructure as code)
- Professional AWS icon set
- Great for deployment documentation
- Easy to version control architecture changes

**Limitations:**
- Architecture/component diagrams only
- Not suitable for sequence or class diagrams
- Limited customization of layout

**Usage:**
```bash
cd uml/diagrams
python generate_architecture.py
```

**Output files:**
- `ec2_automator_architecture.png` - Overall system architecture
- `deployment_flow.png` - Instance launch workflow

---

### 6. Mermaid
**Best for: GitHub and Markdown documentation**

Diagram syntax embedded directly in Markdown files. Renders automatically in GitHub, GitLab, and modern editors.

**Generates:**
- Class diagrams (embedded in .md)
- Sequence diagrams (embedded in .md)
- Component diagrams (embedded in .md)
- State diagrams (embedded in .md)
- ER diagrams (embedded in .md)

**Strengths:**
- Native Markdown integration
- No external dependencies
- Renders in GitHub without build step
- Easy to embed in documentation
- Great for README.md

**Limitations:**
- Less professional styling than PlantUML
- Limited diagram types
- Browser rendering (not as crisp as PNG)

**Usage:**
Open `uml/mermaid/*.md` files in GitHub or any Markdown viewer.

**Output files:**
- `class_diagram.md` - Pydantic model diagram
- `sequence_diagram.md` - Instance launch sequence
- `component_diagram.md` - Module relationships
- `README.md` - Guide with embedded diagrams

---

## Architecture Overview by Tool

### pyreverse Class Diagram
Shows the actual Python class structure including Pydantic models.

### PlantUML Sequence Diagram
Illustrates the async workflow when a user launches an EC2 instance:
1. User sends POST /launch request
2. FastAPI endpoint creates a task
3. Returns 202 Accepted immediately
4. Background worker provisions EC2 instance
5. EC2 client tags the instance
6. SES sends email notification

### pydeps Dependency Graph
Shows which modules import from which:
- `endpoints.py` depends on `background.py`, `tasks.py`
- `background.py` depends on `aws/ec2.py`, `aws/ses.py`
- All modules use `logging_config.py`

### diagrams Architecture
Shows the deployment topology:
- Docker container running FastAPI
- AWS VPC and EC2 instances
- SES email notifications
- IAM roles for security

---

## Installation Guide (Bodhi Linux)

### System Dependencies

```bash
# Java runtime (for PlantUML)
sudo apt-get install default-jre

# PlantUML
sudo apt-get install plantuml

# Graphviz (for pydeps and diagrams)
sudo apt-get install graphviz
```

### Python Dependencies

```bash
# Install all UML tools
pip install -r requirements-dev.txt

# Or individually:
pip install pylint==3.0.3
pip install py2puml==0.9.0
pip install pydeps==1.12.8
pip install diagrams==0.23.3
pip install plantuml==0.3.0
```

### Verify Installation

```bash
pyreverse --version
plantuml -version
py2puml --help
pydeps --help
python -c "import diagrams; print('diagrams installed')"
```

---

## CI/CD Integration

### Jenkins Pipeline

The project includes a Jenkins pipeline that automatically generates diagrams on code changes.

```bash
# Manual trigger
bash uml/jenkins/generate_all_diagrams.sh

# Configure in Jenkins:
# 1. Add uml/jenkins/Jenkinsfile.diagrams to Jenkins
# 2. Set build trigger to poll SCM every 15 minutes
# 3. Artifacts are archived after generation
```

### Git Pre-Commit Hook (Optional)

```bash
#!/bin/bash
# .git/hooks/pre-commit
bash uml/jenkins/generate_all_diagrams.sh
git add uml/**/*.png uml/**/*.svg
```

---

## Directory Structure

```
uml/
├── README.md                          # This file
├── pyreverse/
│   ├── generate.sh                    # Generate pyreverse diagrams
│   ├── classes_ec2_automator.png
│   ├── packages_ec2_automator_packages.png
│   ├── classes_ec2_automator_dot.dot
│   └── README.md
├── plantuml/
│   ├── sequence_launch.puml           # Async workflow sequence
│   ├── activity_background.puml       # Background task processing
│   ├── component_architecture.puml    # Module organization
│   ├── deployment_aws.puml            # AWS deployment diagram
│   ├── class_models.puml              # Pydantic models
│   ├── generate.sh                    # Convert .puml to PNG/SVG
│   ├── *.png                          # Generated PNG files
│   ├── *.svg                          # Generated SVG files
│   └── README.md
├── py2puml/
│   ├── generate.sh                    # Auto-generate from Python
│   ├── app.puml                       # Generated PlantUML source
│   ├── app.png
│   ├── app.svg
│   └── README.md
├── pydeps/
│   ├── generate.sh                    # Generate dependency graphs
│   ├── dependencies.svg
│   ├── dependencies_detailed.svg
│   ├── dependencies_clustered.svg
│   └── README.md
├── diagrams/
│   ├── generate_architecture.py       # Python script for diagrams
│   ├── ec2_automator_architecture.png
│   ├── deployment_flow.png
│   └── README.md
├── mermaid/
│   ├── README.md                      # With embedded diagrams
│   ├── class_diagram.md
│   ├── sequence_diagram.md
│   ├── component_diagram.md
│   └── (rendered in GitHub)
└── jenkins/
    ├── generate_all_diagrams.sh       # Master generation script
    └── Jenkinsfile.diagrams           # Jenkins pipeline configuration
```

---

## Comparison: Which Tool to Use?

### For Developer Onboarding
- Start with **pyreverse** for class overview
- Then read **pydeps** for dependency understanding
- Finish with **mermaid** sequence diagrams for workflow comprehension

### For API Documentation
- Use **PlantUML** sequence diagrams to show request flow
- Embed in API docs with generated PNG

### For Architecture Reviews
- Use **diagrams** for deployment topology
- Use **PlantUML** component diagram for module organization
- Use **pydeps** for dependency analysis

### For PR Code Review
- Use **Mermaid** for quick visual reference in GitHub
- Use **py2puml** to verify class structure changes

### For System Design
- Use **PlantUML** (all diagram types)
- Use **diagrams** for AWS infrastructure
- Combine multiple views for comprehensive documentation

---

## Troubleshooting

### PlantUML not found
```bash
# Reinstall PlantUML
sudo apt-get remove plantuml
sudo apt-get install plantuml

# Or use Python wrapper
pip install plantuml
```

### Graphviz dependency error (pydeps/diagrams)
```bash
sudo apt-get install graphviz graphviz-dev
```

### Java not installed (PlantUML)
```bash
sudo apt-get install default-jre
```

### Permission denied on generate.sh
```bash
chmod +x uml/*/generate.sh
chmod +x uml/jenkins/generate_all_diagrams.sh
```

---

## Future Enhancements

- [ ] Sphinx integration for HTML documentation
- [ ] Automatic diagram updates on code changes (pre-commit hook)
- [ ] Diagram diffing for PR reviews
- [ ] Interactive HTML diagrams (D3.js)
- [ ] OpenAPI/Swagger diagram auto-generation
- [ ] Database schema diagrams
- [ ] Deployment automation diagrams

---

## References

- [PlantUML Documentation](https://plantuml.com)
- [Mermaid Documentation](https://mermaid.js.org)
- [py2puml GitHub](https://github.com/lucyking/py2puml)
- [pydeps GitHub](https://github.com/thebjorn/pydeps)
- [diagrams GitHub](https://github.com/mingrammer/diagrams)
- [pyreverse Documentation](https://pylint.readthedocs.io)

---

**Generated for EC2-Automator Project**
**Last Updated: 2026-03-03**
