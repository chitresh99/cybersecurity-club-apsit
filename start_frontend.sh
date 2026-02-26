#!/bin/bash

# Frontend startup script for Linux/Mac
# Automatically generates config.js from environment variables and starts the server

set -e

echo "🔒 Starting Cybersecurity Club Frontend..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if .env.frontend exists
if [ ! -f "$SCRIPT_DIR/.env.frontend" ]; then
    echo -e "${YELLOW}⚠${NC}  .env.frontend not found. Creating from example..."
    cp "$SCRIPT_DIR/.env.frontend.example" "$SCRIPT_DIR/.env.frontend"
    echo -e "${GREEN}✓${NC} Created .env.frontend - please update with your backend URL"
    echo ""
fi

# Generate config.js from environment variables
echo -e "${BLUE}[1/2]${NC} Generating js/config.js..."
cd "$SCRIPT_DIR"
python3 generate-config.py

# Start frontend server
echo -e "${BLUE}[2/2]${NC} Starting HTTP Server on port 5500..."
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Frontend is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Frontend:${NC}  http://localhost:5500"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 5500
