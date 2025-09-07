#!/bin/bash

# Setup script for GLM Chat CLI
# This script creates a virtual environment and installs dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-glm"

echo "🔧 Setting up GLM Chat CLI..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "Make sure python3-venv is installed: sudo apt install python3-venv"
        exit 1
    fi
fi

echo "📚 Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip > /dev/null 2>&1
"$VENV_DIR/bin/pip" install zai-sdk pyperclip prompt_toolkit colorama

if [ $? -eq 0 ]; then
    echo "✅ Setup complete!"
    echo ""
    echo "To run GLM Chat CLI, use one of these methods:"
    echo ""
    echo "1. Direct execution:"
    echo "   $SCRIPT_DIR/glm-chat-launcher"
    echo ""
    echo "2. Add to PATH (run once):"
    echo "   echo 'alias glm-chat=\"$SCRIPT_DIR/glm-chat-launcher\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo "   Then just type: glm-chat"
    echo ""
    echo "Don't forget to set your API key:"
    echo "   export GLM_API_KEY='your-api-key'"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi