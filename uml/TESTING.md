# UML Diagram Generation - Testing Guide

Complete guide for testing all diagram generation tools on your system.

## Prerequisites

Before testing, ensure all dependencies are installed:

```bash
# Install Python dependencies
pip install -r requirements-dev.txt

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    default-jre \
    plantuml \
    graphviz \
    graphviz-dev
```

## Dependency Verification Checklist

Run these commands to verify each tool is properly installed:

```bash
# Python tools
echo "=== Python Tools ==="
python3 --version                    # Should show 3.10+
pip install --list | grep pylint    # pyreverse (part of pylint)
pip install --list | grep py2puml   # py2puml
pip install --list | grep pydeps    # pydeps
pip install --list | grep diagrams  # diagrams
pip install --list | grep plantuml  # plantuml

# System tools
echo "=== System Tools ==="
java -version                        # Java runtime for PlantUML
plantuml -version                    # PlantUML version
which dot                            # Graphviz
dot -V                               # Graphviz version
```

**Expected Output**:
```
Java(TM) Runtime Environment (build X.X.X)
PlantUML version X.XXXX
/usr/bin/dot                         # Should exist
dot - graphviz version X.XX
```

## Testing Procedures

### Test 1: pyreverse (Auto-generated class diagrams)

**Difficulty**: Easy
**Time**: < 5 seconds
**Expected Output**: PNG and DOT files

```bash
cd uml/pyreverse
bash generate.sh
```

**Expected Output**:
```
=== Generating pyreverse diagrams ===
Generating class diagram...
Generating package diagram...
Generating DOT source files...
✓ pyreverse generation complete

Generated files:
  - classes_diagram.png (...)
  - packages_diagram.png (...)
  - classes_source.dot (...)
```

**Verification**:
```bash
ls -lh uml/pyreverse/
# Should show:
# - classes_diagram.png (> 5KB)
# - packages_diagram.png (> 5KB)
# - classes_source.dot (> 2KB)
```

**Troubleshooting**:
```bash
# If pyreverse not found:
pip install pylint --upgrade
which pyreverse

# If diagram is empty/white:
# Check that app/ directory has Python files
ls -la ../app/
# Try with verbose output:
pyreverse -v ../app/
```

### Test 2: PlantUML (Manual UML diagrams)

**Difficulty**: Medium
**Time**: 10-15 seconds
**Expected Output**: PNG and SVG files

```bash
cd uml/plantuml
bash generate.sh
```

**Expected Output**:
```
=== Generating PlantUML diagrams ===
Found PlantUML files:
  sequence_launch.puml
  activity_background.puml
  component_architecture.puml
  deployment_aws.puml
  class_models.puml

Processing: sequence_launch.puml
  → Generating PNG...
  → Generating SVG...
  ✓ Complete: sequence_launch.png and sequence_launch.svg

(... more diagrams ...)

=== PlantUML generation complete ===

Generated files:
  - sequence_launch.png (...)
  - activity_background.png (...)
  (... more files ...)
```

**Verification**:
```bash
ls -lh uml/plantuml/
# Should show 10+ files:
# - 5 .puml source files
# - 5 .png files
# - 5 .svg files
```

**Troubleshooting**:
```bash
# If plantuml not found:
sudo apt-get install plantuml

# If Java errors:
sudo apt-get install default-jre
java -version

# Test individual file:
plantuml -tpng uml/plantuml/sequence_launch.puml

# If output is blank image:
# Check .puml syntax with:
plantuml -syntax error uml/plantuml/sequence_launch.puml
```

### Test 3: py2puml (Auto-generated PlantUML from Python)

**Difficulty**: Easy
**Time**: 5-10 seconds
**Expected Output**: PUML, PNG, SVG files

```bash
cd uml/py2puml
bash generate.sh
```

**Expected Output**:
```
=== Generating py2puml diagrams ===
Auto-generating PlantUML from Python code...

Generating PlantUML from Python module: app
✓ Generated: app.puml (PlantUML source)
Generating PNG from PlantUML...
✓ Generated: app.png
Generating SVG from PlantUML...
✓ Generated: app.svg

=== py2puml generation complete ===

Generated files:
  - app.puml (...)
  - app.png (...)
  - app.svg (...)
```

**Verification**:
```bash
ls -lh uml/py2puml/
# Should show:
# - app.puml (> 1KB)
# - app.png (> 10KB)
# - app.svg (> 5KB)

# Check PUML syntax:
head -20 uml/py2puml/app.puml
```

**Troubleshooting**:
```bash
# If py2puml not found:
pip install py2puml --upgrade

# If import errors:
python3 -c "import py2puml; print('OK')"

# Manual generation:
py2puml ../app ec2_automator > app_test.puml

# If PNG generation fails:
plantuml -tpng app.puml
```

