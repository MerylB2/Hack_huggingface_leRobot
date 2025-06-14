#!/bin/bash

# Startup script for Print Params Chat App
# This script launches the Gradio web application

echo "🚀 Starting Print Params Chat App..."
echo "📁 Working directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Check if gradio is installed
if ! python -c "import gradio" 2>/dev/null; then
    echo "❌ Gradio not found. Installing..."
    pip install gradio
    if [ $? -eq 0 ]; then
        echo "✅ Gradio installed successfully"
    else
        echo "❌ Failed to install Gradio"
        exit 1
    fi
else
    echo "✅ Gradio is already installed"
fi

# Check if print_params.py exists
if [ ! -f "print_params.py" ]; then
    echo "❌ print_params.py not found in current directory"
    exit 1
else
    echo "✅ Found print_params.py"
fi

# Check if chat_app.py exists
if [ ! -f "chat_app.py" ]; then
    echo "❌ chat_app.py not found in current directory"
    exit 1
else
    echo "✅ Found chat_app.py"
fi

echo ""
echo "🌐 Starting web server..."
echo "📱 The app will be available at: http://localhost:7860"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Launch the application
python chat_app.py
