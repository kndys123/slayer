#!/bin/bash
# Setup script for SLAYER Enterprise

echo "🚀 SLAYER Enterprise Setup"
echo "=========================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ Pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Run tests
echo ""
echo "Running tests..."
pytest tests/ -v --tb=short
echo ""

# Show stats
echo ""
echo "==========================="
echo "✅ Setup Complete!"
echo "==========================="
echo ""
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Try CLI: python slayer_enterprise_cli.py --help"
echo "3. Run example: python examples/basic_usage.py"
echo "4. Read docs: cat QUICKSTART.md"
echo ""
echo "🎯 SLAYER Enterprise v3.0 is ready!"
