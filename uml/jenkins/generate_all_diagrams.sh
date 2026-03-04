#!/bin/bash
# Master script to generate all UML diagrams
# Runs all diagram generation tools and creates a comprehensive report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
UML_DIR="$PROJECT_ROOT/uml"

echo "=================================================="
echo "EC2-Automator: Comprehensive UML Diagram Generation"
echo "=================================================="
echo ""
echo "Timestamp: $(date)"
echo "Project Root: $PROJECT_ROOT"
echo "UML Directory: $UML_DIR"
echo ""

# Counter for tracking results
TOOLS_RUN=0
TOOLS_PASSED=0
TOOLS_FAILED=0

# Function to run a tool and track results
run_tool() {
    local tool_name="$1"
    local tool_dir="$2"
    local script_name="$3"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $tool_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    TOOLS_RUN=$((TOOLS_RUN + 1))

    if [ -d "$tool_dir" ]; then
        cd "$tool_dir"

        if [ -f "$script_name" ]; then
            if bash "$script_name" 2>&1; then
                echo "✓ $tool_name completed successfully"
                TOOLS_PASSED=$((TOOLS_PASSED + 1))
            else
                echo "✗ $tool_name failed"
                TOOLS_FAILED=$((TOOLS_FAILED + 1))
            fi
        else
            echo "✗ Script not found: $script_name"
            TOOLS_FAILED=$((TOOLS_FAILED + 1))
        fi
    else
        echo "✗ Directory not found: $tool_dir"
        TOOLS_FAILED=$((TOOLS_FAILED + 1))
    fi

    echo ""
}

# Generate diagrams using each tool

echo "Phase 1: Auto-Generation Tools"
echo ""

# pyreverse
run_tool "pyreverse (pylint)" "$UML_DIR/pyreverse" "generate.sh"

# py2puml
run_tool "py2puml (Python → PlantUML)" "$UML_DIR/py2puml" "generate.sh"

# pydeps
run_tool "pydeps (Dependency Analysis)" "$UML_DIR/pydeps" "generate.sh"

echo "Phase 2: Manual UML Diagrams"
echo ""

# PlantUML
run_tool "PlantUML (Manual UML)" "$UML_DIR/plantuml" "generate.sh"

echo "Phase 3: Architecture Diagrams"
echo ""

# diagrams (mingrammer)
cd "$UML_DIR/diagrams"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: diagrams (AWS Architecture)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOOLS_RUN=$((TOOLS_RUN + 1))

if python3 generate_architecture.py 2>&1; then
    echo "✓ diagrams completed successfully"
    TOOLS_PASSED=$((TOOLS_PASSED + 1))
else
    echo "✗ diagrams failed"
    TOOLS_FAILED=$((TOOLS_FAILED + 1))
fi
echo ""

echo "=================================================="
echo "Diagram Generation Summary"
echo "=================================================="
echo ""
echo "Tools Run:    $TOOLS_RUN"
echo "Passed:       $TOOLS_PASSED"
echo "Failed:       $TOOLS_FAILED"
echo ""

# List generated files
echo "Generated Files:"
echo ""

for dir in "$UML_DIR"/{pyreverse,plantuml,py2puml,pydeps,diagrams}; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        echo "  $dir_name/"
        find "$dir" \( -name "*.png" -o -name "*.svg" -o -name "*.puml" \) -type f 2>/dev/null | \
            while read -r file; do
                size=$(du -h "$file" | cut -f1)
                filename=$(basename "$file")
                echo "    - $filename ($size)"
            done || true
    fi
done

echo ""

# Count total files
PNG_COUNT=$(find "$UML_DIR" -name "*.png" -type f 2>/dev/null | wc -l)
SVG_COUNT=$(find "$UML_DIR" -name "*.svg" -type f 2>/dev/null | wc -l)
PUML_COUNT=$(find "$UML_DIR" -name "*.puml" -type f 2>/dev/null | wc -l)

echo "Total Counts:"
echo "  PNG files:  $PNG_COUNT"
echo "  SVG files:  $SVG_COUNT"
echo "  PUML files: $PUML_COUNT"
echo ""

# Final status
echo "=================================================="
if [ $TOOLS_FAILED -eq 0 ]; then
    echo "✓ All diagram generation completed successfully!"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Review generated diagrams:"
    echo "     cd $UML_DIR"
    echo "     ls -lh */*.png */*.svg"
    echo ""
    echo "  2. Embed diagrams in documentation:"
    echo "     README.md, docs/architecture/, etc."
    echo ""
    echo "  3. Commit and push:"
    echo "     git add uml/"
    echo "     git commit -m 'Update UML diagrams'"
    echo ""
    exit 0
else
    echo "✗ Some diagram generation failed ($TOOLS_FAILED tools)"
    echo "=================================================="
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check dependencies:"
    echo "     pip install -r requirements-dev.txt"
    echo "     sudo apt-get install plantuml graphviz"
    echo ""
    echo "  2. Run individual tools for details:"
    echo "     cd uml/<tool> && bash generate.sh"
    echo ""
    exit 1
fi
