#!/bin/bash

# diagnose.sh - Diagnostic script for system health checks

echo "========================================"
echo "System Diagnostics Report"
echo "========================================"
echo ""

echo "1. Python Version:"
python3 --version 2>&1 || echo "   ✗ Python not found"
echo ""

echo "2. Docker Status:"
if command -v docker &> /dev/null; then
    docker --version
    docker ps --format "table {{.Names}}\t{{.Status}}" 2>&1 | head -10
else
    echo "   ✗ Docker not found"
fi
echo ""

echo "3. Database Connectivity:"
echo "   PostgreSQL (5433):"
nc -zv localhost 5433 2>&1 | grep -q "succeeded" && echo "     ✓ Port open" || echo "     ✗ Port closed"

echo "   TimescaleDB (5432):"
nc -zv localhost 5432 2>&1 | grep -q "succeeded" && echo "     ✓ Port open" || echo "     ✗ Port closed"
echo ""

echo "4. API Endpoints:"
echo "   Backend (8000):"
if curl -s http://localhost:8000/health &> /dev/null; then
    echo "     ✓ Backend responding"
else
    echo "     ✗ Backend not responding"
fi

echo "   Frontend (8501):"
if curl -s http://localhost:8501 &> /dev/null; then
    echo "     ✓ Frontend responding"
else
    echo "     ✗ Frontend not responding"
fi
echo ""

echo "5. Required Python Packages:"
python3 << 'EOF'
packages = ['fastapi', 'streamlit', 'sqlalchemy', 'pandas', 'numpy', 'psycopg']
import importlib
for pkg in packages:
    try:
        importlib.import_module(pkg)
        print(f"     ✓ {pkg}")
    except ImportError:
        print(f"     ✗ {pkg} (not installed)")
EOF
echo ""

echo "6. Git Status:"
if [ -d ".git" ]; then
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    echo "   ✓ Git repository initialized"
    echo "   Current branch: $branch"
    commits=$(git rev-list --count HEAD 2>/dev/null)
    echo "   Total commits: $commits"
else
    echo "   ✗ Not a git repository"
fi
echo ""

echo "7. Directory Structure:"
echo "   backend/: $([ -d 'backend' ] && echo '✓' || echo '✗')"
echo "   frontend/: $([ -d 'frontend' ] && echo '✓' || echo '✗')"
echo "   analytics/: $([ -d 'analytics' ] && echo '✓' || echo '✗')"
echo "   scripts/: $([ -d 'scripts' ] && echo '✓' || echo '✗')"
echo "   docs/: $([ -d 'docs' ] && echo '✓' || echo '✗')"
echo ""

echo "========================================"
echo "End of Diagnostics"
echo "========================================"
