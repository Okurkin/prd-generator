#!/bin/bash

# Generate project documentation summary

echo "📚 PRD Generator - Project Summary"
echo "=================================="

# Basic project info
echo "🏗️  Project Structure:"
echo "   📁 $(pwd | xargs basename)"
echo "   📅 Last modified: $(date)"
echo "   🐍 Python version: $(python3 --version)"
echo ""

# File counts
echo "📊 Project Statistics:"
echo "   📄 Python files: $(find . -name "*.py" | wc -l | tr -d ' ')"
echo "   📋 Config files: $(find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" | wc -l | tr -d ' ')"
echo "   📜 Script files: $(find . -name "*.sh" | wc -l | tr -d ' ')"
echo "   📖 Doc files: $(find . -name "*.md" | wc -l | tr -d ' ')"
echo "   📦 Total files: $(find . -type f | wc -l | tr -d ' ')"
echo ""

# Dependencies
echo "🔧 Dependencies:"
if [ -f "requirements.txt" ]; then
    echo "   📋 Requirements: $(cat requirements.txt | grep -v '^#' | grep -v '^$' | wc -l | tr -d ' ') packages"
    echo "   📦 Main packages:"
    cat requirements.txt | grep -v '^#' | grep -v '^$' | head -5 | sed 's/^/      /'
else
    echo "   ❌ No requirements.txt found"
fi
echo ""

# Scripts
echo "🛠️  Available Scripts:"
for script in *.sh; do
    if [ -f "$script" ]; then
        echo "   🚀 ./$script"
        # Get first comment line as description
        desc=$(head -5 "$script" | grep '^#' | grep -v '#!/' | head -1 | sed 's/^# *//')
        if [ -n "$desc" ]; then
            echo "      $desc"
        fi
    fi
done
echo ""

# Configuration
echo "⚙️  Configuration:"
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    if grep -q "OPENAI_API_KEY.*your_openai_api_key_here" .env 2>/dev/null; then
        echo "   ⚠️  API key not configured"
    else
        echo "   ✅ API key configured"
    fi
else
    echo "   ❌ No .env file"
fi

if [ -d ".venv" ]; then
    echo "   ✅ Virtual environment exists"
else
    echo "   ❌ No virtual environment"
fi
echo ""

# Database status
echo "🗃️  Database Status:"
if [ -f "prd_history.db" ]; then
    db_size=$(ls -lh prd_history.db | awk '{print $5}')
    echo "   📊 Database exists ($db_size)"
    
    # Check if we can read tables (requires sqlite3)
    if command -v sqlite3 &> /dev/null; then
        sessions=$(sqlite3 prd_history.db "SELECT COUNT(*) FROM sessions;" 2>/dev/null || echo "unknown")
        versions=$(sqlite3 prd_history.db "SELECT COUNT(*) FROM versions;" 2>/dev/null || echo "unknown")
        echo "   📁 Sessions: $sessions"
        echo "   📄 Versions: $versions"
    fi
else
    echo "   📭 No database file"
fi
echo ""

# Port status
echo "🌐 Port Status:"
for port in 8501 8502 8503; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   🔴 Port $port: OCCUPIED"
    else
        echo "   🟢 Port $port: FREE"
    fi
done
echo ""

# Quick start
echo "🚀 Quick Start:"
echo "   1. Configure API key: cp .env.example .env && edit .env"
echo "   2. Start application: ./start.sh"
echo "   3. Access app: http://localhost:8501"
echo ""
echo "🧹 Maintenance:"
echo "   - Quick reset: ./reset.sh"
echo "   - Full cleanup: ./cleanup.sh"
echo "   - This summary: ./info.sh"
echo ""

echo "=================================="
echo "✅ Summary complete!"
