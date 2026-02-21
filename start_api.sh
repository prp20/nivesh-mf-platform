#!/bin/bash
# Start Mutual Funds API

set -e

cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Mutual Funds Analysis API${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found at .venv"
    echo "Please create it first with: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements if needed
echo -e "${BLUE}Checking dependencies...${NC}"
pip install -q -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${BLUE}Starting API server...${NC}"
echo -e "${GREEN}Server will be available at: http://127.0.0.1:8000${NC}"
echo -e "${GREEN}API Documentation: http://127.0.0.1:8000/docs${NC}"
echo -e "${GREEN}Alternative Docs: http://127.0.0.1:8000/redoc${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run uvicorn without reload to avoid file watching permission issues
uvicorn mf_app.app.main:app --host 127.0.0.1 --port 8000 --reload --reload-exclude docker,.git,__pycache__,*.db
