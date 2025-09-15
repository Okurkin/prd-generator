#!/bin/bash

# PRD Generator - Interactive Chat Version
# Quick start script

echo "🚀 Starting AI PRD Generator..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and set your OPENAI_API_KEY"
    exit 1
fi

# Check if port 8501 is already in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8501 is already in use!"
    echo "🧹 Run ./cleanup.sh or ./reset.sh to kill existing processes"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "🚫 Start cancelled."
        exit 0
    fi
fi

# Activate virtual environment and run
source .venv/bin/activate

echo "✅ Virtual environment activated"
echo "🌐 Starting Streamlit application..."
echo "📝 Access the app at: http://localhost:8501"

streamlit run app/app.py
