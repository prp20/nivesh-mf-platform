#!/bin/bash

# ============================================================================
# CRUD Test Suite Runner Script
# ============================================================================

set -e  # Exit on error

PROJECT_DIR="/home/prasad/dev_home/mutual_fund_exp/nivesh_platform"
VENV_DIR="$PROJECT_DIR/.venv"

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                 MUTUAL FUNDS PLATFORM - POPULATE DB RUNNER                     ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running from correct directory
if [ ! -f "$PROJECT_DIR/mf_app/data/populate_db.py" ]; then
    echo "❌ Error: test_crud_operations.py not found in $PROJECT_DIR"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if FastAPI server is running
echo -n "  Checking FastAPI server (http://localhost:8000)... "
if timeout 2 curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✓ Running"
else
    echo "✗ Not running"
    echo ""
    echo "⚠️  The FastAPI server is not running!"
    echo "Please start it with: python -m uvicorn mf_app.app.main:app --reload"
    echo ""
    exit 1
fi

# Check if database is accessible
echo -n "  Checking PostgreSQL database... "
if timeout 2 curl -s http://localhost:8000/funds > /dev/null 2>&1; then
    echo "✓ Accessible"
else
    echo "✗ Not accessible"
    echo ""
    echo "⚠️  The database is not accessible!"
    echo "Please ensure PostgreSQL is running with: docker-compose up -d"
    echo ""
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "All prerequisites verified! Starting test suite..."
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Run the test suite
cd "$PROJECT_DIR/mf_app/data"
python populate_db.py

TEST_EXIT_CODE=$?

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Test suite completed successfully!"
else
    echo "❌ Test suite encountered errors (exit code: $TEST_EXIT_CODE)"
fi
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

exit $TEST_EXIT_CODE
