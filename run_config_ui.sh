#!/bin/bash
# WS2812 Configuration UI Launcher

echo "🚀 Starting WS2812 Matrix Configuration Interface..."
echo ""

# Check if we're in the scripts directory
if [ ! -f "pixi.toml" ]; then
    echo "❌ Error: Please run this script from the 'scripts' directory"
    exit 1
fi

# Check if pixi is available
if ! command -v pixi &> /dev/null; then
    echo "❌ Error: pixi is not installed. Please install pixi first:"
    echo "   curl -fsSL https://pixi.sh/install.sh | bash"
    exit 1
fi

echo "📦 Installing dependencies..."
pixi install

echo ""
echo "🌐 Starting Streamlit server..."
echo "   Open your browser to: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

pixi run streamlit run ws2812_config_ui.py