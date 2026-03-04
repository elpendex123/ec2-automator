#!/bin/bash
# Generate PNG and SVG files from PlantUML diagram sources
# Requires: plantuml and Java runtime

set -e

echo "=== Generating PlantUML diagrams ==="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if plantuml is installed
if ! command -v plantuml &> /dev/null; then
    echo "Error: plantuml not found"
    echo "Install with: sudo apt-get install plantuml"
    exit 1
fi

# Check for PUML files
PUML_FILES=$(ls *.puml 2>/dev/null || echo "")
if [ -z "$PUML_FILES" ]; then
    echo "Error: No .puml files found in $(pwd)"
    exit 1
fi

echo "Found PlantUML files:"
ls -lh *.puml
echo ""

# Generate PNG and SVG from each PUML file
for puml_file in *.puml; do
    echo "Processing: $puml_file"

    # Get filename without extension
    filename="${puml_file%.puml}"

    # Generate PNG
    echo "  → Generating PNG..."
    plantuml -tpng "$puml_file" || {
        echo "  Error: PNG generation failed for $puml_file"
        exit 1
    }

    # Generate SVG
    echo "  → Generating SVG..."
    plantuml -tsvg "$puml_file" || {
        echo "  Error: SVG generation failed for $puml_file"
        exit 1
    }

    echo "  ✓ Complete: ${filename}.png and ${filename}.svg"
    echo ""
done

echo "=== PlantUML generation complete ==="
echo ""
echo "Generated files:"
ls -lh *.png *.svg 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "View diagrams:"
echo "  - PNG files (raster, embedded in docs)"
echo "  - SVG files (vector, responsive scaling)"
echo ""
