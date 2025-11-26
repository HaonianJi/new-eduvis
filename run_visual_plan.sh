#!/bin/bash
# Quick runner for visual plan pipeline
# Reads configuration from .env file

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file
if [ -f "${SCRIPT_DIR}/.env" ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
else
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create a .env file from the template:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then edit .env with your Azure OpenAI credentials."
    exit 1
fi

# Check required environment variables
if [ -z "${AZURE_ENDPOINT}" ] && [ -z "${AZURE_OPENAI_ENDPOINT}" ]; then
    echo "❌ Error: AZURE_ENDPOINT not set in .env file"
    exit 1
fi

if [ -z "${AZURE_API_KEY}" ] && [ -z "${AZURE_OPENAI_API_KEY}" ]; then
    echo "❌ Error: AZURE_API_KEY not set in .env file"
    exit 1
fi

# Check if MinerU is installed
if [ ! -d "${SCRIPT_DIR}/MinerU/venv" ]; then
    echo "❌ Error: MinerU not installed!"
    echo ""
    echo "Please run the setup script first:"
    echo "  ./setup_mineru.sh"
    exit 1
fi

echo "Activating MinerU environment..."
source "${SCRIPT_DIR}/MinerU/venv/bin/activate"

echo "Running visual plan pipeline..."
python "${SCRIPT_DIR}/project/pdf_to_flowchart_v2.py" "$@"

echo ""
echo "✅ Pipeline completed!"
