#!/bin/bash
# Generate UML diagrams using pyreverse (part of pylint)
# This script generates class and package diagrams from the Python codebase

set -e

echo "=== Generating pyreverse diagrams ==="
echo "This tool analyzes Python code and generates class/package diagrams"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/app"

# Check if app directory exists
if [ ! -d "$PROJECT_APP_DIR" ]; then
    echo "Error: Could not find app directory at $PROJECT_APP_DIR"
    exit 1
fi

cd "$SCRIPT_DIR"

# Generate class diagram (PNG format)
echo "Generating class diagram..."
pyreverse -o png -p ec2_automator "$PROJECT_APP_DIR"/ || {
    echo "Error: pyreverse class diagram generation failed"
    exit 1
}

# Generate package diagram (PNG format, shows module structure)
echo "Generating package diagram..."
pyreverse -o png -p ec2_automator_packages -k "$PROJECT_APP_DIR"/ || {
    echo "Error: pyreverse package diagram generation failed"
    exit 1
}

# Generate DOT format for advanced customization
echo "Generating DOT source files..."
pyreverse -o dot -p ec2_automator_dot "$PROJECT_APP_DIR"/ || {
    echo "Error: pyreverse DOT generation failed"
    exit 1
}

# Rename files to be more descriptive
mv -f "classes_ec2_automator.png" "classes_diagram.png" 2>/dev/null || true
mv -f "packages_ec2_automator_packages.png" "packages_diagram.png" 2>/dev/null || true
mv -f "classes_ec2_automator_dot.dot" "classes_source.dot" 2>/dev/null || true

echo ""
echo "=== pyreverse generation complete ==="
echo ""
echo "Generated files:"
echo "  - classes_diagram.png       (Class diagram with Pydantic models and relationships)"
echo "  - packages_diagram.png      (Module/package structure diagram)"
echo "  - classes_source.dot        (DOT source format - editable)"
echo ""
echo "View the PNG files with any image viewer:"
echo "  - For class overview: classes_diagram.png"
echo "  - For module organization: packages_diagram.png"
