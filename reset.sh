#!/bin/bash

# Quick cleanup script - No confirmation required
# Usage: ./reset.sh

echo "🔄 Quick Reset..."

# Kill only Streamlit processes on common ports
for port in 8501 8502 8503; do
    # Check if there are processes on the port
    pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        for pid in $pids; do
            # Check if the process is Streamlit
            process_cmd=$(ps -p $pid -o command= 2>/dev/null | head -1)
            if [[ "$process_cmd" == *"streamlit"* ]]; then
                echo "🔪 Killing Streamlit process on port $port (PID: $pid)"
                kill -9 $pid 2>/dev/null
            else
                echo "⏭️  Skipping non-Streamlit process on port $port (PID: $pid): $(echo $process_cmd | cut -d' ' -f1)"
            fi
        done
    fi
done

# Kill all streamlit processes (as backup)
streamlit_pids=$(pgrep -f streamlit 2>/dev/null)
if [ -n "$streamlit_pids" ]; then
    echo "🔪 Killing remaining Streamlit processes: $streamlit_pids"
    pkill -f streamlit 2>/dev/null
fi


# Clean cache
rm -rf .streamlit __pycache__ 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "✅ Reset complete! Run ./start.sh to restart."
