#!/bin/bash

# PRD Generator - Cleanup Script
# This script will clean the database and kill processes on application ports

echo "🧹 PRD Generator Cleanup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default ports used by Streamlit
PORTS=(8501 8502 8503 8504 8505)

# Function to kill only Streamlit processes on specific port
kill_port_processes() {
    local port=$1
    echo -e "${BLUE}🔍 Checking for Streamlit processes on port $port...${NC}"
    
    # Find processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}⚠️  Found processes on port $port: $pids${NC}"
        for pid in $pids; do
            # Get process info
            local process_info=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
            local process_cmd=$(ps -p $pid -o command= 2>/dev/null | head -1)
            
            # Check if it's a Streamlit process
            if [[ "$process_cmd" == *"streamlit"* ]]; then
                echo -e "${YELLOW}   Killing Streamlit PID $pid ($process_info)${NC}"
                kill -9 $pid 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}   ✅ Successfully killed Streamlit PID $pid${NC}"
                else
                    echo -e "${RED}   ❌ Failed to kill Streamlit PID $pid${NC}"
                fi
            else
                echo -e "${BLUE}   ⏭️  Skipping non-Streamlit PID $pid ($process_info)${NC}"
                echo -e "${BLUE}      Command: $(echo $process_cmd | cut -d' ' -f1-3)${NC}"
            fi
        done
    else
        echo -e "${GREEN}✅ No processes found on port $port${NC}"
    fi
}

# Function to clean database files
clean_database() {
    echo -e "\n${BLUE}🗃️  Cleaning database files...${NC}"
    
    # List of database files to clean
    local db_files=(
        "prd_history.db"
        "prd_history.db-shm"
        "prd_history.db-wal"
        "test_prd.db"
        "test_prd.db-shm"
        "test_prd.db-wal"
    )
    
    local cleaned=0
    
    for db_file in "${db_files[@]}"; do
        if [ -f "$db_file" ]; then
            echo -e "${YELLOW}🗑️  Removing $db_file...${NC}"
            rm -f "$db_file"
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}   ✅ Removed $db_file${NC}"
                ((cleaned++))
            else
                echo -e "${RED}   ❌ Failed to remove $db_file${NC}"
            fi
        fi
    done
    
    if [ $cleaned -eq 0 ]; then
        echo -e "${GREEN}✅ No database files found to clean${NC}"
    else
        echo -e "${GREEN}✅ Cleaned $cleaned database file(s)${NC}"
    fi
}

# Function to clean cache and temporary files
clean_cache() {
    echo -e "\n${BLUE}🧹 Cleaning cache and temporary files...${NC}"
    
    # Streamlit cache
    if [ -d ".streamlit" ]; then
        echo -e "${YELLOW}🗑️  Removing .streamlit cache...${NC}"
        rm -rf .streamlit
        echo -e "${GREEN}   ✅ Removed .streamlit cache${NC}"
    fi
    
    # Python cache
    if [ -d "__pycache__" ]; then
        echo -e "${YELLOW}🗑️  Removing __pycache__ directories...${NC}"
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        echo -e "${GREEN}   ✅ Removed __pycache__ directories${NC}"
    fi
    
    # Python bytecode files
    local pyc_files=$(find . -name "*.pyc" 2>/dev/null | wc -l)
    if [ $pyc_files -gt 0 ]; then
        echo -e "${YELLOW}🗑️  Removing .pyc files...${NC}"
        find . -name "*.pyc" -delete 2>/dev/null
        echo -e "${GREEN}   ✅ Removed $pyc_files .pyc files${NC}"
    fi
    
    # Temporary files
    local tmp_files=$(find . -name "*.tmp" -o -name "*.temp" 2>/dev/null | wc -l)
    if [ $tmp_files -gt 0 ]; then
        echo -e "${YELLOW}🗑️  Removing temporary files...${NC}"
        find . -name "*.tmp" -delete 2>/dev/null
        find . -name "*.temp" -delete 2>/dev/null
        echo -e "${GREEN}   ✅ Removed $tmp_files temporary files${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting cleanup process...${NC}"
    
    # Kill Streamlit processes on common Streamlit ports
    echo -e "\n${BLUE}🔫 Killing Streamlit processes on application ports...${NC}"
    for port in "${PORTS[@]}"; do
        kill_port_processes $port
    done
    
    # Also check for any python processes running streamlit
    echo -e "\n${BLUE}🐍 Checking for Streamlit processes...${NC}"
    local streamlit_pids=$(pgrep -f "streamlit" 2>/dev/null)
    if [ -n "$streamlit_pids" ]; then
        echo -e "${YELLOW}⚠️  Found Streamlit processes: $streamlit_pids${NC}"
        for pid in $streamlit_pids; do
            echo -e "${YELLOW}   Killing Streamlit PID $pid${NC}"
            kill -9 $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}   ✅ Successfully killed Streamlit PID $pid${NC}"
            else
                echo -e "${RED}   ❌ Failed to kill Streamlit PID $pid${NC}"
            fi
        done
    else
        echo -e "${GREEN}✅ No Streamlit processes found${NC}"
    fi
    
    # Clean database
    clean_database
    
    # Clean cache and temporary files
    clean_cache
    
    # Final summary
    echo -e "\n${GREEN}🎉 Cleanup completed!${NC}"
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}✅ All processes killed${NC}"
    echo -e "${GREEN}✅ Database files cleaned${NC}"
    echo -e "${GREEN}✅ Cache files removed${NC}"
    echo -e "${BLUE}🚀 You can now start the application fresh!${NC}"
    echo -e "${BLUE}   Run: ./start.sh${NC}"
}

# Check if running from correct directory
if [ ! -f "app/app.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the PRD-Generator root directory${NC}"
    echo -e "${YELLOW}   (The directory containing app/app.py)${NC}"
    exit 1
fi

# Confirm before running
echo -e "${YELLOW}⚠️  This will:${NC}"
echo -e "   - Kill only Streamlit processes on ports: ${PORTS[*]}"
echo -e "   - Remove all database files (prd_history.db, etc.)"
echo -e "   - Clean cache and temporary files"
echo -e "   - Remove all session data and version history"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    main
else
    echo -e "${BLUE}🚫 Cleanup cancelled.${NC}"
    exit 0
fi
