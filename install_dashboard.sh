#!/bin/bash

# NYC Congestion Pricing Audit Dashboard - Installation Script
# This script sets up a virtual environment and installs all dependencies

echo "🚕 NYC Congestion Pricing Audit Dashboard - Setup"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Virtual environment created!"
echo ""
echo "📦 Installing dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "=================================================="
echo "🎉 Setup Successful!"
echo "=================================================="
echo ""
echo "To run the dashboard:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run Streamlit:"
echo "     streamlit run streamlit_dashboard.py"
echo ""
echo "  3. Open browser to:"
echo "     http://localhost:8501"
echo ""
echo "=================================================="