### Test 4: pydeps (Dependency analysis)

**Difficulty**: Easy
**Time**: 5-10 seconds
**Expected Output**: SVG files

```bash
cd uml/pydeps
bash generate.sh
```

**Expected Output**:
```
=== Generating pydeps dependency graphs ===
Analyzing module imports and dependencies...

Generating shallow dependency graph (max-bacon=1)...
✓ Generated: dependencies_shallow.svg
Generating moderate dependency graph (max-bacon=2)...
✓ Generated: dependencies_moderate.svg
Generating deep dependency graph (max-bacon=3)...
✓ Generated: dependencies_deep.svg

=== pydeps generation complete ===

Generated files:
  - dependencies_shallow.svg (...)
  - dependencies_moderate.svg (...)
  - dependencies_deep.svg (...)
```

**Verification**:
```bash
ls -lh uml/pydeps/
# Should show 3 SVG files (each > 10KB)

# Check SVG is valid XML:
file uml/pydeps/dependencies_deep.svg
# Should show: SVG Scalable Vector Graphics
```

**Troubleshooting**:
```bash
# If pydeps not found:
pip install pydeps --upgrade

# If Graphviz error:
sudo apt-get install graphviz graphviz-dev
which dot

# Manual generation:
pydeps ../app --max-bacon=3 -o test_deps.svg

# If output is empty:
pydeps ../app --show-deps  # Check what it finds
```

### Test 5: diagrams (AWS architecture)

**Difficulty**: Medium
**Time**: 10-15 seconds
**Expected Output**: PNG files

```bash
cd uml/diagrams
python3 generate_architecture.py
```

**Expected Output**:
```
==================================================
EC2-Automator: Diagram Generation
==================================================

Generating EC2 Automator architecture diagram...
✓ Generated: ec2_automator_architecture.png
Generating instance launch deployment flow diagram...
✓ Generated: deployment_flow.png
Generating free tier resource topology...
✓ Generated: free_tier_topology.png

==================================================
✓ All diagrams generated successfully!
==================================================

Generated files:
  - ec2_automator_architecture.png (...)
  - deployment_flow.png (...)
  - free_tier_topology.png (...)
```

**Verification**:
```bash
ls -lh uml/diagrams/
# Should show 3+ PNG files (each > 20KB)

file uml/diagrams/*.png
# Should show: PNG image data
```

**Troubleshooting**:
```bash
# If diagrams not found:
pip install diagrams --upgrade

# If Graphviz error:
sudo apt-get install graphviz graphviz-dev

# Test import:
python3 -c "from diagrams import Diagram; print('OK')"

# If PNG is blank/small:
# Check Graphviz: dot -V
# Try manual generation:
python3 -c "
from diagrams import Diagram
from diagrams.aws.compute import EC2

with Diagram('Test', show=False):
    EC2('Server')
"
```

### Test 6: Mermaid (Markdown diagrams)

**Difficulty**: None (no generation needed)
**Time**: Instant
**Note**: Mermaid is rendered automatically by GitHub

```bash
# No script to run
# View diagrams in GitHub or mermaid.live:
cat uml/mermaid/class_diagram.md
cat uml/mermaid/sequence_diagram.md
cat uml/mermaid/component_diagram.md
```

**Verification**:
```bash
# Check files exist and contain mermaid code:
grep -c "^​```mermaid" uml/mermaid/*.md
# Should show 1+ matches per file

# Validate syntax with mermaid.live:
# 1. Go to https://mermaid.live
# 2. Copy content from class_diagram.md
# 3. Check that diagram renders without errors
```

### Test 7: Master Generation Script

**Difficulty**: Medium
**Time**: 30-60 seconds (all tools combined)
**Expected Output**: Summary report

```bash
bash uml/jenkins/generate_all_diagrams.sh
```

**Expected Output**:
```
==================================================
EC2-Automator: Comprehensive UML Diagram Generation
==================================================

Timestamp: (...)
Project Root: (...)
UML Directory: (...)

Phase 1: Auto-Generation Tools
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running: pyreverse (pylint)
... (output) ...
✓ pyreverse completed successfully

Running: py2puml (Python → PlantUML)
... (output) ...
✓ py2puml completed successfully

Running: pydeps (Dependency Analysis)
... (output) ...
✓ pydeps completed successfully

Phase 2: Manual UML Diagrams
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running: PlantUML (Manual UML)
... (output) ...
✓ PlantUML completed successfully

Phase 3: Architecture Diagrams
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running: diagrams (AWS Architecture)
... (output) ...
✓ diagrams completed successfully

