#!/bin/bash

# quick_setup_dual_db.sh - Quick setup for dual database architecture

set -e

echo "========================================"
echo "Quick Setup: Dual Database Architecture"
echo "========================================"
echo ""

# Check if docker is running
if ! docker ps &> /dev/null; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "[1/5] Pulling Docker images..."
docker-compose pull

echo "[2/5] Building services..."
docker-compose build

echo "[3/5] Starting services..."
docker-compose up -d

echo "[4/5] Waiting for databases to be ready..."
sleep 10

echo "[5/5] Running database initialization..."
chmod +x setup_database.sh
./setup_database.sh

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Services are now running:"
echo "  ✓ PostgreSQL (relational data): localhost:5433"
echo "  ✓ TimescaleDB (time-series data): localhost:5432"
echo "  ✓ FastAPI Backend: http://localhost:8000"
echo "  ✓ Streamlit Frontend: http://localhost:8501"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Frontend: http://localhost:8501"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
