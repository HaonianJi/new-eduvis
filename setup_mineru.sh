#!/bin/bash
# MinerU One-Click Deployment Script
# Supports: macOS, Linux (Ubuntu/Debian)

set -e  # Exit on error

echo "========================================"
echo "  MinerU Installation Script"
echo "========================================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    PLATFORM="macOS";;
    Linux*)     PLATFORM="Linux";;
    *)          PLATFORM="UNKNOWN";;
esac

echo "Detected Platform: ${PLATFORM}"
echo ""

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is required but not found."
    echo "Please install Git first:"
    if [ "${PLATFORM}" = "macOS" ]; then
        echo "  xcode-select --install"
    else
        echo "  sudo apt-get install git"
    fi
    exit 1
fi

# Check Python version
PYTHON_CMD=""
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python3"
else
    echo "❌ Error: Python 3.10+ is required but not found."
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

echo "Python version: ${PYTHON_VERSION}"
echo "Python command: ${PYTHON_CMD}"

# Parse version
PYTHON_MAJOR=$(echo "${PYTHON_VERSION}" | cut -d. -f1)
PYTHON_MINOR=$(echo "${PYTHON_VERSION}" | cut -d. -f2)

if [ "${PYTHON_MAJOR}" -lt 3 ] || ([ "${PYTHON_MAJOR}" -eq 3 ] && [ "${PYTHON_MINOR}" -lt 10 ]); then
    echo "❌ Error: Python 3.10 or higher is required."
    echo "Current version: ${PYTHON_VERSION}"
    exit 1
fi

echo ""
echo "Step 1/6: Cloning MinerU repository..."
if [ -d "MinerU" ]; then
    echo "⚠️  MinerU directory already exists."
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Updating MinerU repository..."
        cd MinerU
        git pull
        cd ..
    else
        echo "Skipping clone, using existing directory."
    fi
else
    echo "Cloning from GitHub..."
    git clone https://github.com/opendatalab/MinerU.git
    echo "✅ Repository cloned"
fi

cd MinerU

echo ""
echo "Step 2/6: Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    ${PYTHON_CMD} -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "Step 3/6: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 4/6: Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Step 5/6: Installing MinerU..."
echo "This may take 5-10 minutes depending on your network..."

# Install magic-pdf with full dependencies
pip install magic-pdf[full]==0.7.1b1 --extra-index-url https://wheels.myhloli.com

echo ""
echo "Step 6/6: Downloading models..."
echo "Downloading pipeline model (recommended for 8GB RAM)..."
mineru-models-download --model_type pipeline

echo ""
echo "========================================"
echo "  ✅ MinerU Installation Complete!"
echo "========================================"
echo ""
echo "📁 MinerU installed at: $(pwd)"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "1. Activate the environment:"
echo "   cd MinerU && source venv/bin/activate"
echo ""
echo "2. Convert PDF to Markdown:"
echo "   mineru -p your_paper.pdf -o ./output"
echo ""
echo "3. Deactivate when done:"
echo "   deactivate"
echo ""
echo "📖 For more options, run:"
echo "   mineru --help"
echo ""

if [ "${PLATFORM}" = "macOS" ]; then
    echo "💡 macOS Tips:"
    echo "   • For better performance on Apple Silicon:"
    echo "     pip install magic-pdf[full-cpu-mlx]"
    echo "   • Check official docs: https://github.com/opendatalab/MinerU"
    echo ""
fi

echo "📚 Documentation:"
echo "   • GitHub: https://github.com/opendatalab/MinerU"
echo "   • Local docs: ./MinerU/README.md"
echo ""
echo "========================================"
