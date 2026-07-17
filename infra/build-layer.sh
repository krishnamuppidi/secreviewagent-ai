#!/bin/bash
# Build Lambda layer with Python dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Lambda layer..."

# Create temp directory
rm -rf layer_build
mkdir -p layer_build/python

# Install dependencies
pip install anthropic httpx boto3 -t layer_build/python --quiet

# Remove unnecessary files to reduce size
find layer_build -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find layer_build -type f -name "*.pyc" -delete 2>/dev/null || true
find layer_build -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true

# Create zip
cd layer_build
zip -r ../layer.zip python -q

cd ..
rm -rf layer_build

SIZE=$(du -h layer.zip | cut -f1)
echo "✓ Created layer.zip ($SIZE)"