==================================================
Diagram Generation Summary
==================================================

Tools Run:    6
Passed:       6
Failed:       0

Generated Files:
  pyreverse/
    - classes_diagram.png (...)
    - packages_diagram.png (...)
    - classes_source.dot (...)

  plantuml/
    - sequence_launch.png (...)
    - activity_background.png (...)
    (... more files ...)

  py2puml/
    - app.puml (...)
    - app.png (...)
    - app.svg (...)

  pydeps/
    - dependencies_shallow.svg (...)
    - dependencies_moderate.svg (...)
    - dependencies_deep.svg (...)

  diagrams/
    - ec2_automator_architecture.png (...)
    - deployment_flow.png (...)
    - free_tier_topology.png (...)

Total Counts:
  PNG files:  15
  SVG files:  8
  PUML files: 5

==================================================
✓ All diagram generation completed successfully!
==================================================

Next steps:
  1. Review generated diagrams:
     cd uml
     ls -lh */*.png */*.svg

  2. Embed diagrams in documentation:
     README.md, docs/architecture/, etc.

  3. Commit and push:
     git add uml/
     git commit -m 'Update UML diagrams'
```

**Verification**:
```bash
# Check total file count
find uml -type f \( -name "*.png" -o -name "*.svg" -o -name "*.puml" \) | wc -l
# Should be 25+ files

# Check file sizes
find uml -type f -name "*.png" -exec du -h {} \; | awk '{print $1}' | sort -h | uniq -c
# Should have variety of sizes (small, medium, large)

# Check for errors
bash uml/jenkins/generate_all_diagrams.sh 2>&1 | grep -i "error"
# Should show NO errors (or only warnings)
```

## Complete Test Checklist

```bash
# Run all tests in sequence
echo "Testing EC2-Automator UML Diagrams"
echo "=================================="
echo ""

echo "1. pyreverse..."
cd uml/pyreverse && bash generate.sh && cd ../.. && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "2. PlantUML..."
cd uml/plantuml && bash generate.sh && cd ../.. && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "3. py2puml..."
cd uml/py2puml && bash generate.sh && cd ../.. && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "4. pydeps..."
cd uml/pydeps && bash generate.sh && cd ../.. && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "5. diagrams..."
cd uml/diagrams && python3 generate_architecture.py && cd ../.. && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "6. Mermaid (verification only)..."
test -f uml/mermaid/class_diagram.md && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "=================================="
echo "Summary:"
find uml -type f \( -name "*.png" -o -name "*.svg" \) | wc -l
echo "diagram files generated"
```

## Performance Benchmarks

Expected execution times on modern hardware:

| Tool | Time | Notes |
|------|------|-------|
| pyreverse | 2-3s | Fast analyzer |
| PlantUML | 5-8s | Renders 5 diagrams |
| py2puml | 3-5s | With PlantUML rendering |
| pydeps | 2-4s | Graphviz rendering |
| diagrams | 4-6s | 3 AWS architecture diagrams |
| **Total** | **20-30s** | All tools combined |

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'diagrams'"

**Solution**:
```bash
pip install diagrams --upgrade
# Verify:
python3 -c "import diagrams; print('OK')"
```

### Issue: "plantuml: command not found"

**Solution**:
```bash
sudo apt-get install plantuml
# Verify:
plantuml -version
```

### Issue: "No Java runtime found"

**Solution**:
```bash
sudo apt-get install default-jre
# Verify:
java -version
```

### Issue: "dot: command not found"

**Solution**:
```bash
sudo apt-get install graphviz graphviz-dev
# Verify:
which dot
dot -V
```

### Issue: "py2puml not found"

**Solution**:
```bash
pip install py2puml==0.9.0
# Verify:
py2puml --help
```

### Issue: Diagrams render as blank/white images

**Solution**:
1. Check that app/ directory exists and has Python files
2. Verify PlantUML/Graphviz are properly installed
3. Try generating individual files for debugging
4. Check file sizes (should be > 5KB typically)

## Next Steps After Testing

1. **Review all diagrams**:
   ```bash
   cd uml
   # View each PNG/SVG in image viewer or browser
   ```

2. **Commit to git**:
   ```bash
   git add uml/
   git commit -m "Add comprehensive UML diagram generation"
   git push origin master
   ```

3. **Integrate with documentation**:
   - Embed diagrams in README.md
   - Add architecture documentation
   - Link from relevant sections

4. **Setup Jenkins CI/CD**:
   - Create pipeline job
   - Configure triggers
   - Test automatic generation

5. **Monitor and maintain**:
   - Re-run on major changes
   - Update diagrams when architecture changes
   - Keep tools updated

---

**Last Updated**: 2026-03-03
