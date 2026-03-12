#!/bin/bash
# =============================================================================
# TideWatch MCP Server — One-Click Setup Script (Azure VM)
# =============================================================================

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "========================================"
echo "  🌊 TideWatch MCP Server Setup"
echo "========================================"
echo ""
echo "Directory: $REPO_DIR"

# Check Python
echo ""
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required"
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python version: $PYTHON_VERSION"

# Check Poetry
echo ""
echo "Checking Poetry..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "  Poetry version: $(poetry --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
cd "$REPO_DIR"
poetry install --no-interaction

# Setup .env
if [ ! -f "$REPO_DIR/.env" ]; then
    echo ""
    echo "Creating .env with auto-generated API key..."
    GENERATED_KEY="polly-tidewatch-$(openssl rand -hex 12)"
    cat > "$REPO_DIR/.env" << EOF
# TideWatch MCP Server — Environment Variables
# ==============================================

# API Key for remote HTTP access (auto-generated)
MCP_API_KEY=$GENERATED_KEY

# CopilotX LLM (for narrative polishing)
COPILOTX_API_KEY=your-copilotx-key-here
EOF
    echo "  ✅ API Key generated: $GENERATED_KEY"
    echo "  ⚠️  Please edit .env to set COPILOTX_API_KEY!"
fi

# Create data directory
mkdir -p "$REPO_DIR/data"

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env to configure API keys"
echo "  2. Test locally:"
echo "     poetry run tidewatch --http --port 8889"
echo ""
echo "  3. Setup domain (run as root):"
echo "     sudo ./scripts/setup_domain.sh"
echo ""
echo "  4. Run as systemd service:"
echo "     sudo cp scripts/tidewatch.service /etc/systemd/system/"
echo "     sudo systemctl enable --now tidewatch"
echo ""
