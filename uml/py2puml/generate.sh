#!/bin/bash
# Generate PlantUML class diagrams from Python code using py2puml
# Automatically converts Python module to PlantUML class diagram

set -e

echo "=== Generating py2puml diagrams ==="
echo "Auto-generating PlantUML from Python code..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/app"

# Check if app directory exists
if [ ! -d "$PROJECT_APP_DIR" ]; then
    echo "Error: Could not find app directory at $PROJECT_APP_DIR"
    exit 1
fi

cd "$SCRIPT_DIR"

# Check if py2puml is installed
if ! command -v py2puml &> /dev/null; then
    echo "Error: py2puml not found"
    echo "Install with: pip install py2puml"
    exit 1
fi

# Generate PlantUML from Python code
echo "Generating PlantUML from Python module: app"
cd "$PROJECT_APP_DIR" || exit 1
py2puml . app > "$SCRIPT_DIR/app.puml" || {
    echo "Error: py2puml generation failed"
    cd "$SCRIPT_DIR"
    exit 1
}
cd "$SCRIPT_DIR"

echo "✓ Generated: app.puml (PlantUML source)"

# Check if plantuml is installed for PNG generation
if command -v plantuml &> /dev/null; then
    echo "Generating PNG from PlantUML..."
    plantuml -tpng app.puml || {
        echo "Warning: PNG generation failed, but .puml file was created"
    }
    echo "✓ Generated: app.png"

    echo "Generating SVG from PlantUML..."
    plantuml -tsvg app.puml || {
        echo "Warning: SVG generation failed, but .puml file was created"
    }
    echo "✓ Generated: app.svg"
else
    echo "Note: plantuml not found. Skipping PNG/SVG generation."
    echo "PlantUML source file (.puml) was created successfully."
    echo "Install plantuml to generate PNG/SVG: sudo apt-get install plantuml"
fi

echo ""
echo "=== py2puml generation complete ==="
echo ""
echo "Generated files:"
ls -lh app.* 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "The .puml file contains auto-generated class diagram"
echo "from the Python code. You can:"
echo "  1. View app.png/app.svg with any image viewer"
echo "  2. Edit app.puml manually for customization"
echo "  3. Convert to other formats with plantuml"
echo ""
