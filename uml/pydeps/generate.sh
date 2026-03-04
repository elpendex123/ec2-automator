#!/bin/bash
# Generate dependency graphs using pydeps
# Shows module imports and dependencies visually

set -e

echo "=== Generating pydeps dependency graphs ==="
echo "Analyzing module imports and dependencies..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/app"

# Check if app directory exists
if [ ! -d "$PROJECT_APP_DIR" ]; then
    echo "Error: Could not find app directory at $PROJECT_APP_DIR"
    exit 1
fi

cd "$SCRIPT_DIR"

# Check if pydeps is installed
if ! command -v pydeps &> /dev/null; then
    echo "Error: pydeps not found"
    echo "Install with: pip install pydeps"
    exit 1
fi

# Generate basic dependency graph (max-bacon=3 for cleaner output)
echo "Generating high-level dependency graph..."
pydeps "$PROJECT_APP_DIR" --max-bacon=3 -o dependencies.svg || {
    echo "Error: pydeps generation failed for basic graph"
    exit 1
}
echo "✓ Generated: dependencies.svg"

# Generate detailed dependency graph (all imports)
echo "Generating detailed dependency graph (all imports)..."
pydeps "$PROJECT_APP_DIR" --max-bacon=10 --show-deps -o dependencies_detailed.svg || {
    echo "Warning: detailed graph generation had issues"
}
echo "✓ Generated: dependencies_detailed.svg"

# Generate clustered dependency graph (grouped by package)
echo "Generating clustered dependency graph..."
pydeps "$PROJECT_APP_DIR" --cluster -o dependencies_clustered.svg || {
    echo "Warning: clustered graph generation had issues"
}
echo "✓ Generated: dependencies_clustered.svg"

echo ""
echo "=== pydeps generation complete ==="
echo ""
echo "Generated files:"
ls -lh dependencies*.svg 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "View diagrams with any SVG viewer or web browser:"
echo "  - dependencies.svg              (High-level dependencies)"
echo "  - dependencies_detailed.svg     (All import relationships)"
echo "  - dependencies_clustered.svg    (Grouped by package)"
echo ""
echo "Note: SVG files are interactive in modern browsers"
echo "You can zoom, pan, and hover for details"
echo ""
