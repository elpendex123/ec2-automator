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

# Generate shallow dependency graph (max-bacon=1 - direct imports only)
echo "Generating shallow dependency graph (max-bacon=1)..."
pydeps "$PROJECT_APP_DIR" --max-bacon=1 -o dependencies_shallow.svg || {
    echo "Error: pydeps generation failed for shallow graph"
    exit 1
}
echo "✓ Generated: dependencies_shallow.svg"

# Generate moderate dependency graph (max-bacon=2 - secondary imports)
echo "Generating moderate dependency graph (max-bacon=2)..."
pydeps "$PROJECT_APP_DIR" --max-bacon=2 -o dependencies_moderate.svg || {
    echo "Error: pydeps generation failed for moderate graph"
    exit 1
}
echo "✓ Generated: dependencies_moderate.svg"

# Generate deep dependency graph (max-bacon=3 - full dependency tree)
echo "Generating deep dependency graph (max-bacon=3)..."
pydeps "$PROJECT_APP_DIR" --max-bacon=3 -o dependencies_deep.svg || {
    echo "Error: pydeps generation failed for deep graph"
    exit 1
}
echo "✓ Generated: dependencies_deep.svg"

echo ""
echo "=== pydeps generation complete ==="
echo ""
echo "Generated files:"
ls -lh dependencies*.svg 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "View diagrams with any SVG viewer or web browser:"
echo "  - dependencies_shallow.svg      (Max-bacon=1, direct imports only)"
echo "  - dependencies_moderate.svg     (Max-bacon=2, includes secondary imports)"
echo "  - dependencies_deep.svg         (Max-bacon=3, full dependency tree)"
echo ""
echo "Note: SVG files are interactive in modern browsers"
echo "You can zoom, pan, and hover for details"
echo ""
